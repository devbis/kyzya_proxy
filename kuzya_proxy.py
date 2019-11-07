#!/usr/bin/env python3

import json
import os

from aiohttp import web, ClientSession
from jsonpath_ng import parse

config = None


async def handle(request):
    for item in config['config']:
        if item['path'] == request.match_info.get('path'):
            async with ClientSession() as session:
                resp = await session.get(item['url'])
                result = await resp.json(content_type=None)
                value_list = parse(item['jsonpath']).find(result)
                value = value_list[0].value
                if value.isnumeric():
                    value = int(value)
                else:
                    try:
                        value = float(value)
                    except ValueError:
                        pass

            return web.json_response({"value": value})
    else:
        raise web.HTTPNotFound()


async def web_app():
    global config
    with open(os.environ.get('CONFIG', 'config.json')) as conf_file:
        config = json.load(conf_file)
    app = web.Application()
    app.add_routes([
        web.get('/{path:.*}', handle),
    ])
    return app
