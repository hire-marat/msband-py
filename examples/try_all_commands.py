import logging
from msband.static.command import *
from msband.static.status import Status
from msband.protocol import USBInterface


# Connect using USB for best results
iband: USBInterface = ...


logging.root.handlers[0].level = 20
from usb.core import USBError

for facility in range(Facility.Max + 1):
    for code in range(0x7F + 1):
        try:
            facility = Facility(facility)
        except ValueError:
            pass

        try:
            command_name = Command.from_fields[facility, code, True].Name
        except KeyError:
            command_name = None

        try:
            result = iband.command(
                Command(
                    Facility=facility,
                    Code=code,
                    Transferless=True,
                    Arguments={},
                    Response=Bytes(720),
                )
            )
        except USBError:
            if command_name is None:
                logging.warning(f"Bad size for {facility!r} command {code}!")
            else:
                logging.warning(f"Bad size for {facility!r} command {command_name}!")
            iband.reset()
            continue

        status = Status.Success
        if isinstance(result, tuple):
            result, status = result

        if status == Status.UsbCmdProtocolBadCommand:
            continue

        if command_name is None:
            logging.info(f"Got result from {facility!r} command {code}: {result}")
        else:
            logging.info(f"Got result from {facility!r} command {command_name}: {result}")


# %%
b = None
for i in range(1, 0xFFFF):
    try:
        result = iband.command(
            Command(
                Facility=Facility.ModuleProfile,
                Code=8,
                Transferless=True,
                Response=Bytes(i),
            )
        )
    except USBError as a:
        b = a
        iband.reset()
        continue

    if set(result) == {0}:
        continue

    print(i)
    break
