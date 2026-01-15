"""
Модели базы данных
"""
import aiosqlite
from config import DB_PATH


async def init_db():
    """Инициализация базы данных и создание таблиц"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Таблица пользователей
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                rating REAL DEFAULT 5.0,
                driver_type TEXT DEFAULT 'regular',
                car_consumption REAL DEFAULT 8.0,
                preferred_balance TEXT DEFAULT 'balanced',
                max_willing_distance REAL DEFAULT 10.0,
                time_value REAL DEFAULT 10.0,
                cards TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица АЗС
        await db.execute("""
            CREATE TABLE IF NOT EXISTS azs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                network TEXT NOT NULL,
                address TEXT NOT NULL,
                city TEXT NOT NULL,
                zone TEXT DEFAULT 'center',
                distance REAL DEFAULT 0.0,
                lat REAL,
                lon REAL,
                discount_card INTEGER DEFAULT 0,
                traffic TEXT DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица цен
        await db.execute("""
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                azs_id INTEGER NOT NULL,
                fuel_type TEXT NOT NULL,
                price REAL NOT NULL,
                user_id INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (azs_id) REFERENCES azs(id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Индексы для ускорения запросов
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_prices_azs_fuel 
            ON prices(azs_id, fuel_type)
        """)
        
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_prices_timestamp 
            ON prices(timestamp DESC)
        """)
        
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_azs_city 
            ON azs(city)
        """)
        
        await db.commit()
        
        # Миграция: добавляем новые поля для существующих пользователей
        try:
            await db.execute("""
                ALTER TABLE users ADD COLUMN driver_type TEXT DEFAULT 'regular'
            """)
        except Exception:
            pass  # Поле уже существует
        
        try:
            await db.execute("""
                ALTER TABLE users ADD COLUMN car_consumption REAL DEFAULT 8.0
            """)
        except Exception:
            pass
        
        try:
            await db.execute("""
                ALTER TABLE users ADD COLUMN preferred_balance TEXT DEFAULT 'balanced'
            """)
        except Exception:
            pass
        
        try:
            await db.execute("""
                ALTER TABLE users ADD COLUMN max_willing_distance REAL DEFAULT 10.0
            """)
        except Exception:
            pass
        
        try:
            await db.execute("""
                ALTER TABLE users ADD COLUMN time_value REAL DEFAULT 10.0
            """)
        except Exception:
            pass
        
        try:
            await db.execute("""
                ALTER TABLE users ADD COLUMN cards TEXT DEFAULT '[]'
            """)
        except Exception:
            pass
        
        # Миграция для АЗС
        try:
            await db.execute("""
                ALTER TABLE azs ADD COLUMN zone TEXT DEFAULT 'center'
            """)
        except Exception:
            pass
        
        try:
            await db.execute("""
                ALTER TABLE azs ADD COLUMN distance REAL DEFAULT 0.0
            """)
        except Exception:
            pass
        
        try:
            await db.execute("""
                ALTER TABLE azs ADD COLUMN discount_card INTEGER DEFAULT 0
            """)
        except Exception:
            pass
        
        try:
            await db.execute("""
                ALTER TABLE azs ADD COLUMN traffic TEXT DEFAULT 'medium'
            """)
        except Exception:
            pass
        
        await db.commit()
        
        # Добавляем начальные данные, если база пуста
        await add_initial_azs(db)


async def add_initial_azs(db):
    """Добавление начальных АЗС Минска"""
    # Проверяем, есть ли уже данные
    cursor = await db.execute("SELECT COUNT(*) FROM azs")
    count = await cursor.fetchone()
    if count[0] > 0:
        return
    
    # Список реальных АЗС Минска (примерные координаты)
    initial_azs = [
        ('Лукойл', 'пр. Победителей, 10', 'Минск', 53.9045, 27.5615),
        ('Лукойл', 'ул. Тимирязева, 45', 'Минск', 53.9200, 27.5800),
        ('А100', 'пр. Независимости, 95', 'Минск', 53.9000, 27.5500),
        ('А100', 'ул. Тимирязева, 50', 'Минск', 53.9150, 27.5750),
        ('Газпром', 'ул. Червякова, 8', 'Минск', 53.8900, 27.5400),
        ('Газпром', 'пр. Дзержинского, 125', 'Минск', 53.8700, 27.5200),
        ('Белнефтехим', 'ул. Кальварийская, 25', 'Минск', 53.9100, 27.5600),
        ('Белнефтехим', 'пр. Партизанский, 150', 'Минск', 53.8800, 27.5300),
        ('Танко', 'ул. Притыцкого, 83', 'Минск', 53.9050, 27.5450),
        ('Танко', 'пр. Рокоссовского, 150', 'Минск', 53.9250, 27.5900),
        ('Shell', 'ул. Орловская, 76', 'Минск', 53.8950, 27.5500),
        ('Shell', 'пр. Победителей, 65', 'Минск', 53.9150, 27.5700),
        ('Лукойл', 'ул. Сурганова, 50', 'Минск', 53.9000, 27.5800),
        ('А100', 'ул. Бобруйская, 25', 'Минск', 53.8850, 27.5100),
        ('Газпром', 'ул. Козлова, 20', 'Минск', 53.9200, 27.6000),
    ]
    
    await db.executemany("""
        INSERT INTO azs (network, address, city, lat, lon)
        VALUES (?, ?, ?, ?, ?)
    """, initial_azs)
    await db.commit()

