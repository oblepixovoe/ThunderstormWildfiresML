import pandas as pd
from geopy.distance import geodesic
from datetime import datetime, timedelta
from scipy.spatial import KDTree

# 🔹 Загружаем файлы (укажи правильные пути к своим данным)
fires = pd.read_excel("fires.xls")  # Данные о пожарах
storms = pd.read_csv("grosy.csv")  # Данные о грозах

# 🔹 Приводим названия колонок к единому формату (если нужно)
fires.columns = fires.columns.str.lower().str.strip()
storms.columns = storms.columns.str.lower().str.strip()

# 🔹 Проверяем, какие колонки есть в файлах
print("Столбцы в файле с пожарами:", fires.columns)
print("Столбцы в файле с грозами:", storms.columns)

# 🔹 Приводим даты в нужный формат
fires["fire_date"] = pd.to_datetime(fires["дата первого наблюдения"])  # Укажи правильное название столбца
storms["storm_date"] = pd.to_datetime(storms["dt"])  # Аналогично, если dt — это дата грозы

# 🔹 Берём только нужные координаты
fire_coords = fires[["lat", "lon"]].values
storm_coords = storms[["lat", "lon"]].values

# 🔹 Создаём KDTree для быстрого поиска ближайшей грозы по координатам
storm_tree = KDTree(storm_coords)

# 🔹 Определяем максимальное расстояние и временной лаг для поиска гроз
max_distance_km = 50  # Максимальное расстояние между грозой и пожаром
max_time_diff = timedelta(days=5)  # Максимальный лаг между грозой и пожаром

# 🔹 Функция для поиска ближайшей грозы
def find_nearest_storm(fire_lat, fire_lon, fire_date):
    # Ищем ближайшую грозу по координатам
    dist, idx = storm_tree.query([fire_lat, fire_lon], k=1)
    
    # Берём координаты и дату ближайшей грозы
    nearest_storm = storms.iloc[idx]
    storm_date = nearest_storm["storm_date"]
    
    # Проверяем, подходит ли гроза по расстоянию и времени
    fire_point = (fire_lat, fire_lon)
    storm_point = (nearest_storm["lat"], nearest_storm["lon"])
    real_distance = geodesic(fire_point, storm_point).km  # Реальное расстояние
    
    if real_distance <= max_distance_km and abs(fire_date - storm_date) <= max_time_diff:
        return pd.Series([nearest_storm["storm_date"], nearest_storm["amplitude"], real_distance])
    else:
        return pd.Series([None, None, None])  # Если нет подходящей грозы, ставим NaN

# 🔹 Применяем функцию к каждому пожару
fires[["nearest_storm_date", "storm_amplitude", "distance_to_storm"]] = fires.apply(
    lambda row: find_nearest_storm(row["lat"], row["lon"], row["fire_date"]), axis=1
)

# 🔹 Сохраняем объединённые данные
fires.to_csv("fires_with_storms.csv", index=False)

print(fires.head())  # Проверяем результат
