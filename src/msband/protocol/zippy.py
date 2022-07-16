import uuid
import asyncio
import logging
import dataclasses
from msband.static import GUIDAdapter
from bleak.uuids import register_uuids
from msband.sugar import IntEnumAdapter, EnumBase, csfield
from construct_typed import DataclassMixin, DataclassStruct
from construct import Bytes, Int32ul, Const, Int8ul, Int16ul, Flag

ZIPPY_SERVICE = uuid.UUID(hex="a502ca98-2ba5-413c-a4e0-13804e47b38f")

# TX
ZIPPY_R1 = uuid.UUID(hex="0534594a-a8e7-4b1a-a6b1-cd5243059a55")  # notify
ZIPPY_R2 = uuid.UUID(hex="0434594a-a8e7-4b1a-a6b1-cd5243059a54")  # notify
ZIPPY_R_CONTROL = uuid.UUID(hex="af04c4b2-892b-43be-b69c-5d13f2195391")  # write, notify
ZIPPY_R_BUFFER = uuid.UUID(hex="8004c4b2-892b-43be-b69c-5d13f2195380")  # write

# RX
ZIPPY_W1 = uuid.UUID(hex="0734594a-a8e7-4b1a-a6b1-cd5243059a57")  # write
ZIPPY_W2 = uuid.UUID(hex="0634594a-a8e7-4b1a-a6b1-cd5243059a56")  # write
ZIPPY_W_CONTROL = uuid.UUID(hex="ae04c4b2-892b-43be-b69c-5d13f2195390")  # write, notify
ZIPPY_W_BUFFER = uuid.UUID(hex="7f04c4b2-892b-43be-b69c-5d13f2195379")  # read, notify

ZIPPY_MAX_ALIGNED = uuid.UUID(hex="4204c4b2-892b-43be-b69c-5d13f2195359")  # read, notify
ZIPPY_ERROR = uuid.UUID(hex="d2a1e333-c56c-445c-a24d-4a4440c676f6")  # read, notify

# LOCK
ZIPPY_LOCK = uuid.UUID(hex="2f8784ec-6a34-11b6-634d-b7369dce1c55")  # write, read, notify


# PUSH
PUSH2_SERVICE = uuid.UUID(hex="0BAD7FCC-2EE4-F1AC-439F-D7B2BA250294")
PUSH2_CHARACTERISTIC = uuid.UUID(hex="80B22CC2-8C79-CAA6-B341-3D0675F9859F")  # notify


PUSH_SERVICE = uuid.UUID(hex="C742E1A3-6320-5ABC-9643-D206C677E580")


UUID_NAMES = {
    # Zippy
    str(ZIPPY_SERVICE): "Zippy Protocol",
    str(ZIPPY_R1): "Zippy TX1",
    str(ZIPPY_R2): "Zippy TX2",
    str(ZIPPY_R_CONTROL): "Zippy TX Control",
    str(ZIPPY_R_BUFFER): "Zippy TX Buffer Limit",
    str(ZIPPY_W1): "Zippy RX1",
    str(ZIPPY_W2): "Zippy RX2",
    str(ZIPPY_W_CONTROL): "Zippy RX Control",
    str(ZIPPY_W_BUFFER): "Zippy RX Buffer Limit",
    str(ZIPPY_MAX_ALIGNED): "Zippy Max Aligned",
    str(ZIPPY_ERROR): "Zippy Error",
    str(ZIPPY_LOCK): "Zippy Lock",
    # Push 2
    str(PUSH2_SERVICE): "Push2 Protocol",
    str(PUSH2_CHARACTERISTIC): "Push2 Data",
    # Push
    str(PUSH_SERVICE): "Push Protocol",
}
register_uuids(UUID_NAMES)


def buffer_notification_closure(buffer: asyncio.Queue):
    async def buffer_notification(sender: int, data: bytearray) -> None:
        logging.info(f"From handle {sender} got {data}")
        await buffer.put(data)

    return buffer_notification


def buffer_join_fragments_closure(buffer: asyncio.Queue):
    async def buffer_notification(sender: int, data: bytearray) -> None:
        logging.info(f"From handle {sender} got {data}")
        fragment_id, fragment_data = data[0], data[1:]
        await buffer.put((fragment_id, fragment_data))

    return buffer_notification


class ZippyLock(EnumBase):
    Release = False
    Acquire = True


ZippyLockAdapter = IntEnumAdapter(ZippyLock)


@dataclasses.dataclass(kw_only=True)
class ZippyLockPacket(DataclassMixin):
    AppID: uuid.UUID = csfield(GUIDAdapter(Bytes(16)))
    Lock: bool = csfield(ZippyLockAdapter(Int32ul))


ZippyLockPacketStruct = DataclassStruct(ZippyLockPacket)


@dataclasses.dataclass(kw_only=True)
class ZippyControlPacket(DataclassMixin):
    E0: int = csfield(Const(0xE0, Int8ul))
    Length: int = csfield(Int16ul)


ZippyControlPacketStruct = DataclassStruct(ZippyControlPacket)


@dataclasses.dataclass(kw_only=True)
class ZippyCalibrationPacket(DataclassMixin):
    Counter: int = csfield(Int16ul)
    Padding: int = csfield(Const(0, Int32ul))
    Flag: bool = csfield(Flag)
    Unknown: int = csfield(Int8ul)
    Mode: int = csfield(Int16ul)


ZippyCalibrationPacketStruct = DataclassStruct(ZippyCalibrationPacket)
