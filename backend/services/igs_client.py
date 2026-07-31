"""
┌─────────────────────────────────────────────────────┐
│  MapGIS IGServer 客户端                              │
│                                                     │
│  🔴 这是 C 需要配置的文件                            │
│                                                     │
│  功能：通过 REST API 调用 MapGIS 的分析功能          │
│  核心：flowID 600227 叠置分析                        │
│                                                     │
│  参考：                                             │
│  - CSDN《IGServer 叠加分析实践》四部曲               │
│  - MapGIS/WebClient-JavaScript WorkFlowServer.js     │
└─────────────────────────────────────────────────────┘
"""
import requests
import json

# ══════════════════════════════════════════════════════════
# 🔴 IGServer 配置（C 同学填自己的地址和端口）
# ══════════════════════════════════════════════════════════

IGS_CONFIG = {
    "host": "localhost",         # IGServer 地址
    "port": 6163,                # 默认端口
    "protocol": "http",
}

# ══════════════════════════════════════════════════════════
# 工具函数
# ══════════════════════════════════════════════════════════

def _base_url() -> str:
    return f"{IGS_CONFIG['protocol']}://{IGS_CONFIG['host']}:{IGS_CONFIG['port']}/igs/rest"


def check_connection() -> bool:
    """
    检测 IGServer 连接

    🔴 C 同学：运行这个函数验证 MapGIS 是否安装正确

    >>> check_connection()
    ✅ IGServer 连接成功！
    """
    try:
        url = f"{_base_url()}/mrfws/workflows"
        resp = requests.get(url, params={"f": "json"}, timeout=5)
        if resp.status_code == 200:
            print("✅ IGServer 连接成功！")
            print(f"   可用工作流数量: {len(resp.json().get('workflows', []))}")
            return True
        else:
            print(f"❌ IGServer 返回错误: {resp.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接 IGServer")
        print("   请确认：")
        print("   1. MapGIS IGServer 已启动")
        print(f"   2. {_base_url()} 可以访问")
        print("   3. 防火墙没有阻挡 6163 端口")
        return False


def list_workflows() -> list:
    """
    获取 IGServer 所有可用的分析工作流

    🔴 C 同学：运行这个，看 MapGIS 提供了哪些分析功能
    """
    url = f"{_base_url()}/mrfws/workflows"
    resp = requests.get(url, params={"f": "json"})
    data = resp.json()
    return data.get("workflows", [])


def overlay_layers(layer1_gdbp: str, layer2_gdbp: str,
                   over_type: int = 1, result_gdbp: str = None) -> dict:
    """
    矢量叠置分析 — flowID 600227

    参数
    ----------
    layer1_gdbp : str
        图层1 的 GDB 路径（如 "gdbp://MapGisLocal/floods/flood_extent"）
    layer2_gdbp : str
        图层2 的 GDB 路径
    over_type : int
        叠置类型：1=求交, 2=求并, 3=求差, ...
    result_gdbp : str
        结果图层路径

    返回
    -------
    dict : IGServer 的 JSON 响应

    🔴 C 同学：参考 CSDN 教程配置具体参数
    """
    raise NotImplementedError("C 同学需要配置 IGServer 连接并实现 overlay_layers()！")
    # ── 参考实现（CSDN 叠加分析实践四部曲） ──
    # url = f"{_base_url()}/mrfws/execute/600227"
    # para = f"srcInfo1:{layer1_gdbp};srcInfo2:{layer2_gdbp};overType:{over_type};desInfo:{result_gdbp};radius:0"
    # resp = requests.post(url, params={"f": "json"}, data={"paraValues": para})
    # return resp.json()


# ══════════════════════════════════════════════════════════
# ✅ 测试
# ══════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 50)
    print("  MapGIS IGServer 连接测试")
    print("=" * 50)
    print()
    print("  请先确认 MapGIS IGServer 已安装并启动")
    print()

    # 测试连接
    check_connection()
    print()

    # 列出可用工作流
    try:
        workflows = list_workflows()
        print(f"  发现 {len(workflows)} 个可用工作流:")
        for w in workflows[:5]:
            print(f"    - {w.get('flowID', '?')}: {w.get('flowName', '?')}")
    except Exception as e:
        print(f"  ⚠️ 获取工作流列表失败: {e}")
