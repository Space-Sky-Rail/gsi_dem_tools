# dem2tif.py
# convert_all_dem.py と build_dem_index.py を Python で連続実行

import subprocess
import sys

python = sys.executable  # 現在の仮想環境の Python パス

print("=== DEM一括変換を開始します ===")
subprocess.run([python, "convert_all_dem.py"], check=True)

print("\n=== インデックス作成を開始します ===")
subprocess.run([python, "build_dem_index.py"], check=True)

print("\n✅ すべての処理が完了しました！")
