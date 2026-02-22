import json
import csv

# --- Настройки ---
# 1. Поместите ваш файл с данными в ту же папку, что и скрипт, и назовите его 'data.json'
input_filename = 'data.json'
# 2. Имя файла, который получится на выходе
output_filename = 'azs_list.csv'
# ----------------

# Читаем JSON файл
try:
    with open(input_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Ошибка: Файл '{input_filename}' не найден.")
    print("Пожалуйста, сохраните ваш JSON список в файл с именем 'data.json' в той же папке, где запускаете скрипт.")
    exit()
except json.JSONDecodeError:
    print(f"Ошибка: Файл '{input_filename}' содержит некорректный JSON.")
    exit()

# Проверяем, что данные — это список
if not isinstance(data, list):
    print("Ошибка: Ожидался список JSON объектов, но получен другой тип.")
    exit()

print(f"Найдено {len(data)} записей. Начинаю обработку...")

# Открываем CSV файл для записи
with open(output_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
    # Определяем заголовки столбцов, которые хотим видеть в CSV
    # (можно добавить или убрать любые поля из вашего JSON)
    fieldnames = [
        'name', 'brand', 'address', 'latitude', 'longitude',
        'workingHours', 'hasCafe', 'hasShop', 'hasWash', 'hasPump',
        'fuelPrices', 'website', 'osm_id'
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    # Записываем заголовок
    writer.writeheader()

    # Обрабатываем каждую запись
    successful_rows = 0
    for item in data:
        # Словарь для записи в CSV
        row = {}

        # Копируем значения из JSON, если ключ существует
        for key in fieldnames:
            if key in item:
                value = item[key]
                # Преобразуем словарь с ценами в строку, чтобы было удобнее читать
                if key == 'fuelPrices' and isinstance(value, dict):
                    # Если в словаре есть цены, перечислим их через запятую
                    if value:
                        row[key] = ', '.join([f"{k}: {v}" for k, v in value.items()])
                    else:
                        row[key] = '' # Пусто, если нет цен
                else:
                    row[key] = value
            else:
                row[key] = '' # Пустая строка, если ключа нет в JSON

        # Добавляем обработанную строку в CSV
        writer.writerow(row)
        successful_rows += 1

print(f"Готово! Создан файл '{output_filename}' с {successful_rows} заправками.")
