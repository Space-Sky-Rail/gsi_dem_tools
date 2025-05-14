from lxml import etree
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from pathlib import Path

# --- 入力と出力ファイルを指定 ---
xml_path = Path("FG-GML-5236-01-00-DEM5A-20231113.xml")  # GML (XML) ファイルパス
output_tif = Path("converted_dem5a.tif")  # 出力先の GeoTIFF

# --- XMLをパース ---
tree = etree.parse(str(xml_path))
root = tree.getroot()
ns = {"gml": "http://www.opengis.net/gml/3.2"}

# --- グリッドサイズを取得 ---
grid_env = root.find(".//gml:GridEnvelope", ns)
if grid_env is None:
    raise ValueError("GridEnvelope が見つかりません")
low = grid_env.find("gml:low", ns).text.split()
high = grid_env.find("gml:high", ns).text.split()
cols = int(high[0]) - int(low[0]) + 1
rows = int(high[1]) - int(low[1]) + 1

# --- 空間範囲を取得 ---
# --- 空間範囲を取得（ここが重要！！）---
envelope = root.find(".//gml:Envelope", ns)
lower_corner = list(map(float, envelope.find("gml:lowerCorner", ns).text.split()))
upper_corner = list(map(float, envelope.find("gml:upperCorner", ns).text.split()))

# GMLは lat lon の順なので、ここで逆にして代入
min_lat, min_lon = lower_corner
max_lat, max_lon = upper_corner

# --- 標高データを取得 ---
tuple_list_text = root.find(".//gml:tupleList", ns).text.strip()
elevations_flat = [float(line.split(",")[1]) for line in tuple_list_text.splitlines()]
elevations = np.array(elevations_flat).reshape((rows, cols))

# --- アフィン変換行列を計算 ---
transform = from_bounds(min_lon, min_lat, max_lon, max_lat, cols, rows)

# --- XMLパース処理の直後 ---
print(f"🔹 サイズ: {cols} × {rows}")
print(f"🔹 範囲: 緯度 {min_lat}〜{max_lat}, 経度 {min_lon}〜{max_lon}")
print(f"🔹 標高数: {len(elevations_flat)}")


# --- GeoTIFFとして保存 ---
with rasterio.open(
    output_tif,
    "w",
    driver="GTiff",
    height=rows,
    width=cols,
    count=1,
    dtype=elevations.dtype,
    crs="EPSG:6668",  # JGD2011（日本の測地系）
    transform=transform,
) as dst:
    dst.write(elevations, 1)

print("✅ GeoTIFF変換完了！→", output_tif)


# --- script for test ---
lat = 34.670  # 例
lon = 136.130

with rasterio.open("converted_dem5a.tif") as src:
    col, row = src.index(lon, lat)  # ← 順番超重要
    val = src.read(1)[row, col]
    print(f"標高: {val:.2f} m")