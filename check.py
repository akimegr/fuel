import os
from pathlib import Path

print("=" * 60)
print("🔍 ДИАГНОСТИКА .env ФАЙЛА")
print("=" * 60)

# 1. Проверяем файл
env_path = Path(__file__).parent / '.env'
print(f"1. Путь к .env: {env_path}")
print(f"2. Файл существует: {env_path.exists()}")

if env_path.exists():
    # 2. Читаем файл как есть
    with open(env_path, 'rb') as f:
        raw_content = f.read()

    print(f"3. Сырые байты файла: {raw_content}")
    print(f"4. Длина файла: {len(raw_content)} байт")

    # 3. Показываем каждый символ
    print("\n5. Посимвольный анализ:")
    for i, byte in enumerate(raw_content):
        char = chr(byte) if byte < 128 else f'\\x{byte:02x}'
        print(f"   Позиция {i:3d}: {byte:3d} (0x{byte:02x}) = '{char}'")

    # 4. Пытаемся декодировать
    try:
        content_utf8 = raw_content.decode('utf-8')
        print(f"\n6. UTF-8 декодирование: УСПЕХ")
        print(f"   Декодировано: '{content_utf8}'")
    except UnicodeDecodeError as e:
        print(f"\n6. UTF-8 декодирование: ОШИБКА - {e}")

    # 5. Пробуем другие кодировки
    for encoding in ['utf-8-sig', 'cp1251', 'latin-1']:
        try:
            decoded = raw_content.decode(encoding)
            print(f"7. {encoding}: '{decoded}'")
        except:
            pass

    # 6. Ищем BOT_TOKEN
    print("\n8. Поиск BOT_TOKEN в строке:")
    lines = raw_content.decode('utf-8', errors='ignore').split('\n')
    for i, line in enumerate(lines):
        print(f"   Строка {i}: '{line}'")
        if 'BOT_TOKEN' in line:
            parts = line.split('=', 1)
            if len(parts) == 2:
                token = parts[1].strip()
                print(f"   ⭐ НАЙДЕН ТОКЕН! Длина: {len(token)} символов")
                print(f"   ⭐ Токен: {token[:15]}...")

print("\n" + "=" * 60)
print("🔍 ПРОВЕРКА ЗАГРУЗКИ ЧЕРЕЗ python-dotenv")
print("=" * 60)

try:
    from dotenv import load_dotenv

    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    print(f"python-dotenv загрузил токен: {'ДА' if token else 'НЕТ'}")
    if token:
        print(f"Значение: {token[:15]}...")
        print(f"Длина: {len(token)}")
        print(f"Полный токен (для проверки): {token}")
except Exception as e:
    print(f"Ошибка загрузки: {e}")