# plot_dem_overview.py (Cartopy版)
# DEMタイルを日本地図上にオーバーレイ表示（並べ替え不要）

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from pathlib import Path
import sys
import matplotlib.ticker as ticker
import platform
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# 日本語フォント対応（環境に応じて）
if platform.system() == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"
elif platform.system() == "Windows":
    plt.rcParams["font.family"] = "Yu Gothic"
else:
    plt.rcParams["font.family"] = "IPAexGothic"

plt.rcParams["axes.unicode_minus"] = False

TIF_DIR = Path("output_tifs")

# コマンドライン引数で枚数を指定（例: python plot_dem_overview.py 4）
try:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 0  # 0なら全タイル
except ValueError:
    print("引数は整数で指定してください")
    sys.exit(1)

# タイルを取得
def sort_key_by_geography(tif_path):
    with rasterio.open(tif_path) as src:
        bounds = src.bounds
        lat = bounds.top     # 北を優先
        lon = bounds.left    # 西を優先
        return (-lat, lon)   # 降順（北→南）、昇順（西→東）

tif_files = sorted(TIF_DIR.glob("*.tif"), key=sort_key_by_geography, reverse=False)
if n > 0:
    tif_files = tif_files[:n]

# 描画用キャンバス作成（Cartopy使用）
fig = plt.figure(figsize=(10, 12))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_title("DEMタイルを日本地図にオーバーレイ", fontsize=14)
ax.coastlines(resolution="10m")
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.LAND, facecolor='lightgray')
ax.gridlines(draw_labels=True)

# 全体の標高スケールを決定
vmin_global, vmax_global = float("inf"), float("-inf")
min_x, min_y = float("inf"), float("inf")
max_x, max_y = float("-inf"), float("-inf")
cmap = plt.get_cmap("terrain").copy()
cmap.set_bad(color="white")

tif_bounds = []
for tif_path in tif_files:
    with rasterio.open(tif_path) as src:
        nodata_val = src.nodata if src.nodata is not None else -9999
        data = src.read(1)
        masked = np.ma.masked_where((data <= -1000), data)
        if np.all(masked.mask):
            print(f"{tif_path.name} は全欠損のためスキップ")
            continue
        transform = src.transform
        width = src.width
        height = src.height
        left = transform.c
        top = transform.f
        right = left + width * transform.a
        bottom = top + height * transform.e
        extent = [left, right, bottom, top]
        vmin_global = min(vmin_global, masked.min())
        vmax_global = max(vmax_global, masked.max())
        min_x = min(min_x, extent[0])
        max_x = max(max_x, extent[1])
        min_y = min(min_y, extent[2])
        max_y = max(max_y, extent[3])
        tif_bounds.append((tif_path, masked, extent))

if not tif_bounds:
    print("有効なDEMタイルが見つかりませんでした。")
    sys.exit(1)

# 描画処理
import matplotlib.patches as mpatches
for tif_path, masked, extent in tif_bounds:
    ax.imshow(masked, extent=extent, transform=ccrs.PlateCarree(), origin="lower",
              cmap=cmap, interpolation="none", vmin=vmin_global, vmax=vmax_global)
    # タイル枠線を描画
    rect = mpatches.Rectangle((extent[0], extent[2]), extent[1]-extent[0], extent[3]-extent[2],
                              linewidth=0.3, edgecolor='black', facecolor='none', transform=ccrs.PlateCarree(), zorder=10)
    ax.add_patch(rect)

# 範囲調整
ax.set_extent([min_x, max_x, min_y, max_y], crs=ccrs.PlateCarree())

plt.colorbar(ax.images[-1], ax=ax, label="標高 [m]", orientation="vertical", shrink=0.6)
plt.tight_layout()
plt.show()
