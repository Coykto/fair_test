import asyncio

from aiohttp import web

from fair.repository import CarRepository
from fair.utils import JSONResponse


async def create_car(request: web.Request) -> JSONResponse:
    car_data = await request.json()
    car_id = await request.app["car_repository"].create(car_data)
    return JSONResponse(status=201, headers={"Location": f"/{car_id}"})


async def get_by_id(request: web.Request) -> JSONResponse:
    car_id = int(request.match_info.get("id"))
    data = await request.app["car_repository"].get(car_id)
    return JSONResponse(json=data)


async def update_car(request: web.Request) -> JSONResponse:
    data = await request.json()
    await request.app["car_repository"].update(data)
    return JSONResponse()


async def partially_update_car(request: web.Request) -> JSONResponse:
    car_id = int(request.match_info.get("id"))
    data = await request.json()
    await request.app["car_repository"].patch(car_id, data)
    return JSONResponse()


async def delete_car(request: web.Request) -> JSONResponse:
    car_id = int(request.match_info.get("id"))
    await request.app["car_repository"].delete(car_id)
    return JSONResponse(status=204)


async def list_cars(request: web.Request) -> JSONResponse:
    data = await request.app["car_repository"].list()
    return JSONResponse(json=data)


@web.middleware
async def error_middleware(request, handler) -> JSONResponse:
    try:
        return await handler(request)
    except web.HTTPException as ex:
        return JSONResponse(json={"error": ex.reason}, status=ex.status)
    except Exception as ex:
        return JSONResponse(json={"error": str(ex)}, status=500)


async def init_app(repository) -> web.Application:
    app = web.Application(middlewares=[error_middleware])
    car_repository = repository()
    await car_repository.initialize()
    app["car_repository"] = car_repository

    app.router.add_route("POST", "/", create_car)
    app.router.add_route("GET", "/{id:\d+}", get_by_id)
    app.router.add_route("PUT", "/", update_car)
    app.router.add_route("PATCH", "/{id:\d+}", partially_update_car)
    app.router.add_route("DELETE", "/{id:\d+}", delete_car)

    app.router.add_route("GET", "/", list_cars)
    return app


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app(CarRepository))
    web.run_app(app, loop=loop)
