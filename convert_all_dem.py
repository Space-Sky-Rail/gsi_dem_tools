# convert_all_dem5a.py
# 一括変換スクリプト: zip内のDEM5A GMLファイルを読み取り、GeoTIFFに変換

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import rasterio
from rasterio.transform import from_bounds
import shutil
from datetime import datetime

INPUT_DIR = Path("input_zips")      # zipファイルを入れるフォルダ
OUTPUT_DIR = Path("output_tifs")    # 変換後の.tifを保存するフォルダ
temp_dir = Path("temp_extracted")   # 一時解凍先
LOG_PATH = OUTPUT_DIR / "convert_log.txt"  # ログファイルパス（出力フォルダ内）

OUTPUT_DIR.mkdir(exist_ok=True)
temp_dir.mkdir(exist_ok=True)

with open(LOG_PATH, "a", encoding="utf-8") as log_file:

    def log(msg):
        print(msg)
        log_file.write(f"{datetime.now().isoformat()} {msg}\n")

    def convert_single_gml_to_tif(xml_path: Path, out_path: Path):
        ns = {"gml": "http://www.opengis.net/gml/3.2"}
        tree = ET.parse(xml_path)
        root = tree.getroot()

        grid_env = root.find(".//gml:GridEnvelope", ns)
        low = grid_env.find("gml:low", ns).text.split()
        high = grid_env.find("gml:high", ns).text.split()
        cols = int(high[0]) - int(low[0]) + 1
        rows = int(high[1]) - int(low[1]) + 1

        envelope = root.find(".//gml:Envelope", ns)
        lower_corner = list(map(float, envelope.find("gml:lowerCorner", ns).text.split()))
        upper_corner = list(map(float, envelope.find("gml:upperCorner", ns).text.split()))
        min_lat, min_lon = lower_corner
        max_lat, max_lon = upper_corner

        tuple_list_text = root.find(".//gml:tupleList", ns).text.strip()
        elevations_flat = [float(line.split(",")[1]) for line in tuple_list_text.splitlines()]

        expected = rows * cols
        actual = len(elevations_flat)
        if actual < expected:
            log(f"[WARN] {xml_path.name}: データ数が不足しています ({actual} < {expected})。-9999で補完します。")
            elevations_flat += [-9999.] * (expected - actual)
        elif actual > expected:
            log(f"[WARN] {xml_path.name}: データ数が超過しています ({actual} > {expected})。カットします。")
            elevations_flat = elevations_flat[:expected]

        elevations = np.array(elevations_flat).reshape((rows, cols))
        elevations = elevations[::-1, :]  # 上下反転（北→南の順に）
        transform = from_bounds(min_lon, min_lat, max_lon, max_lat, cols, rows)

        with rasterio.open(
            out_path,
            "w",
            driver="GTiff",
            height=rows,
            width=cols,
            count=1,
            dtype=elevations.dtype,
            crs="EPSG:6668",
            transform=transform,
            nodata=-9999.0
        ) as dst:
            dst.write(elevations, 1)

    zip_files = list(INPUT_DIR.glob("*.zip"))
    num_zips = len(zip_files)

    for zip_idx, zip_path in enumerate(zip_files, 1):
        log(f"[ZIP {zip_idx}/{num_zips}] Extracting {zip_path.name}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        xml_files = list(temp_dir.glob("*.xml"))
        num_xmls = len(xml_files)

        for xml_idx, xml_path in enumerate(xml_files, 1):
            base = "-".join(xml_path.stem.split("-")[:-1])
            out_path = OUTPUT_DIR / f"{base}.tif"

            if out_path.exists():
                log(f"[SKIP] {out_path.name} already exists")
                continue

            try:
                log(f"[CONVERT {zip_idx}/{num_zips}, {xml_idx}/{num_xmls}] {xml_path.name} -> {out_path.name}")
                convert_single_gml_to_tif(xml_path, out_path)
            except Exception as e:
                log(f"[ERROR] Failed to convert {xml_path.name}: {e}")

        shutil.rmtree(temp_dir)
        temp_dir.mkdir()
