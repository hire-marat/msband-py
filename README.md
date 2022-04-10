# Microsoft Band Python Library

[![good-idea-license](https://img.shields.io/badge/license-GOOD%20IDEA-lightgrey?style=plastic)](#)
[![made-with-python](https://img.shields.io/badge/made%20with-Python-yellow?style=plastic)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=plastic)](https://github.com/psf/black)

## Setting up Bluetooth on Windows
* Pair the Band with your PC, making sure to press `No` when it prompts to use an iPhone/BLE
* Run `control printers` to open the `Devices and Printers`
* Find the MAC Address of your device in Properties -> Bluetooth -> Troubleshooting Information -> Unique identifier
* Copy the `BluetoothInterface` example from `msband/examples/connect.py` and replace `BLUETOOTH_MAC_ADDRESS` with the MAC Address of your device

## Setting up USB on Windows
### For a Microsoft Band 2
* Get [libusb-win32](//sourceforge.net/projects/libusb-win32/) *[sourceforge.net]*
* Open the `Filter Wizard`
* `Install a device filter` for the `vid:045e pid:02d6 rev:0001` `WinUsb Device`
* Copy the `USBInterface` example from `msband/examples/connect.py`