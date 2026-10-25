"""★ 场景描述：把装配体的三维关系翻译成**人能核对的话**（不再靠我手推坐标）。

## 为什么要有这个模块（业主 2026-10-26 指令）

> 不管是任何状态下，你通过视觉检查出来的错误，不能够打个补丁就了事儿，
> 你要从根本上去修复问题。…你要从工具层面、根本的层面去解决问题。

当时的错误：

```
我把 add_component(z_m=0.050) 说成「把上面那块抬高 50mm」
业主看屏：「它只是往右错开了一点，并没有高出一截」
```

**根因不是「说错了」，是「没有任何工具把坐标翻译成人话」** ——
我拿 `Transform2` 的三个数字自己脑补成空间关系，而**轴方向我根本没核**。

⇒ 本模块把这件事收进代码：
- 轴语义是**常量 + 有测试钉住**的（不靠我记）
- 关系描述由 `describe_scene()` **生成**，我不再手写
- 任何要我向业主描述场景的地方，都应当先跑它

## 轴语义（实测 + 官方视图枚举，**不是猜的**）

SolidWorks 默认前视（`swStandardViews_e.swFrontView = 1`）沿 **−Z** 看：

| 轴 | 屏幕上 | 依据 |
|---|---|---|
| **X** | 右 / 左 | 前视截图里 X −50…50 正好是左右 |
| **Y** | **上 / 下** | 两个组件 Y 相同 ⇒ 前视图里**一样高**（实测） |
| **Z** | 前 / 后 | Z 差 50mm 在前视图里**看不出高**，只在上视图里表现为纵向偏移 |

★★ **「抬高」= +Y，不是 +Z。** 这是本轮错误的直接原因。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（场景描述 · 视觉取证）
# 文件:   scripts/sw_scene.py
# 定位:   读装配体的**世界包围盒**，生成「谁在谁的哪一侧、相距多少」的中文描述，
#          并按前/上/右三视图截图。起因：业主指出我把 +Z 说成「抬高」。
# 官方依据: IComponent2::GetBox(IncludeRefPlanes, IncludeSketches)（回两对角，米）·
#          swStandardViews_e（swFrontView=1 / swTopView=5 / swRightView=4）·
#          IModelDoc2::ShowNamedView2
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

#: ★★★ 轴 → 屏幕方向。**这是常量，不是每次现推。**
AXIS_SCREEN = {
    "x": ("右", "左"),      #: 正值 = 屏幕右
    "y": ("上", "下"),      #: 正值 = 屏幕上  ← ★「抬高」就是这个
    "z": ("前", "后"),      #: 正值 = 朝观察者
}

#: 轴的中文名（描述里用）
AXIS_NAME = {"x": "X（左右）", "y": "Y（上下）", "z": "Z（前后）"}


def component_boxes(doc) -> list:
    """回 `[{name, lo, hi, center, size}]`，单位**毫米**。

    ★ 用的是 `IComponent2.GetBox`（官方：回包围盒的下角与上角，单位米）。
    """
    from sw_connect import get_com_member, try_call

    out = []
    for cp in list(get_com_member(doc, "GetComponents", False) or ()):
        ok, arr = try_call(cp.GetBox, False, False)
        if not ok or arr is None:
            continue
        v = [float(x) * 1000.0 for x in list(arr)[:6]]
        if len(v) < 6:
            continue
        lo = (v[0], v[1], v[2])
        hi = (v[3], v[4], v[5])
        out.append(
            {
                "name": str(get_com_member(cp, "Name2") or ""),
                "lo": lo,
                "hi": hi,
                "center": tuple(round((lo[i] + hi[i]) / 2.0, 1) for i in range(3)),
                "size": tuple(round(hi[i] - lo[i], 1) for i in range(3)),
            }
        )
    return out


def relation_text(a: dict, b: dict, *, tol_mm: float = 0.5) -> str:
    """描述 `b` 相对 `a` 的位置关系（中文，按轴）。

    ★ 只说**实测**的东西：
      · 分离（某轴间隙 > tol）⇒「b 在 a 的<方向> <距离>mm」
      · 重叠（某轴区间相交）⇒「b 与 a 在<轴>上重叠」
    """
    parts = []
    for idx, axis in enumerate(("x", "y", "z")):
        gap_pos = b["lo"][idx] - a["hi"][idx]   #: b 在 a 正方向外侧的距离
        gap_neg = a["lo"][idx] - b["hi"][idx]   #: b 在 a 负方向外侧的距离
        pos_word, neg_word = AXIS_SCREEN[axis]
        if gap_pos > tol_mm:
            parts.append("在 %s 方向 %s %.1fmm" % (AXIS_NAME[axis], pos_word, gap_pos))
        elif gap_neg > tol_mm:
            parts.append("在 %s 方向 %s %.1fmm" % (AXIS_NAME[axis], neg_word, gap_neg))
        else:
            parts.append("在 %s 上与它重叠" % AXIS_NAME[axis])
    return "、".join(parts)


def describe_scene(boxes: list) -> str:
    """整场景的人话描述（逐对给关系 + 一句总述）。

    ★ 总述用**最大分离轴**判方向，避免把「左右错开」说成「抬高」。
    """
    if not boxes:
        return "（没有组件）"
    lines = []
    for b in boxes:
        lines.append(
            "组件 %-18s 中心 (%.1f, %.1f, %.1f) mm · 尺寸 %.1f×%.1f×%.1f mm"
            % (
                b["name"],
                b["center"][0], b["center"][1], b["center"][2],
                b["size"][0], b["size"][1], b["size"][2],
            )
        )
    if len(boxes) >= 2:
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a, b = boxes[i], boxes[j]
                lines.append(
                    "%s 相对 %s：%s" % (b["name"], a["name"], relation_text(a, b))
                )
                #: 总述：取分离量最大的轴
                best = None
                for idx, axis in enumerate(("x", "y", "z")):
                    gp = b["lo"][idx] - a["hi"][idx]
                    gn = a["lo"][idx] - b["hi"][idx]
                    gap, sign = (gp, 1) if gp > gn else (gn, -1)
                    if best is None or gap > best[0]:
                        best = (gap, axis, sign)
                if best and best[0] > 0.5:
                    gap, axis, sign = best
                    word = AXIS_SCREEN[axis][0 if sign > 0 else 1]
                    lines.append(
                        "  ⇒ 主要分离：**%s**，%s 在 %s 的%s方 %.1fmm"
                        % (AXIS_NAME[axis], b["name"], a["name"], word, gap)
                    )
                    if axis == "y":
                        lines.append("  ⇒ 这确实是**高/低**的差别（Y 是竖直方向）")
                    elif axis == "z":
                        lines.append(
                            "  ⇒ 这是**前后（深度）**的差别，**不是高**"
                            "（前视图里看不出高矮）"
                        )
                    else:
                        lines.append("  ⇒ 这是**左右**的差别，**不是高**")
    return "\n".join(lines)


def capture_views(doc, out_dir: Path, prefix: str) -> dict:
    """按前/上/右三视图各截一张。回 `{视图名: 文件路径}`。"""
    import time

    from sw_connect import try_call

    sys.path.insert(0, str(R / "tools"))
    from sw_screenshot import capture, find_sw_window

    out_dir.mkdir(parents=True, exist_ok=True)
    hwnd = find_sw_window()
    out = {}
    for label, view in (("前视", "*前视"), ("上视", "*上视"), ("右视", "*右视")):
        try_call(doc.ShowNamedView2, view, 7)
        try_call(doc.ViewZoomtofit2)
        time.sleep(0.8)
        path = out_dir / ("%s-%s.png" % (prefix, label))
        ok, w, h, err = capture(hwnd, path)
        out[label] = str(path) if ok else "失败：%s" % err
    return out


def color_components(doc, colors) -> list:
    """给各组件上色。`colors` 是 `[(r,g,b), …]`（0..1）。回每项是否成功。"""
    import pythoncom
    from sw_connect import get_com_member, try_call
    from win32com.client import VARIANT

    res = []
    comps = list(get_com_member(doc, "GetComponents", False) or ())
    for cp, rgb in zip(comps, colors):
        vals = [
            float(rgb[0]), float(rgb[1]), float(rgb[2]),
            1.0, 1.0, 0.5, 0.5, 0.0, 0.0,
        ]
        ok, _ = try_call(
            cp.SetMaterialPropertyValues2,
            VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, vals),
            1,
            VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_BSTR, []),
        )
        res.append(bool(ok))
    return res
