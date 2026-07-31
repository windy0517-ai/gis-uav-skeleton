"""
┌─────────────────────────────────────────────────────┐
│  OpenCV 颜色检测（替代 YOLO）                       │
│                                                     │
│  🔴 这是 A 需要填算法实现的文件                     │
│                                                     │
│  功能：从无人机航拍影像中检测特定颜色的目标           │
│  方法：HSV 颜色空间分割，不需要深度学习              │
│                                                     │
│  参考原型：                                         │
│  - zzhmx/HSV颜色检测（无人机竞赛项目）               │
│  - Krish-Bhalala/Color-Detection（零基础友好）       │
└─────────────────────────────────────────────────────┘
"""
import cv2
import numpy as np
import json

# ══════════════════════════════════════════════════════════
# 🔴 目标颜色HSV范围（需要根据你的航拍图调整）
# ══════════════════════════════════════════════════════════

TARGET_COLORS = {
    # 橙色救生衣/救援服
    "person": {
        "lower": np.array([5, 100, 100]),
        "upper": np.array([15, 255, 255]),
        "color": (0, 0, 255),  # BGR: 红色框
    },
    # 车辆（假设主要颜色为红/蓝/白）
    "vehicle": {
        "lower": np.array([100, 50, 50]),
        "upper": np.array([130, 255, 255]),
        "color": (0, 165, 255),  # BGR: 橙色框
    },
    # 建筑物（屋顶颜色，假设为灰/棕色）
    "building": {
        "lower": np.array([0, 0, 100]),
        "upper": np.array([30, 30, 200]),
        "color": (0, 255, 255),  # BGR: 黄色框
    },
}


def detect_by_color(image_path: str) -> dict:
    """
    通过颜色分割检测目标

    参数
    ----------
    image_path : str
        航拍影像路径

    返回
    -------
    dict : {"geojson": ..., "counts": {...}}

    实现步骤：
    =========
    第1步：读取图片
        img = cv2.imread(image_path)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    第2步：对每种目标颜色做分割
        mask = cv2.inRange(hsv, lower, upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, ...)

    第3步：过滤掉太小的区域（噪声）
        for cnt in contours:
            if cv2.contourArea(cnt) < min_area: continue

    第4步：绘制边界框 + 生成 GeoJSON
        x, y, w, h = cv2.boundingRect(cnt)
        center = (x + w/2, y + h/2)

    参考：Krish-Bhalala/Color-Detection 的 color_detection.py
    """
    raise NotImplementedError("A/B 同学需要实现 detect_by_color()！参考颜色检测开源项目")


def detect_by_haar(image_path: str) -> dict:
    """
    通过 Haar Cascade 检测行人和车辆（OpenCV 传统方法）

    不需要深度学习，使用 OpenCV 自带的预训练分类器

    参考：AadhavanAP/Vehicle-and-Pedestrian-Detection-using-OpenCV
    """
    raise NotImplementedError("如果需要检测行人和车辆，实现 detect_by_haar() 方法")


def adjust_hsv_threshold(image_path: str):
    """
    HSV 阈值调节工具（交互式）

    运行后会出现滑动条窗口，拖动调参找到最佳 HSV 范围
    按 's' 保存参数，按 'q' 退出

    参考：zzhmx/HSV颜色检测的 Fine_tuning_range.py
    """
    # ── 交互式调参 ──
    def nothing(x):
        pass

    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ 无法读取图片: {image_path}")
        return

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    cv2.namedWindow('调整HSV阈值')
    cv2.createTrackbar('H_min', '调整HSV阈值', 0, 179, nothing)
    cv2.createTrackbar('H_max', '调整HSV阈值', 179, 179, nothing)
    cv2.createTrackbar('S_min', '调整HSV阈值', 0, 255, nothing)
    cv2.createTrackbar('S_max', '调整HSV阈值', 255, 255, nothing)
    cv2.createTrackbar('V_min', '调整HSV阈值', 0, 255, nothing)
    cv2.createTrackbar('V_max', '调整HSV阈值', 255, 255, nothing)

    print('按 s 保存, 按 q 退出')

    while True:
        h_min = cv2.getTrackbarPos('H_min', '调整HSV阈值')
        h_max = cv2.getTrackbarPos('H_max', '调整HSV阈值')
        s_min = cv2.getTrackbarPos('S_min', '调整HSV阈值')
        s_max = cv2.getTrackbarPos('S_max', '调整HSV阈值')
        v_min = cv2.getTrackbarPos('V_min', '调整HSV阈值')
        v_max = cv2.getTrackbarPos('V_max', '调整HSV阈值')

        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])

        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(img, img, mask=mask)

        cv2.imshow('原图', img)
        cv2.imshow('掩膜', mask)
        cv2.imshow('结果', result)

        key = cv2.waitKey(1)
        if key == ord('s'):
            print(f"✅ 保存参数: HSV=[{h_min},{h_max}],[{s_min},{s_max}],[{v_min},{v_max}]")
        elif key == ord('q'):
            break

    cv2.destroyAllWindows()


# ══════════════════════════════════════════════════════════
# ✅ 测试
# ══════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 50)
    print("  颜色检测测试")
    print("=" * 50)
    print()
    print("  交互式调参: python services/color_detector.py --adjust 图片路径")
    print()
    print("  自动检测: python services/color_detector.py --detect 图片路径")
    print()

    import sys
    if len(sys.argv) > 2 and sys.argv[1] == '--adjust':
        adjust_hsv_threshold(sys.argv[2])
    elif len(sys.argv) > 2 and sys.argv[1] == '--detect':
        result = detect_by_color(sys.argv[2])
        print(f"检测结果: {json.dumps(result, indent=2)[:200]}")
