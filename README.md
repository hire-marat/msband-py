# Microsoft Band Python Library

[![good-idea-2-license](https://img.shields.io/badge/license-GOOD%20IDEA%202-lightgrey?style=plastic)](#)
[![made-with-python](https://img.shields.io/badge/made%20with-Python-yellow?style=plastic)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=plastic)](https://github.com/psf/black)

This library is currently just a side project to create a Python interface for the Microsoft Band and Microsoft Band 2.  
It doesn't have any friendly UIs, so unless you like gettings your hands dirty (or reading amazing Python code) this probably isn't for you. Sorry.  
I do have something in the works to enable interacting with a Band through Chromium though, stay tuned...

## Supported Features
* Communicating with a Band over Bluetooth
* Communicating with a Band over USB
* Getting/setting Band time
* Decoding/encoding Band RLE icons
* Reading/setting the Me Tile (watchface background)
* Reading tile icons (and default tiles)
* Downloading device logs
* Updating device firmware version
* Parsing/building command packets
* Parsing FirmwareUpdate.bin
* Escaping demo mode
* Entering demo mode (not recommended)

## Planned Features
* Communicating with a Band over BLE
* Escaping OOBE
* Setting profile
* Customising tile layout
* Customising colour scheme
* Updating calendar items
* Setting up custom workouts
* Generating and uploading ephemeris data to reduce TTFF
* Updating timezone info
* Processing live data from sensors
* Downloading and processing historical data
* Framework for interactive tiles running from a computer
* ~~Shenanigans~~

## Setting up a development environment
`msband` depends on `poetry` for building, `construct` for parsing/building data structures, `pyusb` for USB stuff, and `pillow` for reading images.  

Thankfully, Poetry takes care of setting up the virtual environment correctly, so here's the short set of instructions to get started:

* Install Python 3.9 or higher
* `git clone git@github.com:hire-marat/msband.git --depth 1`
* `cd msband`
* `py -m pip install poetry`
* `py -m poetry update`
* To get started, see [the *"Running the examples"* section](#Running-the-examples) *[anchor-link]*

## Setting up Bluetooth
### on Windows
* Pair the Band with your machine, making sure to press `No` when it prompts to use an iPhone/BLE
* Run `control printers` to open the `Devices and Printers`
* Find the MAC Address of your device in Properties -> Bluetooth -> Troubleshooting Information -> Unique identifier
* Copy the `BluetoothInterface` example from [examples/connect.py](examples/connect.py) and replace `BLUETOOTH_MAC_ADDRESS` with the MAC Address of your device

## Setting up USB
### on Linux
You probably already have libusb set up, and if that's the case, PyUSB will use it as a backend automatically.  
If that's not the case, please research PyUSB compatibility with your distro.
#### For a Microsoft Band 1
* Copy the `USBInterface` example from [examples/connect.py](examples/connect.py)
* Replace `USBInterface("")` with `USBInterface("", pid=0x02D7)`
#### For a Microsoft Band 2
* Copy the `USBInterface` example from [examples/connect.py](examples/connect.py)
### on Windows
#### For a Microsoft Band 1
* Get [libusb-win32](//sourceforge.net/projects/libusb-win32/) *[sourceforge.net]*
* Open the `Filter Wizard`
* `Install a device filter` for the `vid:045e pid:02d7` `WinUsb Device`
* Copy the `USBInterface` example from [examples/connect.py](examples/connect.py)
* Replace `USBInterface("")` with `USBInterface("", pid=0x02D7)`
#### For a Microsoft Band 2
* Get [libusb-win32](//sourceforge.net/projects/libusb-win32/) *[sourceforge.net]*
* Open the `Filter Wizard`
* `Install a device filter` for the `vid:045e pid:02d6 rev:0001` `WinUsb Device`
* Copy the `USBInterface` example from [examples/connect.py](examples/connect.py)

## Running the [examples](examples)
* Open an interpreter using the virtualenv set up by Poetry
  * You can:
    * Use your IDE's Python interpreter, making sure to set it to `.venv\bin\python` or `.venv\Scripts\python.exe`
    * Use IPython by running `poetry run ipython`
    * Use the Python interpreter by running `poetry run python`
* Open [examples/connect.py](examples/connect.py) in a second window with a text editor
* Open the example file you want to run in a third window with a text editor
* Replace the code `iband: ProtocolInterface = ...` with the relevant connection code from `examples/connect.py`
* Run the example code line by line in the Python interpreter

## License
[GOOD IDEA 2](LICENSE)
