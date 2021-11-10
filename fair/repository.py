from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Dict,
    List,
    Optional,
)

import asyncpg
from asyncpg import Pool

from settings import settings


class BaseRepository(ABC):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    async def initialize(self):
        pass

    @abstractmethod
    async def create(self, obj: dict) -> int:
        pass

    @abstractmethod
    async def get(self, car_id: int) -> Dict:
        pass

    @abstractmethod
    async def list(self) -> List[Dict]:
        pass

    @abstractmethod
    async def update(self, car: dict):
        pass

    @abstractmethod
    async def patch(self, car_id: int, car: dict):
        pass

    @abstractmethod
    async def delete(self, car_id: int):
        pass


class CarRepository(BaseRepository):
    pool: Pool = None

    async def initialize(self):
        self.pool = await asyncpg.create_pool(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USERNAME,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
        )

    async def create(self, obj: dict) -> int:
        async with self.pool.acquire() as connection:
            keys = ", ".join(obj.keys())
            params = ", ".join([f"${i+1}" for i in range(len(obj))])
            stmt = f"INSERT INTO cars({keys}) VALUES ({params}) RETURNING id"
            return await connection.fetchval(stmt, *obj.values())

    async def get(self, car_id: int) -> Optional[Dict]:
        async with self.pool.acquire() as connection:
            result = await connection.fetchrow(
                "SELECT * FROM cars WHERE id = $1", car_id
            )
            if result is not None:
                return dict(result)

    async def list(self) -> List[Dict]:
        async with self.pool.acquire() as connection:
            return [dict(row) for row in await connection.fetch("SELECT * FROM cars")]

    async def update(self, car: dict):
        car_id = car.pop("id")
        async with self.pool.acquire() as connection:
            stmt = f"UPDATE cars SET model=$2, year=$3 WHERE id = $1"
            return await connection.execute(
                stmt, car_id, car.get("model", None), car.get("year", None)
            )

    async def patch(self, car_id: int, car: dict):
        car_id = car.pop("id")
        async with self.pool.acquire() as connection:
            set_params = ", ".join(f"{key}={value}" for key, value in car.items())
            stmt = f"UPDATE cars SET {set_params} WHERE id = $1"
            return await connection.execute(stmt, car_id)

    async def delete(self, car_id: int):
        async with self.pool.acquire() as connection:
            return await connection.execute("DELETE FROM cars WHERE id = $1", car_id)

    async def clear(self):
        async with self.pool.acquire() as connection:
            await connection.execute("DELETE FROM cars")


class TestRepository(BaseRepository):
    cars = dict()

    async def create(self, obj: dict) -> int:
        last_index = len(self.cars)
        obj["id"] = last_index
        self.cars[last_index] = obj
        return last_index

    async def get(self, car_id: int) -> Optional[Dict]:
        return self.cars.get(car_id)

    async def list(self) -> List[Dict]:
        return [car for car in self.cars.values()]

    async def update(self, car: dict):
        self.cars[car["id"]] = car

    async def patch(self, car_id: int, car: dict):
        if "id" in car:
            del car["id"]
        existing_car = self.cars[car_id].copy()
        for key, value in car.items():
            existing_car[key] = value
        self.cars[car_id] = existing_car

    async def delete(self, car_id: int):
        del self.cars[car_id]

    async def clear(self):
        self.cars.clear()
