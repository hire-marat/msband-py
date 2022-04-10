import typing
import logging
import construct
from msband.static import BandType
from msband.static.command import Command
from msband.static.constants import BandConstants
from msband.static.status import Status, StatusPacket


MAX_TRANSFER = 64


class ProtocolInterface:
    __slots__ = "acquire_vars", "band_type"

    def __init__(self):
        self.acquire_vars = None
        self.band_type = None

    @property
    def constants(self) -> BandConstants:
        if self.band_type is None:
            api_version = self.command(Command.get("CoreModuleGetApiVersion"))
            self.band_type = BandType.Envoy if api_version > 30 else BandType.Cargo
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
            logging.warning(response_data)
            logging.warning(status_data)
            raise

    def command(self, command: typing.Union[Command, str], **kwargs) -> typing.Any:

        if not isinstance(command, Command):
            command = Command.get(command)

        # Communication
        result_bytes, status = self.communicate(*command.build_command_packet(**kwargs))

        response_prototype = kwargs.get("Response") or command.Response

        # Result
        if response_prototype is not None:
            if response_prototype is construct.Pass:
                return status
            else:
                if status.value[1] != 0:
                    return result_bytes, status
                return response_prototype.parse(result_bytes)
        else:
            return result_bytes


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


class BluetoothInterface(ProtocolInterface):
    __slots__ = "socket"

    def __init__(self, id=None, port=4):
        super().__init__()
        self.socket: typing.Optional["socket.socket"] = None
        if id is not None:
            self.acquire(id, port)

    def acquire(self, id: str, port: int = 4, **kwargs) -> None:
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


class USBInterface(ProtocolInterface):
    __slots__ = "bulk_in", "bulk_out"

    def __init__(self, id: str = None, vid: int = 0x045E, pid: int = 0x02D6):
        super().__init__()
        self.bulk_in = None
        self.bulk_out = None
        if id is not None:
            self.acquire(id=id, vid=vid, pid=pid)

    def acquire(self, id: str = None, vid: int = 0x045E, pid: int = 0x02D6, **kwargs):
        ProtocolInterface.acquire(**vars())  # ugly
        import usb.util

        # REV = 0x0001
        filter_kwargs = dict(idVendor=vid, idProduct=pid)
        if id:
            filter_kwargs["iSerialNumber"] = id

        band: usb.core.Device = usb.core.find(**filter_kwargs)

        (configuration,) = band
        configuration.set()

        (interface,) = configuration

        self.bulk_in, self.bulk_out = interface

    def reset(self):
        self.bulk_in.clear_halt()
        self.bulk_out.clear_halt()

    def send(self, data: bytes, raw: bool = True) -> int:
        return self.bulk_out.write(data)

    def read(self, length: int) -> bytes:
        return self.bulk_in.read(length)
