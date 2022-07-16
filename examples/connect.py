# %%
from msband.protocol import MockInterface
iband = MockInterface()

# %%
from msband.protocol import USBInterface
iband = USBInterface("")

# %%
from msband.protocol import BluetoothInterface
BLUETOOTH_MAC_ADDRESS = "00:00:00:00:00:00"
iband = BluetoothInterface(BLUETOOTH_MAC_ADDRESS)

# %%
from msband.protocol import BLEv2Interface
BLUETOOTH_MAC_ADDRESS = "00:00:00:00:00:00"
iband = BLEv2Interface()
await iband.acquire(BLUETOOTH_MAC_ADDRESS)

# %%
from msband.static.command import *
