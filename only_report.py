import json
import sys
from collections import defaultdict

def build_report(stations):
    brands = defaultdict(list)
    for s in stations:
        brands[s["brand"]].append(s)

    report = {
        "brand_count": {k: len(v) for k, v in brands.items()},
        "brand_stations": {k: [x["name"] for x in v] for k, v in brands.items()},
        "name_unknown": [s["id"] for s in stations if s["name"] == "unknown"],
        "brand_unknown": [s["id"] for s in stations if s["brand"] == "unknown"],
        "coords_missing": [s["id"] for s in stations if s["latitude"] is None],
        "no_fuels": [s["id"] for s in stations if len(s["fuelPrices"]) == 0],
        "few_fuels": [s["id"] for s in stations if 0 < len(s["fuelPrices"]) <= 3],
        "workingHours_unknown": [s["id"] for s in stations if s["workingHours"] == "unknown"],
        "hasCafe_unknown": [s["id"] for s in stations if s["hasCafe"] == "unknown"],
        "hasShop_unknown": [s["id"] for s in stations if s["hasShop"] == "unknown"],
        "hasWash_unknown": [s["id"] for s in stations if s["hasWash"] == "unknown"],
    }
    return report

def print_report(report):
    print("=== ОТЧЕТ ПО АЗС БЕЛАРУСИ ===")
    print(f"Всего станций: {sum(report['brand_count'].values())}")
    print("\nБренды:")
    for brand, count in sorted(report['brand_count'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {brand}: {count}")
    print(f"\nНет имени: {len(report['name_unknown'])}")
    print(f"Нет бренда: {len(report['brand_unknown'])}")
    print(f"Нет координат: {len(report['coords_missing'])}")
    print(f"Нет топлива: {len(report['no_fuels'])}")
    print(f"Мало топлива (1-3 вида): {len(report['few_fuels'])}")
    print(f"Нет часов работы: {len(report['workingHours_unknown'])}")
    print(f"Нет информации о кафе: {len(report['hasCafe_unknown'])}")
    print(f"Нет информации о магазине: {len(report['hasShop_unknown'])}")
    print(f"Нет информации о мойке: {len(report['hasWash_unknown'])}")

def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else "belarus_azs_merged.json"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            stations = json.load(f)
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")
        return
    except json.JSONDecodeError as e:
        print(f"Ошибка чтения JSON: {e}")
        return

    report = build_report(stations)
    print_report(report)

    # опционально сохранить отчет
    output_filename = "belarus_azs_analysis_report.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nПодробный отчет сохранен в {output_filename}")

if __name__ == "__main__":
    main()