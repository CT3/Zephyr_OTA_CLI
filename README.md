
# Firmware Upload Tool

## Overview

This Python script allows users to upload firmware to a selected BLE (Bluetooth Low Energy) device using the Simple Management Protocol (SMP). It scans for nearby BLE devices, connects to the specified device, uploads a firmware binary, and optionally resets the device to apply the update.

## Features

- Scan and select a BLE device by name
- Upload a firmware binary file (.bin) to the device
- Display a real-time progress bar using `tqdm`
- Read and confirm image states before and after the upload
- Mark the new firmware image for testing
- Reset the device to apply the new firmware

## Requirements

### **Dependencies**

Ensure you have Python 3.8 or later installed. Install the required dependencies using:

```sh
pip install bleak smpclient tqdm
```

### **Supported Platforms**

- Linux
- macOS
- Windows (with compatible BLE adapter)

## Usage

### **Command-line Arguments**

```sh
python dfucli.py --device-name "Device_Name" --bin-file "path/to/firmware.bin"
```

### **Example**

```sh
python dfucli.py --device-name "MyBLEDevice" --bin-file "firmware_v1.2.bin"
```

## Code Structure

- **`firmware_uploader.py`**: Main script handling BLE scanning, firmware upload, and device reset.
- **Dependencies**: Uses `bleak` for BLE communication and `smpclient` for SMP protocol support.

## Troubleshooting

### **1. No BLE Devices Found**

- Ensure Bluetooth is enabled and the device is in pairing mode.
- Try running the script with elevated permissions (e.g., `sudo` on Linux/macOS).

### **2. Connection Issues**

- Check if another process is using the BLE adapter.
- Restart Bluetooth services (`sudo systemctl restart bluetooth` on Linux).

### **3. Slow Upload Speed**

- Ensure the BLE device is within close range.
- Reduce interference by minimizing other Bluetooth connections.

## License

This project is licensed under the MIT License.

## Author

Developed by MantasPats.

For contributions or issues, feel free to submit a pull request or open an issue in the repository.

