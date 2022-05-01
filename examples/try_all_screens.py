import logging
from msband.static.command import *
from msband.static.status import Status
from msband.protocol import ProtocolInterface


# Connect using your preferred interface
iband: ProtocolInterface = ...


success = set()
invalid = set()
disabled = set()
for i in range(65535):
    logging.debug(f"Trying Screen {i}")
    status = iband.command(FireballUINavigateToScreen, Screen=i)
    if status == Status.Success:
        logging.info(f"Successfully reached screen {i}")
        success.add(i)
    elif status == Status.FireballUiInvalidScreenId:
        logging.info(f"Invalid {i}")
        invalid.add(i)
    elif status == Status.FireballUiNavigationDisabled:
        disabled.add(i)
    else:
        logging.info(f"{i}: {status}")
