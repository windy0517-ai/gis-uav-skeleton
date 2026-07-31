"""
┌─────────────────────────────────────────────────────┐
│  NDWI/SDWI 水体提取算法                             │
│                                                     │
│  🔴 这是 A 需要填算法实现的文件                      │
│                                                     │
│  功能：从 Sentinel-1 SAR 影像中提取洪水范围          │
│  输出：洪水范围 GeoJSON                              │
│                                                     │
│  参考原型：                                         │
│  - deepakpraja/floodmap（~50行，最简版本）           │
│  - Sentinel_1_python（SAR 预处理）                   │
└─────────────────────────────────────────────────────┘
"""
import numpy as np
import json

# ══════════════════════════════════════════════════════════
# 🔴 以下函数需要你实现
# ══════════════════════════════════════════════════════════

def extract_flood(sar_image_path: str) -> dict:
    """
    从 SAR 影像中提取洪水范围

    参数
    ----------
    sar_image_path : str
        Sentinel-1 SAR 影像路径（GeoTIFF，含 VV 和 VH 波段）

    返回
    -------
    dict : GeoJSON FeatureCollection
        {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {"area_km2": 12.5, "confidence": 0.87},
                "geometry": {"type": "Polygon", "coordinates": [...]}
            }]
        }

    实现步骤（参考 deepakpraja/floodmap）：
    =========================================
    第1步：用 rasterio 打开 GeoTIFF 文件
        import rasterio
        with rasterio.open(sar_image_path) as src:
            vv = src.read(1)  # VV 波段
            vh = src.read(2)  # VH 波段

    第2步：计算 SDWI 指数
        # SDWI = ln(10 × VV × VH) − 8
        # 注意：需要先将 DN 值转为 dB 单位（10 * log10）
        sdwi = np.log(10 * vv * vh) - 8

    第3步：用 Otsu 自动阈值分割
        from skimage.filters import threshold_otsu
        thresh = threshold_otsu(sdwi)
        flood_mask = sdwi > thresh

    第4步：形态学去噪
        from scipy import ndimage
        flood_mask = ndimage.binary_opening(flood_mask, iterations=2)

    第5步：轮廓转 GeoJSON
        import cv2
        from shapely.geometry import Polygon
        contours, _ = cv2.findContours(...)
        # → shapely Polygon → GeoJSON

    第6步：返回 GeoJSON FeatureCollection
    """
    # ── 🔴 在这里写你的代码 ──
    # from services.ndwi_extractor import extract_flood

    raise NotImplementedError("A 同学需要实现 extract_flood() 函数！参考上方步骤和 deepakpraja/floodmap")


def sdwi_index(vv_band: np.ndarray, vh_band: np.ndarray) -> np.ndarray:
    """
    计算 SDWI 指数（Sentinel-1 水体指数）

    SDWI = ln(10 × VV × VH) − 8

    参数需要是 dB 单位（先做 10*log10）
    """
    # ── 🔴 在这里写你的代码 ──
    # vv_db = 10 * np.log10(vv_band + 1e-10)
    # vh_db = 10 * np.log10(vh_band + 1e-10)
    # sdwi = np.log(10 * vv_db * vh_db + 1e-10) - 8
    # return sdwi
    raise NotImplementedError("A 同学需要实现 sdwi_index()！")


def mask_to_geojson(mask: np.ndarray, transform) -> dict:
    """
    将二值掩膜转为 GeoJSON

    参数
    ----------
    mask : np.ndarray
        二值掩膜（True=水体）
    transform : affine.Affine
        rasterio 读取的坐标变换信息

    返回
    -------
    dict : GeoJSON FeatureCollection
    """
    # ── 🔴 在这里写你的代码 ──
    # 1. cv2.findContours() 提取轮廓
    # 2. 将像素坐标转为地理坐标（用 transform）
    # 3. shapely Polygon → geojson.dump
    raise NotImplementedError("A 同学需要实现 mask_to_geojson()！")


# ══════════════════════════════════════════════════════════
# ✅ 测试：运行这个文件，验证你的实现
# ══════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 50)
    print("  水体提取算法测试")
    print("=" * 50)

    # 测试1：SDWI 指数计算
    test_vv = np.random.rand(100, 100) * 100
    test_vh = np.random.rand(100, 100) * 50

    try:
        result = sdwi_index(test_vv, test_vh)
        print(f"  ✅ SDWI 计算成功: shape={result.shape}")
    except NotImplementedError:
        print("  ❌ sdwi_index() 还没实现")

    # 测试2：整体流程
    import os
    test_image = "data/sar/guigang_s1.tif"
    if os.path.exists(test_image):
        try:
            geojson = extract_flood(test_image)
            print(f"  ✅ 水体提取成功: {json.dumps(geojson)[:100]}...")
        except NotImplementedError:
            print("  ❌ extract_flood() 还没实现")
    else:
        print(f"  ℹ️  测试影像不存在: {test_image}")
        print(f"  ℹ️  C 同学请下载数据放到 {test_image}")
