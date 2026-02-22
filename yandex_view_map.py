import json
import csv
import os

input_filename = 'belarus_azs_merged.json'
output_filename = 'azs_minimal.csv'

print("🚀 Создаю минимальный файл с id...")

if not os.path.exists(input_filename):
    print(f"❌ Файл {input_filename} не найден!")
    exit()

with open(input_filename, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"✅ Загружено записей: {len(data)}")

with open(output_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
    csvfile.write("latitude,longitude,name,id\n")

    count = 0
    for item in data:
        if 'latitude' in item and 'longitude' in item:
            lat = item['latitude']
            lon = item['longitude']

            # Обработка name
            name_raw = item.get('name')
            if name_raw is None:
                name = 'АЗС'
            else:
                name = str(name_raw).replace(',', ' ').replace('"', '""').strip()

            # Обработка id
            id_raw = item.get('id')
            if id_raw is None:
                id_val = ''
            else:
                id_val = str(id_raw)

            if lat and lon:
                # Экранирование name: если есть проблемные символы, обернуть в кавычки
                # Проверим наличие запятой, кавычек или перевода строки
                if any(c in name for c in [',', '"', '\n']):
                    name_escaped = f'"{name}"'
                else:
                    name_escaped = name

                # id редко содержит спецсимволы, но для единообразия применим то же правило
                if any(c in id_val for c in [',', '"', '\n']):
                    id_escaped = f'"{id_val}"'
                else:
                    id_escaped = id_val

                csvfile.write(f"{lat},{lon},{name_escaped},{id_escaped}\n")
                count += 1

    print(f"✅ Создан файл {output_filename} с {count} записей (включая колонку id)")

print("\n📌 Инструкция по загрузке в Яндекс.Конструктор карт:")
print("1. https://yandex.ru/map-constructor/")
print("2. Создать карту → Импорт")
print("3. Выберите файл:", output_filename)
print("4. В настройках укажите соответствие полей:")
print("   • Широта → latitude")
print("   • Долгота → longitude")
print("   • Подпись → name")
print("   • (дополнительно) Описание → id")