"""
CRUD операции для работы с базой данных
"""
from typing import Optional, List
import aiosqlite
from datetime import datetime
from config import DB_PATH


async def get_or_create_user(user_id: int, username: Optional[str] = None) -> dict:
    """Получить или создать пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        )
        user = await cursor.fetchone()
        
        if user:
            return dict(user)
        else:
            await db.execute(
                """INSERT INTO users (user_id, username, driver_type, car_consumption, 
                   preferred_balance, max_willing_distance, time_value, cards)
                   VALUES (?, ?, 'regular', 8.0, 'balanced', 10.0, 10.0, '[]')""",
                (user_id, username)
            )
            await db.commit()
            cursor = await db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            )
            return dict(await cursor.fetchone())


async def update_user_profile(user_id: int, **kwargs) -> dict:
    """Обновить профиль пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Формируем запрос обновления
        updates = []
        values = []
        
        allowed_fields = ['driver_type', 'car_consumption', 'preferred_balance', 
                         'max_willing_distance', 'time_value', 'cards']
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                values.append(value)
        
        if not updates:
            # Если нет полей для обновления, просто возвращаем пользователя
            cursor = await db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            )
            return dict(await cursor.fetchone())
        
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
        
        await db.execute(query, values)
        await db.commit()
        
        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        )
        return dict(await cursor.fetchone())


async def get_azs_by_network_and_city(network: str, city: str) -> List[dict]:
    """Получить список АЗС по сети и городу"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM azs WHERE network = ? AND city = ?",
            (network, city)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_all_azs_by_city(city: str) -> List[dict]:
    """Получить все АЗС в городе"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM azs WHERE city = ?",
            (city,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_azs_by_id(azs_id: int) -> Optional[dict]:
    """Получить АЗС по ID"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM azs WHERE id = ?",
            (azs_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def add_price(azs_id: int, fuel_type: str, price: float, user_id: int) -> int:
    """Добавить цену"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """INSERT INTO prices (azs_id, fuel_type, price, user_id)
               VALUES (?, ?, ?, ?)""",
            (azs_id, fuel_type, price, user_id)
        )
        await db.commit()
        return cursor.lastrowid


async def get_latest_prices_by_city_and_fuel(
    city: str, 
    fuel_type: str, 
    limit: int = 5
) -> List[dict]:
    """Получить последние цены по городу и типу топлива, отсортированные по цене"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        # Получаем последние цены для каждой АЗС
        cursor = await db.execute("""
            SELECT 
                p.id,
                p.azs_id,
                p.fuel_type,
                p.price,
                p.user_id,
                p.timestamp,
                a.network,
                a.address,
                a.city,
                a.lat,
                a.lon
            FROM prices p
            INNER JOIN azs a ON p.azs_id = a.id
            WHERE a.city = ? AND p.fuel_type = ?
            AND p.id IN (
                SELECT MAX(id) 
                FROM prices 
                WHERE azs_id = p.azs_id AND fuel_type = p.fuel_type
            )
            ORDER BY p.price ASC
            LIMIT ?
        """, (city, fuel_type, limit))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_price_age_minutes(price_id: int) -> Optional[int]:
    """Получить возраст цены в минутах"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT timestamp FROM prices WHERE id = ?",
            (price_id,)
        )
        row = await cursor.fetchone()
        if row:
            timestamp = datetime.fromisoformat(row[0])
            age = datetime.now() - timestamp
            return int(age.total_seconds() / 60)
        return None

