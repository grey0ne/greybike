import asyncio

from data_sources.gpsd_client import GpsdClient

HOST = "router.grey"

async def main():
    async with GpsdClient(host=HOST) as client:
        print(await client.poll())  # Get gpsd POLL response
        counter = 0
        while counter < 5:
            counter += 1
            print(await client.get_result())  # Get gpsd TPV responses


asyncio.run(main())
