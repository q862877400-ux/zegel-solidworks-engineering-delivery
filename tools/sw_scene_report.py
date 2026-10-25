"""★ 场景报告：上色 + 三视图 + **人话描述**（人工验收阶段 2 的标准取证工具）。

## 一条命令做完取证

```
python -B tools/sw_scene_report.py                       # 当前活动装配
python -B tools/sw_scene_report.py --grid                # 顺便打开网格
python -B tools/sw_scene_report.py --prefix v2           # 截图命名前缀
```

输出：
1. 每个组件的**世界包围盒**（毫米）与中心
2. 组件之间的**相对位置**，按轴说人话（左右 / 上下 / 前后），
   并明确指出「这是高矮差别」还是「这是前后/左右差别」
3. 前 / 上 / 右三视图截图（`output/shots/<prefix>-*.png`）
4. 组件上色（蓝 / 粉 / 其余按序），便于视觉分辨

## 为什么要它存在（业主 2026-10-26）

我先前把 `+Z` 说成「抬高」，业主从屏幕上看到的是「一样高」。
根因不是嘴误，而是**没有工具把坐标翻成人话** ⇒ 本工具就是那个工具。
★ 以后向业主描述任何三维场景，**先跑它，再照着它的输出说**。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（场景报告 · 人工验收取证）
# 文件:   tools/sw_scene_report.py
# 定位:   上色 + 三视图 + 由包围盒**自动生成**的场景描述 —— 阶段 2 的标准取证工具。
#          以后向业主描述三维场景，先跑它再照着说，不再手推坐标。
# 官方依据: IComponent2::GetBox · IComponent2::SetMaterialPropertyValues2 ·
#          IModelDoc2::ShowNamedView2 · swStandardViews_e
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))
sys.path.insert(0, str(R / "tools"))

import sw_connect as c_  # noqa: E402
from sw_connect import get_com_member  # noqa: E402
from sw_scene import (  # noqa: E402
    AXIS_SCREEN,
    capture_views,
    color_components,
    component_boxes,
    describe_scene,
)

#: 默认配色：蓝、粉、绿、橙 —— 足够区分，且与背景对比强
DEFAULT_COLORS = (
    (0.15, 0.35, 0.90),
    (0.95, 0.45, 0.75),
    (0.20, 0.75, 0.35),
    (0.98, 0.65, 0.15),
)


def main() -> int:
    prefix = "scene"
    if "--prefix" in sys.argv:
        prefix = sys.argv[sys.argv.index("--prefix") + 1]

    conn = c_.connect_solidworks(wait_seconds=30)
    sw = conn[0] if isinstance(conn, tuple) else conn
    doc = c_.try_call(get_com_member, sw, "ActiveDoc")
    doc = doc[1] if isinstance(doc, tuple) else doc
    if doc is None:
        print("★ 没有打开的文档")
        return 1
    title = str(get_com_member(doc, "GetTitle") or "")
    dtype = int(get_com_member(doc, "GetType") or 0)
    print("文档：%s（类型 %d）" % (title, dtype))

    #: ① 上色
    comps = list(get_com_member(doc, "GetComponents", False) or ())
    if comps:
        res = color_components(doc, DEFAULT_COLORS)
        print("上色：%s" % res)

    #: ② 网格（可选）
    if "--grid" in sys.argv:
        from sw_grid import enable_grid

        print("网格：%s" % enable_grid(doc, major_mm=10.0))

    #: ③ 人话描述
    boxes = component_boxes(doc)
    print()
    print("── 轴语义（常量，见 scripts/sw_scene.py）──")
    for axis, (pos, neg) in AXIS_SCREEN.items():
        print("   %s+ = %s · %s- = %s" % (axis.upper(), pos, axis.upper(), neg))
    print()
    print("── 场景描述（由包围盒**自动生成**，不是我手写的）──")
    print(describe_scene(boxes))

    #: ④ 三视图
    shots = capture_views(doc, R / "output" / "shots", prefix)
    print()
    print("── 三视图截图 ──")
    for k, v in shots.items():
        print("   %s: %s" % (k, Path(v).name if v.startswith(str(R)) else v))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
