
import argparse
import asyncio
import logging
import time
from pathlib import Path
from typing import cast

from tqdm import tqdm  # For progress bar
from bleak import BleakScanner
from bleak.backends.device import BLEDevice

from smpclient import SMPClient
from smpclient.generics import SMPRequest, TEr1, TEr2, TRep, error, success
from smpclient.requests.image_management import ImageStatesRead, ImageStatesWrite
from smpclient.requests.os_management import ResetWrite
from smpclient.transport.ble import SMPBLETransport

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

def parse_args():
    parser = argparse.ArgumentParser(description="Upload firmware to a selected BLE device.")
    parser.add_argument("--device-name", type=str, required=True, help="BLE device name.")
    parser.add_argument("--bin-file", type=str, required=True, help="Path to the .bin firmware file.")
    return parser.parse_args()

async def find_device_by_name(device_name: str) -> BLEDevice:
    devices = await BleakScanner.discover()
    if not devices:
        raise SystemExit("No BLE devices found")

    for device in devices:
        if device.name and device_name in device.name:
            logging.info(f"Found device: {device.name} ({device.address})")
            return cast(BLEDevice, device)

    raise SystemExit(f"Device with name '{device_name}' not found")

async def main() -> None:
    args = parse_args()

    logging.info(f"Searching for device '{args.device_name}'...")
    device = await find_device_by_name(args.device_name)
    logging.info("Device found.")

    bin_file_path = Path(args.bin_file)
    if not bin_file_path.exists():
        raise SystemExit(f"File not found: {args.bin_file}")

    logging.info(f"Reading firmware file: {bin_file_path}")
    with open(bin_file_path, "rb") as f:
        b_smp_dut_bin = f.read()

    logging.info(f"Connecting to {device.name}...")
    async with SMPClient(SMPBLETransport(), device.name or device.address) as client:
        logging.info("Connected.")

        async def ensure_request(request: SMPRequest[TRep, TEr1, TEr2]) -> TRep:
            logging.info(f"Sending request: {request}")
            response = await client.request(request)
            if success(response):
                logging.info(f"Response received: {response}")
                return response
            elif error(response):
                raise RuntimeError(f"Error response: {response}")
            else:
                raise RuntimeError(f"Unexpected response: {response}")

        # Read image state
        response = await ensure_request(ImageStatesRead())
        logging.info(f"Current image state: {response}")

        # Upload firmware with progress bar
        logging.info("Starting firmware upload...")
        start_time = time.time()
        progress_bar = tqdm(total=len(b_smp_dut_bin), unit="B", unit_scale=True, desc="Uploading")

        async for offset in client.upload(b_smp_dut_bin):
            progress_bar.n = offset
            progress_bar.refresh()

        progress_bar.close()
        logging.info("Firmware uploaded successfully.")

        # Confirm the upload
        response = await ensure_request(ImageStatesRead())
        logging.info(f"New image state: {response}")

        # Mark for testing
        logging.info("Marking new image for test...")
        await ensure_request(ImageStatesWrite(hash=response.images[1].hash))

        # Reset device
        logging.info("Resetting device for swap...")
        await ensure_request(ResetWrite())

        logging.info("Update complete!")

if __name__ == "__main__":
    asyncio.run(main())
