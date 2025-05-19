# gsi_tools

国土地理院が提供する「基盤地図情報 数値標高モデル（DEM5Aなど）」を活用して，
- 数値標高モデル（DEM5Aなど）を用いて，任意の緯度・経度から標高を取得し，可視化・解析するためのツール群
- ジオイドモデル「ジオイド2024日本とその周辺（JPGEO2024）」を用いて，任意の緯度・経度からジオイド高を取得するツール
をまとめたものです．

**数値標高モデルの活用について，詳細な使い方や解説は[こちら](https://skyrail.tech/archives/860)をご覧ください**
**ジオイドモデルの活用について，詳細な使い方や解説は[こちら](https://skyrail.tech/archives/964)をご覧ください**

---

## 主な機能
### 数値標高モデルについて
- GML形式のDEMデータを GeoTIFF に変換（タイル単位で保存）
- 指定座標の標高をバイリニア補間で取得（高精度）
- DEMをヒートマップとして可視化（複数タイル合成対応）
- 全タイルのカバー範囲を事前にインデックス化し、高速アクセス

### ジオイドモデルについて
- 任意の緯度・経度からジオイド高を取得する

---

## 構成
```
├── convert_all_dem.py # zip内のGMLをすべてGeoTIFFに変換
├── build_dem_index.py # 全タイルの緯度経度範囲をJSONに記録
├── get_elevation.py # 座標から標高を取得する関数（バイリニア補間）
├── plot_dem_overview.py # GeoTIFFをまとめて表示（タイル境界・色分布あり）
├── dem2tif.py # 変換+インデックス作成を一括実行するラッパー
├── output_tifs/ # 変換されたGeoTIFFファイル（標高タイル）が格納されるディレクトリ
├── input_zips/ # 国土地理院からDLしたDEM5Aのzipファイルを格納するディレクトリ
└── dem_index.json # タイルごとの地理範囲インデックス
└── geoid_tools/
        └──  geoid_height.py # 座標からジオイド高を計算する
```

## 依存パッケージ
`requirements.txt`を参照してください

```pip install -r requirements.txt```

で自動的に入ります．

## 使用手順（数値標高モデル）

1. **DEMデータを入手**  
   [国土地理院「基盤地図情報ダウンロードサービス](https://service.gsi.go.jp/kiban/)

   FG-GML-523600-DEM5A-20231113.zipのようなDEMデータファイルがダウンロードされる．

3. **ZIPファイルを `input_zips/` に配置**
   

4. **変換＋インデックス作成（初回のみ）**
   ```bash
   python dem2tif.py

## 使用手順（ジオイドモデル）

1. **DEMデータを入手**  
   [国土地理院「基盤地図情報ダウンロードサービス](https://service.gsi.go.jp/kiban/)


3. **JPGEO2024.isgを`geoid_tools`に配置**
   

4. **実行してみる**
   ```bash
   python geoid_height.py

