import os
import re

class GeoidModelISG2024:
    def __init__(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"ジオイドデータファイルが見つかりません: {filepath}")

        self.grid = []
        self.lat0 = None
        self.lon0 = None
        self.dlat = None
        self.dlon = None
        self.nrows = None
        self.ncols = None
        self.nodata = None

        # 正規表現で DMS を度に変換
        def dms_to_deg(dms_str):
            match = re.match(r"\s*(\d+)°(\d+)'(\d+)\"", dms_str)
            if not match:
                raise ValueError(f"DMS形式が不正です: {dms_str}")
            deg, min_, sec = map(int, match.groups())
            return deg + min_ / 60 + sec / 3600

        with open(filepath, encoding="utf-8") as f:
            in_head = True
            for line in f:
                line = line.strip()
                if in_head:
                    if line.startswith("lat min"):
                        self.lat0 = dms_to_deg(line.split("=")[1].strip())
                    elif line.startswith("lon min"):
                        self.lon0 = dms_to_deg(line.split("=")[1].strip())
                    elif line.startswith("delta lat"):
                        self.dlat = dms_to_deg(line.split("=")[1].strip())
                    elif line.startswith("delta lon"):
                        self.dlon = dms_to_deg(line.split("=")[1].strip())
                    elif line.startswith("nrows"):
                        self.nrows = int(line.split("=")[1].strip())
                    elif line.startswith("ncols"):
                        self.ncols = int(line.split("=")[1].strip())
                    elif line.startswith("nodata"):
                        self.nodata = float(line.split("=")[1].strip())
                    elif line.startswith("end_of_head"):
                        in_head = False
                else:
                    row = [float(x) for x in line.split()]
                    self.grid.append(row)
        self.grid.reverse()  # 緯度方向を南→北へ（grid[0]がlat_min）
        # デバッグ用
        print(f"lat0: {self.lat0}")
        print(f"lon0: {self.lon0}")
        print(f"dlat: {self.dlat}")
        print(f"dlon: {self.dlon}")
        print(f"nrows: {self.nrows}")
        print(f"ncols: {self.ncols}")


        if len(self.grid) != self.nrows:
            raise ValueError(f"データ行数が想定（{self.nrows}）と一致しません")
        if any(len(row) != self.ncols for row in self.grid):
            raise ValueError("データ列数が不一致な行があります")

        # 格子は北から南に並んでいるので、lat=lat0がgrid[0]
        # grid[y][x] = ジオイド高（m）

    def get_geoid_height(self, lat, lon):
        # 緯度・経度を格子インデックスに変換
        dy = (lat - self.lat0) / self.dlat
        dx = (lon - self.lon0) / self.dlon
        iy = int(dy)
        ix = int(dx)

        if iy < 0 or ix < 0 or iy + 1 >= self.nrows or ix + 1 >= self.ncols:
            print(f"[警告] 緯度経度がジオイド範囲外: ({lat}, {lon})")
            return None

        # 4点の値を取得
        z00 = self.grid[iy][ix]
        z01 = self.grid[iy][ix + 1]
        z10 = self.grid[iy + 1][ix]
        z11 = self.grid[iy + 1][ix + 1]

        if any(z == self.nodata for z in [z00, z01, z10, z11]):
            print(f"[警告] ジオイド高が欠損値です: ({lat}, {lon})")
            return None

        # バイリニア補間
        fy = dy - iy
        fx = dx - ix
        z = (
            (1 - fx) * (1 - fy) * z00 +
            fx * (1 - fy) * z01 +
            (1 - fx) * fy * z10 +
            fx * fy * z11
        )
        return z


if __name__ == "__main__":
    filepath = "JPGEO2024.isg"
    try:
        model = GeoidModelISG2024(filepath)
        lat = 34.785
        lon = 135.438
        h = model.get_geoid_height(lat, lon)
        if h is not None:
            print(f"ジオイド高 @ ({lat}, {lon}) = {h:.3f} m")
        else:
            print("ジオイド高が取得できませんでした。")
    except Exception as e:
        print(f"[エラー] {e}")
