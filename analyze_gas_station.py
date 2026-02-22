import json
from collections import defaultdict
from typing import Dict, List

INPUT_FILE = "belarus_gas_stations.json"
OUTPUT_REPORT = "station_analysis_report.txt"

# Словарь с сайтами брендов (на русском) - обновлён на основе данных
BRAND_WEBSITES = {
    "Белоруснефть": "https://azs.belorusneft.by",
    "Лукойл": "https://lukoil.by",
    "ЛУКОЙЛ": "https://lukoil.by",
    "А-100": "https://a-100.by",
    "Газпромнефть": "https://gpnbonus.by",
    "Газпром нефть": "https://gpnbonus.by",
    "United Company": "https://united-company.by",
    "Юнайтед Компани": "https://united-company.by",
    "Славнефть": "https://www.rn-west.by",
    "Роснефть": "https://www.rn-west.by",
    "Мингаз": "http://mingas.by",
    "Белтрансгаз": "https://www.metan.by",
    "Экогаз": "https://www.metan.by",
    "БНК": "https://www.bnk.by",
    "Легавтотранс": "Не найден",
    "Милком": "Не найден",
    "Бутан": "Не найден",
    "Газ": "Не найден",
}


def analyze_stations():
    """Анализирует собранные данные и генерирует отчёт"""

    print("Загрузка данных...")
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            stations = json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: Файл {INPUT_FILE} не найден!")
        return
    except json.JSONDecodeError:
        print(f"Ошибка: Файл {INPUT_FILE} содержит некорректный JSON!")
        return

    print(f"Загружено {len(stations)} АЗС")

    # Статистика
    brand_stats = defaultdict(int)
    stations_by_brand = defaultdict(list)

    # Списки проблемных ID
    unknown_name_ids = []
    unknown_brand_ids = []
    no_coords_ids = []
    no_fuel_ids = []
    low_fuel_ids = []  # меньше 3 видов топлива
    no_hours_ids = []
    no_cafe_ids = []
    no_shop_ids = []
    no_wash_ids = []

    # Статистика по сайтам
    stations_with_website = []
    stations_without_website = []

    # Анализируем каждую станцию
    for station in stations:
        station_id = station["id"]
        brand = station["brand"]
        name = station["name"]

        # Статистика по брендам
        brand_stats[brand] += 1
        stations_by_brand[brand].append(station)

        # Статистика по сайтам
        if station.get("website"):
            stations_with_website.append(station_id)
        else:
            stations_without_website.append(station_id)

        # 3. name не определён
        if name == "Unknown" or "unknown" in name.lower():
            unknown_name_ids.append(station_id)

        # 4. brand не определён
        if brand == "Unknown":
            unknown_brand_ids.append(station_id)

        # 5. нет координат
        if not station.get("latitude") or not station.get("longitude"):
            no_coords_ids.append(station_id)

        # 6. нет топлива
        fuel_prices = station.get("fuelPrices", {})
        if not fuel_prices:
            no_fuel_ids.append(station_id)
        # 7. меньше 3 видов топлива
        elif len(fuel_prices) < 3:
            low_fuel_ids.append(station_id)

        # 8. нет времени работы
        if station.get("workingHours") in [None, "", "Не указано"]:
            no_hours_ids.append(station_id)

        # 9. нет кафе
        if not station.get("hasCafe"):
            no_cafe_ids.append(station_id)

        # 10. нет магазина
        if not station.get("hasShop"):
            no_shop_ids.append(station_id)

        # 11. нет мойки
        if not station.get("hasWash"):
            no_wash_ids.append(station_id)

    # Генерация отчёта
    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("АНАЛИЗ ДАННЫХ ОБ АЗС В БЕЛАРУСИ\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Всего АЗС: {len(stations)}\n")
        f.write(f"Уникальных брендов: {len(brand_stats)}\n")
        f.write(f"АЗС с указанием сайта: {len(stations_with_website)}\n")
        f.write(f"АЗС без сайта: {len(stations_without_website)}\n\n")

        # 1. Список брендов и количество
        f.write("1. СТАТИСТИКА ПО БРЕНДАМ\n")
        f.write("-" * 40 + "\n")
        sorted_brands = sorted(brand_stats.items(), key=lambda x: x[1], reverse=True)
        for brand, count in sorted_brands:
            f.write(f"  {brand}: {count} АЗС\n")

        # 2. Станции по брендам
        f.write("\n\n2. СТАНЦИИ ПО БРЕНДАМ\n")
        f.write("-" * 40 + "\n")
        for brand, brand_stations in sorted(stations_by_brand.items(), key=lambda x: x[0]):
            f.write(f"\n{brand}:\n")
            for i, station in enumerate(brand_stations, 1):
                name = station.get('name', 'Unknown')
                address = station.get('address', 'Адрес не указан')
                website = station.get('website', '')
                website_info = f" (сайт: {website})" if website else ""
                f.write(f"  АЗС N{i} - {name} ({address}){website_info}\n")

        # 3. ID с неизвестным name
        f.write(f"\n\n3. ID С НЕИЗВЕСТНЫМ NAME ({len(unknown_name_ids)})\n")
        f.write("-" * 40 + "\n")
        if unknown_name_ids:
            for i, station_id in enumerate(unknown_name_ids, 1):
                f.write(f"  {i}. {station_id}\n")
        else:
            f.write("  Не найдено\n")

        # 4. ID с неизвестным brand
        f.write(f"\n\n4. ID С НЕИЗВЕСТНЫМ BRAND ({len(unknown_brand_ids)})\n")
        f.write("-" * 40 + "\n")
        if unknown_brand_ids:
            for i, station_id in enumerate(unknown_brand_ids, 1):
                f.write(f"  {i}. {station_id}\n")
        else:
            f.write("  Не найдено\n")

        # 5. ID с отсутствующими координатами
        f.write(f"\n\n5. ID С ОТСУТСТВУЮЩИМИ КООРДИНАТАМИ ({len(no_coords_ids)})\n")
        f.write("-" * 40 + "\n")
        if no_coords_ids:
            for i, station_id in enumerate(no_coords_ids, 1):
                f.write(f"  {i}. {station_id}\n")
        else:
            f.write("  Не найдено\n")

        # 6. ID без информации о топливе
        f.write(f"\n\n6. ID БЕЗ ИНФОРМАЦИИ О ТОПЛИВЕ ({len(no_fuel_ids)})\n")
        f.write("-" * 40 + "\n")
        if no_fuel_ids:
            f.write(f"  Всего: {len(no_fuel_ids)} АЗС\n")
            # Показываем первые 20, чтобы не переполнять отчёт
            for i, station_id in enumerate(no_fuel_ids[:20], 1):
                f.write(f"  {i}. {station_id}\n")
            if len(no_fuel_ids) > 20:
                f.write(f"  ... и ещё {len(no_fuel_ids) - 20} АЗС\n")
        else:
            f.write("  Не найдено\n")

        # 7. ID с менее чем 3 видами топлива
        f.write(f"\n\n7. ID С МЕНЕЕ 3 ВИДОВ ТОПЛИВА ({len(low_fuel_ids)})\n")
        f.write("-" * 40 + "\n")
        if low_fuel_ids:
            f.write(f"  Всего: {len(low_fuel_ids)} АЗС\n")
            for i, station_id in enumerate(low_fuel_ids[:20], 1):
                f.write(f"  {i}. {station_id}\n")
            if len(low_fuel_ids) > 20:
                f.write(f"  ... и ещё {len(low_fuel_ids) - 20} АЗС\n")
        else:
            f.write("  Не найдено\n")

        # 8. ID без времени работы
        f.write(f"\n\n8. ID БЕЗ ВРЕМЕНИ РАБОТЫ ({len(no_hours_ids)})\n")
        f.write("-" * 40 + "\n")
        if no_hours_ids:
            f.write(f"  Всего: {len(no_hours_ids)} АЗС\n")
            for i, station_id in enumerate(no_hours_ids[:20], 1):
                f.write(f"  {i}. {station_id}\n")
            if len(no_hours_ids) > 20:
                f.write(f"  ... и ещё {len(no_hours_ids) - 20} АЗС\n")
        else:
            f.write("  Не найдено\n")

        # 9. ID без кафе
        f.write(f"\n\n9. ID БЕЗ КАФЕ ({len(no_cafe_ids)})\n")
        f.write("-" * 40 + "\n")
        if no_cafe_ids:
            f.write(f"  Всего: {len(no_cafe_ids)} АЗС (это нормально, кафе есть не на всех АЗС)\n")
        else:
            f.write("  Не найдено\n")

        # 10. ID без магазина
        f.write(f"\n\n10. ID БЕЗ МАГАЗИНА ({len(no_shop_ids)})\n")
        f.write("-" * 40 + "\n")
        if no_shop_ids:
            f.write(f"  Всего: {len(no_shop_ids)} АЗС\n")
        else:
            f.write("  Не найдено\n")

        # 11. ID без мойки
        f.write(f"\n\n11. ID БЕЗ МОЙКИ ({len(no_wash_ids)})\n")
        f.write("-" * 40 + "\n")
        if no_wash_ids:
            f.write(f"  Всего: {len(no_wash_ids)} АЗС\n")
        else:
            f.write("  Не найдено\n")

        # 12. Сайты брендов
        f.write(f"\n\n12. САЙТЫ БРЕНДОВ В БЕЛАРУСИ\n")
        f.write("-" * 40 + "\n")

        for brand in sorted(brand_stats.keys()):
            # Ищем сайт для бренда (регистронезависимо)
            website = None
            for b, url in BRAND_WEBSITES.items():
                if b.lower() in brand.lower() or brand.lower() in b.lower():
                    website = url
                    break

            if not website:
                # Пробуем найти сайт среди станций этого бренда
                brand_stations = stations_by_brand.get(brand, [])
                for station in brand_stations:
                    if station.get("website"):
                        website = station.get("website")
                        break

                if not website:
                    website = "Не найден"

            f.write(f"  {brand}: {website}\n")

        # Статистика по топливу
        f.write("\n\n13. СТАТИСТИКА ПО ТОПЛИВУ\n")
        f.write("-" * 40 + "\n")

        # Собираем все виды топлива
        all_fuel_types = set()
        fuel_counts = defaultdict(int)
        for station in stations:
            for fuel in station.get("fuelPrices", {}).keys():
                all_fuel_types.add(fuel)
                fuel_counts[fuel] += 1

        f.write(f"Всего видов топлива: {len(all_fuel_types)}\n")
        f.write("\nРаспределение по типам:\n")
        for fuel in sorted(all_fuel_types):
            count = fuel_counts[fuel]
            percentage = (count / len(stations)) * 100 if stations else 0
            f.write(f"  {fuel}: {count} АЗС ({percentage:.1f}%)\n")

        # Статистика по сайтам
        f.write("\n\n14. СТАТИСТИКА ПО САЙТАМ\n")
        f.write("-" * 40 + "\n")
        f.write(f"АЗС с сайтом: {len(stations_with_website)}\n")
        f.write(f"АЗС без сайта: {len(stations_without_website)}\n")

        if stations_with_website:
            f.write("\nПримеры сайтов:\n")
            sample_stations = [s for s in stations if s.get("website")][:10]
            for station in sample_stations:
                f.write(f"  {station['brand']} - {station['name']}: {station['website']}\n")

        # Сводка
        f.write("\n\n" + "=" * 80 + "\n")
        f.write("СВОДКА\n")
        f.write("=" * 80 + "\n")
        f.write(f"Всего АЗС: {len(stations)}\n")
        f.write(f"Брендов: {len(brand_stats)}\n")
        f.write(f"АЗС без названия: {len(unknown_name_ids)}\n")
        f.write(f"АЗС без бренда: {len(unknown_brand_ids)}\n")
        f.write(f"АЗС без топлива: {len(no_fuel_ids)}\n")
        f.write(f"АЗС с <3 видами топлива: {len(low_fuel_ids)}\n")
        f.write(f"АЗС без времени работы: {len(no_hours_ids)}\n")
        f.write(f"АЗС без кафе: {len(no_cafe_ids)}\n")
        f.write(f"АЗС без магазина: {len(no_shop_ids)}\n")
        f.write(f"АЗС без мойки: {len(no_wash_ids)}\n")
        f.write(f"АЗС с сайтом: {len(stations_with_website)}\n")
        f.write("=" * 80 + "\n")

    print(f"\nОтчёт сохранён в файл: {OUTPUT_REPORT}")

    # Выводим краткую сводку в консоль
    print("\n" + "=" * 60)
    print("КРАТКАЯ СВОДКА")
    print("=" * 60)
    print(f"Всего АЗС: {len(stations)}")
    print(f"Брендов: {len(brand_stats)}")
    print(f"АЗС без названия: {len(unknown_name_ids)}")
    print(f"АЗС без бренда: {len(unknown_brand_ids)}")
    print(f"АЗС без топлива: {len(no_fuel_ids)}")
    print(f"АЗС с <3 видами топлива: {len(low_fuel_ids)}")
    print(f"АЗС с топливом: {len(stations) - len(no_fuel_ids)}")
    print(f"АЗС с сайтом: {len(stations_with_website)}")
    print("=" * 60)


if __name__ == "__main__":
    analyze_stations()