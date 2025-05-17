# gsi_dem_tools

国土地理院が提供する「基盤地図情報 数値標高モデル（DEM5Aなど）」を活用して，
任意の緯度・経度から標高を取得し，可視化・解析するためのツール群をまとめたものです．

**詳細な使い方や解説は[こちら](https://skyrail.tech/archives/860)をご覧ください**

---

## 主な機能

- GML形式のDEMデータを GeoTIFF に変換（タイル単位で保存）
- 指定座標の標高をバイリニア補間で取得（高精度）
- DEMをヒートマップとして可視化（複数タイル合成対応）
- 全タイルのカバー範囲を事前にインデックス化し、高速アクセス

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
```

## 依存パッケージ
`requirements.txt`を参照してください

```pip install -r requirements.txt```

で自動的に入ります．

## 使用手順

1. **DEMデータを入手**  
   [国土地理院「基盤地図情報ダウンロードサービス](https://service.gsi.go.jp/kiban/)

   FG-GML-523600-DEM5A-20231113.zipのようなDEMデータファイルがダウンロードされる．

3. **ZIPファイルを `input_zips/` に配置**
   

4. **変換＋インデックス作成（初回のみ）**
   ```bash
   python dem2tif.py
