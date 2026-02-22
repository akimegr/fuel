import requests
import json
import time
import math
import random
from collections import defaultdict

# ========== НАСТРОЙКИ ==========
USE_GEOCODING = True               # можно выключить, если зависает
MAX_RETRIES = 1                     # для геокодирования достаточно одной попытки
NOMINATIM_TIMEOUT = 3               # таймаут запроса к Nominatim (сек)
NOMINATIM_DELAY = 0.5                # задержка между запросами (сек) - рискованно, но для ускорения
OVERPASS_DELAY = 5                   # задержка перед повтором Overpass
USER_AGENT = "azs-merger/1.0 (your@email.com)"
# ===============================

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"

OUTPUT_FILE = "belarus_azs_merged.json"
REPORT_FILE = "belarus_azs_report.json"

GEOCODE_CACHE = {}

FUEL_MAPPING = {
    "fuel:octane_92": "AI_92",
    "fuel:octane_95": "AI_95",
    "fuel:octane_98": "AI_98",
    "fuel:octane_100": "AI_100",
    "fuel:octane_76": "AI_76",
    "fuel:octane_80": "AI_80",
    "fuel:diesel": "DIESEL",
    "fuel:diesel:premium": "DIESEL_PREMIUM",
    "fuel:lpg": "PROPANE",
    "fuel:cng": "METHANE",
    "fuel:kerosene": "KEROSENE",
}

DAYS_TRANSLATION = {
    "Mo": "Пн",
    "Tu": "Вт",
    "We": "Ср",
    "Th": "Чт",
    "Fr": "Пт",
    "Sa": "Сб",
    "Su": "Вс",
}

def translate_days(text):
    if not text:
        return "unknown"
    if text.strip() == "24/7":
        return "24/7"
    for eng, ru in DAYS_TRANSLATION.items():
        text = text.replace(eng, ru)
    return text

def build_query():
    return """
    [out:json][timeout:300];
    area["ISO3166-1"="BY"][admin_level=2]->.searchArea;
    (
      node["amenity"="fuel"](area.searchArea);
      way["amenity"="fuel"](area.searchArea);
      relation["amenity"="fuel"](area.searchArea);
    );
    out center tags;
    """

def fetch_belarus_azs_with_retries():
    query = build_query()
    for attempt in range(1, 3):  # максимум 2 попытки для Overpass
        try:
            response = requests.post(
                OVERPASS_URL,
                data=query,
                headers={"User-Agent": USER_AGENT},
                timeout=120
            )
            response.raise_for_status()
            data = response.json()
            elements = data.get("elements", [])
            print(f"Получено элементов: {len(elements)}")
            return elements
        except Exception as e:
            print(f"Ошибка Overpass на попытке {attempt}: {e}")
            time.sleep(OVERPASS_DELAY)
    print("Не удалось получить данные от Overpass, завершение.")
    return []

def reverse_geocode_with_cache(lat, lon):
    if not USE_GEOCODING:
        return "unknown"

    key = (round(lat, 5), round(lon, 5))
    if key in GEOCODE_CACHE:
        return GEOCODE_CACHE[key]

    params = {
        "format": "json",
        "lat": lat,
        "lon": lon,
        "accept-language": "ru",
    }
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(
                NOMINATIM_URL,
                params=params,
                headers={"User-Agent": USER_AGENT},
                timeout=NOMINATIM_TIMEOUT
            )
            if r.status_code == 200:
                address = r.json().get("display_name", "unknown")
                GEOCODE_CACHE[key] = address
                return address
            elif r.status_code == 429:
                print(f"  Nominatim 429, попытка {attempt}")
            else:
                print(f"  Nominatim HTTP {r.status_code}, попытка {attempt}")
        except Exception as e:
            print(f"  Ошибка Nominatim: {e}")

        if attempt < MAX_RETRIES:
            time.sleep(1)   # короткая пауза между повторами

    GEOCODE_CACHE[key] = "unknown"
    return "unknown"

def extract_fuels(tags):
    fuels = {}
    for osm_key, our_key in FUEL_MAPPING.items():
        if tags.get(osm_key) == "yes":
            fuels[our_key] = "has"
    return fuels

def extract_yes_unknown(tags, key):
    return "yes" if key in tags else "unknown"

def build_station(element):
    tags = element.get("tags", {})

    lat = element.get("lat") or element.get("center", {}).get("lat")
    lon = element.get("lon") or element.get("center", {}).get("lon")

    name = tags.get("name") or tags.get("name:ru") or "unknown"
    brand = tags.get("brand") or "unknown"

    # Формируем адрес из тегов
    address_parts = []
    if tags.get("addr:street"):
        address_parts.append(tags["addr:street"])
    if tags.get("addr:housenumber"):
        address_parts.append(tags["addr:housenumber"])
    address = ", ".join(address_parts) if address_parts else ""

    # Геокодируем только если нет адреса в тегах и это разрешено
    need_geocode = (not address) and lat and lon and USE_GEOCODING
    if need_geocode:
        address = reverse_geocode_with_cache(lat, lon)
        if address != "unknown":
            time.sleep(NOMINATIM_DELAY)   # пауза только при успешном запросе

    return {
        "id": element["id"],
        "name": name,
        "brand": brand,
        "latitude": lat,
        "longitude": lon,
        "address": address or "unknown",
        "fuelPrices": extract_fuels(tags),
        "workingHours": translate_days(tags.get("opening_hours")),
        "hasCafe": extract_yes_unknown(tags, "cafe"),
        "hasShop": "yes" if tags.get("shop") else "unknown",
        "hasWash": "yes" if tags.get("car_wash") else "unknown",
        "phone": tags.get("contact:phone", "unknown"),
        "website": tags.get("contact:website", "unknown"),
        "city": tags.get("addr:city", "unknown"),
    }

def distance(a, b):
    if a["latitude"] is None or b["latitude"] is None:
        return float("inf")
    return math.sqrt((a["latitude"] - b["latitude"])**2 + (a["longitude"] - b["longitude"])**2)

def merge_duplicates(stations):
    merged = []
    used = set()
    for i, s1 in enumerate(stations):
        if i in used:
            continue
        duplicates = [s1]
        used.add(i)
        for j, s2 in enumerate(stations):
            if j in used:
                continue
            if distance(s1, s2) < 0.0005:
                duplicates.append(s2)
                used.add(j)
        merged_station = s1.copy()
        merged_station["fuelPrices"] = {}
        for d in duplicates:
            merged_station["fuelPrices"].update(d["fuelPrices"])
            if merged_station["name"] == "unknown" and d["name"] != "unknown":
                merged_station["name"] = d["name"]
            if merged_station["brand"] == "unknown" and d["brand"] != "unknown":
                merged_station["brand"] = d["brand"]
            if merged_station["workingHours"] == "unknown" and d["workingHours"] != "unknown":
                merged_station["workingHours"] = d["workingHours"]
            for field in ["hasCafe", "hasShop", "hasWash"]:
                if merged_station[field] == "unknown" and d[field] == "yes":
                    merged_station[field] = "yes"
        merged.append(merged_station)
    return merged

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

def main():
    print("Запрос всех АЗС на территории Беларуси...")
    elements = fetch_belarus_azs_with_retries()
    if not elements:
        print("Нет данных для обработки. Завершение.")
        return
    print(f"Всего получено элементов: {len(elements)}")

    print("Построение станций...")
    stations = []
    total = len(elements)
    geocode_count = 0

    for idx, e in enumerate(elements, 1):
        try:
            # Подсчёт потенциальных геокодирований (для информации)
            tags = e.get("tags", {})
            if USE_GEOCODING and not (tags.get("addr:street") or tags.get("addr:housenumber")) and (e.get("lat") or e.get("center")):
                geocode_count += 1

            station = build_station(e)
            stations.append(station)
        except Exception as ex:
            print(f"Ошибка при обработке элемента {e.get('id')}: {ex}")

        if idx % 50 == 0:
            print(f"  обработано {idx}/{total} элементов...", flush=True)

    print(f"Собрано станций до слияния: {len(stations)}")
    if USE_GEOCODING:
        print(f"Из них потребовали геокодирования (адрес отсутствовал в тегах): {geocode_count}")

    print("Слияние дубликатов...")
    stations = merge_duplicates(stations)

    print(f"Сохранение результата в {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(stations, f, ensure_ascii=False, indent=2)

    print("Построение отчёта...")
    report = build_report(stations)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("ГОТОВО")

if __name__ == "__main__":
    main()