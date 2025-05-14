# build_dem_index.py
# output_tifs ディレクトリ内のすべての .tif を走査し、緯度経度範囲を辞書化

from pathlib import Path
import rasterio
import json

TIF_DIR = Path("output_tifs")
#INDEX_PATH = Path("dem_index.json")
INDEX_PATH = TIF_DIR / "dem_index.json"

def build_index():
    index = {}
    for tif_path in TIF_DIR.glob("*.tif"):
        try:
            with rasterio.open(tif_path) as src:
                bounds = src.bounds
                index[tif_path.name] = {
                    "min_lon": bounds.left,
                    "min_lat": bounds.bottom,
                    "max_lon": bounds.right,
                    "max_lat": bounds.top
                }
                print(f"[INDEXED] {tif_path.name}")
        except Exception as e:
            print(f"[ERROR] Failed to read {tif_path.name}: {e}")

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"\n✅ インデックスファイル出力完了: {INDEX_PATH}")

if __name__ == "__main__":
    build_index()
