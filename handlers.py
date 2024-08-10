from aiohttp import web

from telemetry_logs import reset_log
from dash_page import DASH_PAGE_HTML
from constants import MANIFEST, WS_TIMEOUT, SPA_ASSETS_DIR
from data_types import AppState
from logs_page import render_logs_page
import logging
import os

async def http_handler(request: web.Request):
    return web.Response(text=DASH_PAGE_HTML, content_type='text/html')

async def manifest_handler(request: web.Request):
    return web.Response(text=MANIFEST, content_type='application/json')

async def reset_log_handler(request: web.Request):
    reset_log(request.app['state'])
    return web.Response(text='Log file reset')

def file_response(file_path: str) -> web.FileResponse:
    response = web.FileResponse(file_path)
    response.headers.setdefault('Cache-Control', 'max-age=3600')
    return response

def get_file_serve_handler(file_path: str):
    async def file_serve_handler(request: web.Request):
        return file_response(file_path)
    return file_serve_handler

async def websocket_handler(request: web.Request):
    logger = logging.getLogger('greybike')
    ws = web.WebSocketResponse(timeout=WS_TIMEOUT)
    await ws.prepare(request)
    state: AppState = request.app['state']
    state.websockets.append(ws)
    try:
        async for msg in ws:
            logger.debug(f'Websocket message {msg}')
    finally:
        state.websockets.remove(ws)
    return ws

async def spa_asset_handler(request: web.Request):
    file_name = request.match_info['file']
    file_path = os.path.join(SPA_ASSETS_DIR, file_name)
    if not os.path.exists(file_path):
        return web.Response(text='File not found', status=404)
    return file_response(file_path)


async def log_list_handler(request: web.Request):
    state: AppState = request.app['state']
    return web.Response(text=render_logs_page(state.log_files), content_type='text/html')

