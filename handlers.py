from aiohttp import web

from telemetry_logs import reset_log
from constants import WS_TIMEOUT, SPA_ASSETS_DIR, FAVICON_DIRECTORY
from data_types import AppState
import logging
import os

MAX_WEBSOCKET_CONNECTIONS = 3

async def reset_log_handler(request: web.Request):
    reset_log(request.app['state'])
    return web.Response(text='Log file reset')

def file_response(file_path: str) -> web.FileResponse:
    # TODO add in memory cache. read file in memory and store it in dict or something
    response = web.FileResponse(file_path)
    response.headers.setdefault('Cache-Control', 'max-age=3600')
    return response

def get_file_serve_handler(file_path: str):
    async def file_serve_handler(request: web.Request):
        return file_response(file_path)
    return file_serve_handler

async def websocket_handler(request: web.Request):
    logger = logging.getLogger('greybike')
    logger.info('New websocket connection')
    state: AppState = request.app['state']
    if len(state.websockets) > MAX_WEBSOCKET_CONNECTIONS:
        msg = f'Too many websocket connections: {len(state.websockets)}'
        logger.warning(msg)
        return web.Response(text=msg, status=400)
    ws = web.WebSocketResponse(timeout=WS_TIMEOUT)
    await ws.prepare(request)
    state.websockets.append(ws)
    try:
        async for msg in ws:
            logger.debug(f'Websocket message {msg}')
    finally:
        await ws.close()
        state.websockets.remove(ws)
        logger.info('Websocket connection closed')
    return ws

async def spa_asset_handler(request: web.Request):
    file_name = request.match_info['file']
    file_path = os.path.join(SPA_ASSETS_DIR, file_name)
    if not os.path.exists(file_path):
        return web.Response(text='File not found', status=404)
    return file_response(file_path)


async def icons_handler(request: web.Request):
    file_name = request.match_info['file']
    file_path = os.path.join(FAVICON_DIRECTORY, file_name)
    if not os.path.exists(file_path):
        return web.Response(text='File not found', status=404)
    return file_response(file_path)
