import uuid
import typing
import logging
import construct
from msband.sugar import bites, byte_bites
from msband.static.command import Command, GetPcbId
from msband.static.status import Status, StatusPacket
from msband.static.constants import BandConstants, ENVOY, pcb_id_to_type


if typing.TYPE_CHECKING:
    import socket
    import asyncio
    import bleak.backends.client


APP_ID = uuid.UUID(hex="12bb15c4-1c72-4db5-8fef-f53b6818c50b")


class ProtocolInterface:
    __slots__ = "acquire_vars", "band_type"

    def __init__(self):
        self.acquire_vars = None
        self.band_type = None

    @property
    def constants(self) -> BandConstants:
        if self.band_type is None:
            self.band_type = pcb_id_to_type(self.command(GetPcbId))
        return BandConstants.by_type[self.band_type]

    def acquire(self, **kwargs) -> None:
        self.acquire_vars = kwargs
        self.band_type = None
        try:
            del self.acquire_vars["kwargs"]
        except KeyError:
            pass

    def reacquire(self) -> None:
        if self.acquire_vars is None:
            raise ValueError("Must acquire() at least once before reacquire()")
        return self.acquire(**self.acquire_vars)

    def reset(self) -> None:
        return

    def send(self, data: bytes, raw: bool) -> int:
        raise NotImplementedError

    def receive(self, length: int) -> bytes:
        read_data = b""

        while len(read_data) != length:
            read_data += self.read(length - len(read_data))

        return read_data

    def read(self, length: int) -> bytes:
        raise NotImplementedError

    def communicate(
        self, data: bytes, response_length: int, transfer: bytes = None
    ) -> typing.Tuple[bytes, Status]:

        self.send(data, raw=False)
        logging.debug(f"Sent bytes: {data}")

        if transfer is not None:
            transferred = 0
            transfer_length = len(transfer)
            packet_size: typing.Optional[int] = None
            while transferred < transfer_length:
                if packet_size is None:
                    packet_size = self.send(b"" + transfer[transferred:], raw=True)
                    transferred += packet_size
                    logging.debug(f"Transferred {packet_size}")
                else:
                    last_send_size = self.send(
                        b"" + transfer[transferred : transferred + packet_size], raw=True
                    )
                    transferred += last_send_size
                    logging.debug(f"Transferred {last_send_size}")

        response_data = self.receive(response_length) if response_length else ""
        status_data = self.receive(6)

        try:
            return response_data, StatusPacket.parse(status_data).Status
        except construct.ConstError:
            logging.warning(f"Response: {response_data!r}")
            logging.warning(f"Status: {status_data!r}")
            raise

    def command(self, command: typing.Union[Command, str], **kwargs) -> typing.Any:

        if not isinstance(command, Command):
            command = Command.get(command)

        # Communication
        result_bytes, status = self.communicate(*command.build_command_packet(**kwargs))

        response_prototype = kwargs.get("Response") or command.Response

        # Result
        if response_prototype is None:
            return result_bytes

        else:
            if response_prototype is construct.Pass:
                return status

            else:
                if status.value[1] != 0:
                    return result_bytes, status
                return response_prototype.parse(result_bytes)


class MockInterface(ProtocolInterface):
    __slots__ = "status"

    def __init__(self, status=Status.Success):
        super().__init__()
        self.status: Status = status

    def acquire(self, id: str = None, **kwargs) -> None:
        ProtocolInterface.acquire(**vars())  # ugly
        return

    def send(self, data: bytes, raw=False) -> int:
        logging.info(f"Sending {data!r}")
        return len(data)

    def read(self, length: int) -> bytes:
        return b"\0" * length

    def communicate(
        self, data: bytes, response_length: int, transfer: bytes = None
    ) -> typing.Tuple[bytes, Status]:
        self.send(data)
        return self.read(response_length), self.status


BLUETOOTH_PORT = 4


class BluetoothInterface(ProtocolInterface):
    __slots__ = "socket"

    def __init__(self, id=None, port=BLUETOOTH_PORT):
        super().__init__()
        self.socket: typing.Optional["socket.socket"] = None
        if id is not None:
            self.acquire(id, port)

    def acquire(self, id: str, port: int = BLUETOOTH_PORT, **kwargs) -> None:
        ProtocolInterface.acquire(**vars())  # ugly
        import socket

        self.socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.socket.settimeout(5.0)
        self.socket.connect((id, port))

    def send(self, data: bytes, raw=False) -> int:
        if raw:
            return self.socket.send(data)
        return self.socket.send(bytes(bytearray([len(data)])) + data)

    def read(self, length: int) -> bytes:
        return self.socket.recv(length)


class BLEv2Interface(ProtocolInterface):
    __slots__ = (
        "client",
        "lock_buffer",
        "w_buffer",
        "max_aligned_buffer",
        "max_aligned",
        "send_control_buffer",
        "recv_buffer",
        "recv_control_buffer",
        "error_buffer",
        "status_buffer",
    )

    def __init__(self, id=None):
        super().__init__()
        self.client: typing.Optional["bleak.backends.client.BaseBleakClient"] = None
        if id is not None:
            self.acquire(id)

    async def acquire(self, id: str, **kwargs) -> None:
        ProtocolInterface.acquire(**vars())  # ugly
        import asyncio
        from bleak import BleakClient
        from msband.protocol.zippy import (
            buffer_notification_closure,
            buffer_join_fragments_closure,
            ZIPPY_LOCK,
            ZIPPY_ERROR,
            ZIPPY_MAX_ALIGNED,
            ZIPPY_W_BUFFER,
            ZIPPY_R_CONTROL,
            ZIPPY_R1,
            ZIPPY_R2,
            ZIPPY_W_CONTROL,
            ZIPPY_W1,
            ZIPPY_W2,
        )

        self.status_buffer: asyncio.Queue[bytearray] = asyncio.Queue()

        self.client = BleakClient(id)
        await self.client.connect(timeout=5.0)

        self.lock_buffer: asyncio.Queue[bytearray] = asyncio.Queue()
        await self.client.start_notify(ZIPPY_LOCK, buffer_notification_closure(self.lock_buffer))

        self.w_buffer: asyncio.Queue[bytearray] = asyncio.Queue()
        await self.client.start_notify(ZIPPY_W_BUFFER, buffer_notification_closure(self.w_buffer))

        self.max_aligned_buffer: asyncio.Queue[bytearray] = asyncio.Queue()
        await self.client.start_notify(
            ZIPPY_MAX_ALIGNED, buffer_notification_closure(self.max_aligned_buffer)
        )

        self.recv_buffer: asyncio.PriorityQueue[
            typing.Tuple[int, bytearray]
        ] = asyncio.PriorityQueue()
        await self.client.start_notify(ZIPPY_R1, buffer_join_fragments_closure(self.recv_buffer))
        await self.client.start_notify(ZIPPY_R2, buffer_join_fragments_closure(self.recv_buffer))

        self.send_control_buffer: asyncio.Queue[bytearray] = asyncio.Queue()
        await self.client.start_notify(
            ZIPPY_R_CONTROL, buffer_notification_closure(self.send_control_buffer)
        )

        self.recv_control_buffer: asyncio.Queue[bytearray] = asyncio.Queue()
        await self.client.start_notify(
            ZIPPY_W_CONTROL, buffer_notification_closure(self.recv_control_buffer)
        )

        self.error_buffer: asyncio.Queue[bytearray] = asyncio.Queue()
        await self.client.start_notify(ZIPPY_ERROR, buffer_notification_closure(self.error_buffer))

        self.band_type = pcb_id_to_type(await self.command(GetPcbId))

    async def reacquire(self) -> None:
        if self.acquire_vars is None:
            raise ValueError("Must acquire() at least once before reacquire()")
        return await self.acquire(**self.acquire_vars)

    async def reset(self) -> None:
        for attribute in dir(self):
            if attribute.endswith("_buffer"):
                buffer: asyncio.Queue[bytearray] = getattr(self, attribute)
                while not buffer.empty():
                    buffer.get_nowait()

    async def lock(self, lock: bool):
        from msband.protocol.zippy import ZIPPY_LOCK, ZippyLockPacket, ZippyLockPacketStruct

        lock_response = ZippyLockPacket(AppID=uuid.UUID(int=0), Lock=False)
        while lock_response.AppID != APP_ID:
            await self.client.write_gatt_char(
                ZIPPY_LOCK,
                ZippyLockPacketStruct.build(ZippyLockPacket(AppID=APP_ID, Lock=lock)),
                response=True,
            )
            lock_response = ZippyLockPacketStruct.parse(await self.lock_buffer.get())

            if not lock and not lock_response.AppID.int:
                break

    async def send(self, data: bytes, raw=False) -> int:
        from msband.protocol.zippy import (
            ZippyControlPacketStruct,
            ZippyControlPacket,
            ZIPPY_R_CONTROL,
        )

        sent_length = 0

        for fragment_id, data_subbytes in enumerate(byte_bites(data, self.max_aligned)):
            await self.write(fragment_id=fragment_id, data=data_subbytes)

            write_supplement = ZippyControlPacketStruct.build(
                (ZippyControlPacket(Length=len(data_subbytes) + 1))
            )

            await self.client.write_gatt_char(ZIPPY_R_CONTROL, write_supplement, response=False)

            response = await self.send_control_buffer.get()
            if response != bytearray([1]):
                raise RuntimeError

        return sent_length

    async def write(self, fragment_id, data):
        from msband.protocol.zippy import ZIPPY_W1

        logging.debug(f"Writing {bytearray([fragment_id, len(data)]) + data}")

        return await self.client.write_gatt_char(
            ZIPPY_W1, bytearray([fragment_id, len(data)]) + data, response=True
        )

    async def receive(self, length: int) -> bytes:
        from msband.protocol.zippy import ZippyControlPacketStruct, ZIPPY_W_CONTROL

        read_data = bytearray()

        read_supplement = ZippyControlPacketStruct.parse(await self.recv_control_buffer.get())
        logging.debug(f"{read_supplement=}")

        current_fragment = 0
        while len(read_data) != length:
            current_fragment, new_data = await self.read(
                length - len(read_data), current_fragment=current_fragment
            )
            if new_data is not None:
                read_data.extend(new_data)

        if read_supplement.Length in {
            len(read_data),
            len(read_data) + 6,
        }:
            await self.client.write_gatt_char(ZIPPY_W_CONTROL, construct.Flag.build(True))
        else:
            logging.warning(f"Sending receipt failure, {len(read_data)=}")
            await self.client.write_gatt_char(ZIPPY_W_CONTROL, construct.Flag.build(False))

        return b"" + read_data

    async def read(self, length: int, current_fragment: int = 0) -> typing.Tuple[int, bytes]:

        fragment_id, read_bytes = await self.recv_buffer.get()
        if fragment_id != current_fragment:
            logging.debug(f"{current_fragment=} != {fragment_id}")
            await self.recv_buffer.put((fragment_id, read_bytes))
            return current_fragment, b""

        excess = len(read_bytes) - length

        if excess == 6:
            await self.status_buffer.put(read_bytes[length:])
            return fragment_id, read_bytes[:length]
        elif not excess:
            return fragment_id, read_bytes
        elif excess < 0:
            return fragment_id + 1, read_bytes
        else:
            raise ValueError((length, excess, read_bytes))

    async def communicate(
        self, data: bytes, response_length: int, transfer: bytes = None
    ) -> typing.Tuple[bytes, Status]:
        from msband.protocol.zippy import ZIPPY_MAX_ALIGNED

        if transfer is not None:
            raise NotImplementedError

        await self.lock(True)

        self.max_aligned = construct.Int16ul.parse(
            await self.client.read_gatt_char(ZIPPY_MAX_ALIGNED)
        )
        logging.debug(f"Max aligned: {self.max_aligned}")

        await self.send(data, raw=False)

        # if transfer is not None:
        #     transferred = 0
        #     transfer_length = len(transfer)
        #     packet_size: typing.Optional[int] = None
        #     while transferred < transfer_length:
        #         if packet_size is None:
        #             packet_size = self.send(b"" + transfer[transferred:], raw=True)
        #             transferred += packet_size
        #             logging.debug(f"Transferred {packet_size}")
        #         else:
        #             last_send_size = self.send(
        #                 b"" + transfer[transferred : transferred + packet_size], raw=True
        #             )
        #             transferred += last_send_size
        #             logging.debug(f"Transferred {last_send_size}")

        response_data = await self.receive(response_length) if response_length else ""
        if self.status_buffer.empty():
            status_data = await self.receive(6)
        else:
            status_data = await self.status_buffer.get()

        try:
            return response_data, StatusPacket.parse(status_data).Status
        except construct.ConstError:
            logging.warning(f"Response: {response_data!r}")
            logging.warning(f"Status: {status_data!r}")
            raise
        finally:
            await self.lock(False)

    async def command(self, command: typing.Union[Command, str], **kwargs) -> typing.Any:

        if not isinstance(command, Command):
            command = Command.get(command)

        # Communication
        result_bytes, status = await self.communicate(*command.build_command_packet(**kwargs))

        response_prototype = kwargs.get("Response") or command.Response

        # Result
        if response_prototype is None:
            return result_bytes

        else:
            if response_prototype is construct.Pass:
                return status

            else:
                if status.value[1] != 0:
                    return result_bytes, status
                return response_prototype.parse(result_bytes)


class USBDeviceNotFound(Exception):
    ...


class USBInterface(ProtocolInterface):
    __slots__ = "bulk_in", "bulk_out", "mtu"

    def __init__(
        self,
        id: typing.Optional[int] = None,
        vid: int = ENVOY.UsbVendorId,
        pid: int = ENVOY.UsbProductId,
        **kwargs,
    ):
        super().__init__()
        self.bulk_in = None
        self.bulk_out = None
        self.mtu = None
        if id is not None:
            self.acquire(id=id, vid=vid, pid=pid, **kwargs)

    def acquire(
        self,
        id: typing.Optional[int] = None,
        vid: int = ENVOY.UsbVendorId,
        pid: int = ENVOY.UsbProductId,
        **kwargs,
    ):
        ProtocolInterface.acquire(**vars())  # ugly
        import usb.util

        # REV = 0x0001
        filter_kwargs = dict(idVendor=vid, idProduct=pid)
        if id:
            filter_kwargs["iSerialNumber"] = id

        band: usb.core.Device = usb.core.find(**filter_kwargs)

        if band is None:
            raise USBDeviceNotFound(f"No Band device found with variables {self.acquire_vars}")

        (configuration,) = band
        configuration.set()

        (interface,) = configuration

        self.bulk_in, self.bulk_out = interface
        self.mtu = self.bulk_out.wMaxPacketSize

    def reset(self):
        self.bulk_in.clear_halt()
        self.bulk_out.clear_halt()

    def send(self, data: bytes, raw: bool = True) -> int:
        written = 0

        for data_slice in bites(data, self.mtu):
            written += self.bulk_out.write(b"" + bytearray(data_slice))

        return written

    def read(self, length: int) -> bytes:
        return self.bulk_in.read(length)
