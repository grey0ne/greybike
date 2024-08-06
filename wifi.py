from utils import async_shell, check_running_on_pi, AppState
from constants import PING_TIMEOUT, ROUTER_HOSTNAME
import logging
import asyncio

async def restart_wifi():
    logger = logging.getLogger('greybike')
    if check_running_on_pi():
        logger.info('Restarting WiFi interface')
        restart_command = 'sudo ip link set wlan0 down && sleep 5 && sudo ip link set wlan0 up'
        await async_shell(restart_command)
        await asyncio.sleep(10) # Wait for wifi to come back up
    else:
        logger.error('Restarting wifi not supported on this platform')

async def ping_router(state: AppState):
    logger = logging.getLogger('greybike')
    command = f'ping -c 1 -W{PING_TIMEOUT} {ROUTER_HOSTNAME}'
    ping_result = await async_shell(command)
    if ping_result != 0:
        logger.warning(f'{ROUTER_HOSTNAME} ping failed. Return code: {ping_result}')
        await restart_wifi()

