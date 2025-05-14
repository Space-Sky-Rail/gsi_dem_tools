# get_elevation.py
# 指定された緯度・経度から標高を取得する関数

import json
from pathlib import Path
import rasterio

TIF_DIR = Path("output_tifs")
#INDEX_PATH = Path("dem_index.json")
INDEX_PATH = TIF_DIR / "dem_index.json"


# インデックス読み込み（モジュール初期化時に1回だけ）
with open(INDEX_PATH, "r", encoding="utf-8") as f:
    dem_index = json.load(f)

def get_elevation(lat: float, lon: float) -> float | None:
    for filename, bounds in dem_index.items():
        if bounds["min_lon"] <= lon <= bounds["max_lon"] and bounds["min_lat"] <= lat <= bounds["max_lat"]:
            tif_path = TIF_DIR / filename
            try:
                with rasterio.open(tif_path) as src:
                    col, row = src.index(lon, lat)
                    # row = src.height - row - 1
                    val = src.read(1)[row, col]
                    if val == src.nodata:
                        return None
                    return float(val)
            except Exception as e:
                print(f"[ERROR] 読み込み失敗: {filename} ({e})")
                return None
    return None

# テスト実行用（直接実行された場合）
if __name__ == "__main__":
    test_lat = 35.15118
    test_lon = 136.3915
    h = get_elevation(test_lat, test_lon)
    if h is not None:
        print(f"標高: {h:.2f} m")
    else:
        print("標高情報なし（範囲外または欠損）")
