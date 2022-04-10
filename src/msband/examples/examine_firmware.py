import pathlib
from msband.firmware import *

firmware_path = pathlib.Path("envoy-2.0.5202.0.bin")
firmware = Header.parse_file(firmware_path)

split_sections(firmware_path)
