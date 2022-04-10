import time
import pathlib
from msband.static.command import *
from msband.static import FirmwareApp
from msband.protocol import ProtocolInterface

# Connect using your preferred interface
iband: ProtocolInterface = ...

firmware_path = pathlib.Path("envoy-2.0.5202.0.bin")
firmware_size = firmware_path.stat().st_size
firmware_bytes = firmware_path.read_bytes()

iband.command(SRAMFWUpdateBootIntoUpdateMode)
time.sleep(5)

# Reconnect
iband.reacquire()

assert int(iband.command(CoreModuleWhoAmI)) == FirmwareApp.UpApp
iband.command(
    SRAMFWUpdateLoadData,
    UpdateFileStream=firmware_bytes,
    DataLength=firmware_size,
)
