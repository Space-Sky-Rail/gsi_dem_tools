# get_elevation_bilinear.py
# 指定された緯度・経度から標高を取得する関数（バイリニア補間対応）

import json
from pathlib import Path
import rasterio
import numpy as np

TIF_DIR = Path("output_tifs")
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
                    band = src.read(1)[::-1, :]  # 縦横反転
                    # band = src.read(1)
                    transform = src.transform
                    inv_transform = ~transform
                    col_f, row_f = inv_transform * (lon, lat)  # 小数含むピクセル位置

                    # 周囲の整数座標
                    row0, col0 = int(np.floor(row_f)), int(np.floor(col_f))
                    row1, col1 = row0 + 1, col0 + 1

                    # 範囲チェック
                    if not (0 <= row0 < src.height - 1 and 0 <= col0 < src.width - 1):
                        return None

                    # 4点の標高値
                    z00 = band[row0, col0]
                    z01 = band[row0, col1]
                    z10 = band[row1, col0]
                    z11 = band[row1, col1]

                    # 欠損があれば無効
                    if any(z <= -1000 for z in [z00, z01, z10, z11]):
                        return None

                    # bilinear補間
                    dx, dy = col_f - col0, row_f - row0
                    z0 = z00 * (1 - dx) + z01 * dx
                    z1 = z10 * (1 - dx) + z11 * dx
                    z = z0 * (1 - dy) + z1 * dy

                    return float(z)

            except Exception as e:
                print(f"[ERROR] 読み込み失敗: {filename} ({e})")
                return None
    return None

# テスト実行用（直接実行された場合）
if __name__ == "__main__":
    # test_lat = 35.22037     # GSI: 810.0m
    # test_lon = 136.3534
    # test_lat = 35.103431    # GSI: 901.2m
    # test_lon = 136.340614
    # test_lat = 35.17146     # GSI: 1142.8m
    # test_lon = 136.44017
    # test_lat = 35.17704     # GSI: 1240.5m
    # test_lon = 136.41905
    # test_lat = 35.15118     # GSI: 973.1m
    # test_lon = 136.3915
    # test_lat = 35.138714    # GSI: 730.6m
    # test_lon = 136.30698
    # test_lat = 35.190958    # GSI: 81.6m
    # test_lon = 136.114972
    test_lat = 35.1786306   # GSI: 1221.2m
    test_lon = 136.4135444
    h = get_elevation(test_lat, test_lon)
    if h is not None:
        print(f"標高: {h:.2f} m")
    else:
        print("標高情報なし（範囲外または欠損）")
