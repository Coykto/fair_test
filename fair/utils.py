from typing import Optional

import ujson
from aiohttp.web import Response


class JSONResponse(Response):
    def __init__(self, json: Optional[dict] = None, *args, **kwargs):
        if json is None:
            json = dict()
        kwargs["text"] = ujson.dumps(json)
        kwargs["content_type"] = "application/json"
        super().__init__(*args, **kwargs)
