"""★ 打开 SolidWorks 的**网格显示**（标准视图下的背景标尺）。

## 起源（业主建议，2026-10-26）

> 我记得 SolidWorks 自带的功能，可以让背景视图带这种标尺…正视图、侧视图、上视图
> 这种标准视图上面，背景会显示那种网格，包括尺寸的网格。这样你用视觉去检查的时候更容易。

## 官方取值（`_raw/enum_values_sldworks.txt` 出厂反射）

```
swUserPreferenceToggle_e.swGridDisplay        = 57
swUserPreferenceToggle_e.swGridDisplayDashed  = 58
swUserPreferenceDoubleValue_e.swGridMajorSpacing = 30
```

## 用法

```python
enable_grid(doc)                 # 打开网格（默认主格 10mm）
enable_grid(doc, major_mm=20)    # 主格 20mm
```

★ 它改的是**文档级**用户偏好（`IModelDoc2.SetUserPreferenceToggle`）⇒
  对当前文档生效；不写盘就不会污染后续文档（**本函数不 SaveAs**）。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / "scripts"))

#: 官方枚举取值的**唯一来源**：出厂反射转储
_SW_GRID_DISPLAY = 57
_SW_GRID_MAJOR_SPACING = 30


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（视觉取证辅助 · 网格显示）
# 文件:   tools/sw_grid.py
# 定位:   打开/关闭 SolidWorks 网格显示，给标准视图加背景标尺，便于**视觉**判距离。
#          起因：业主 2026-10-26 建议「标准视图上带网格，你用视觉检查更容易」。
# 官方依据: IModelDoc2::SetUserPreferenceToggle(int, bool) ·
#          swUserPreferenceToggle_e.swGridDisplay=57 / swGridDisplayDashed=58 ·
#          swUserPreferenceDoubleValue_e.swGridMajorSpacing=30
#          （取值来自 _raw/enum_values_sldworks.txt 出厂反射）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


def enable_grid(doc, *, major_mm: float = 10.0, dashed: bool = False) -> dict:
    """打开网格。回 `{"toggle": bool, "spacing": bool, "dashed": bool}`。

    ★ `major_mm` 用**毫米**（本仓对外一律毫米，见 AGENTS.md §十四之二），
      内部换算成**米**再交给 COM。
    """
    from sw_connect import try_call

    out = {}
    ok, _ = try_call(doc.SetUserPreferenceToggle, _SW_GRID_DISPLAY, True)
    out["toggle"] = bool(ok)
    ok, _ = try_call(doc.SetUserPreferenceToggle, _SW_GRID_DISPLAY, True)
    #: 主格间距（米）—— 官方 double 偏好
    ok2, _ = try_call(
        doc.SetUserPreferenceDoubleValue,
        _SW_GRID_MAJOR_SPACING,
        float(major_mm) / 1000.0,
    )
    out["spacing"] = bool(ok2)
    ok3, _ = try_call(doc.SetUserPreferenceToggle, 58, bool(dashed))
    out["dashed"] = bool(ok3)
    return out


def disable_grid(doc) -> bool:
    from sw_connect import try_call

    ok, _ = try_call(doc.SetUserPreferenceToggle, _SW_GRID_DISPLAY, False)
    return bool(ok)


def main() -> int:
    import sw_connect as c_
    from sw_connect import get_com_member

    conn = c_.connect_solidworks(wait_seconds=30)
    sw = conn[0] if isinstance(conn, tuple) else conn
    doc = c_.try_call(get_com_member, sw, "ActiveDoc")
    doc = doc[1] if isinstance(doc, tuple) else doc
    if doc is None:
        print("★ 没有打开的文档")
        return 1
    print("文档：%s" % (get_com_member(doc, "GetTitle") or ""))
    on = "--off" not in sys.argv
    if on:
        print("打开网格：%s" % enable_grid(doc))
        try:
            doc.GraphicsRedraw2()
        except Exception:  # noqa: BLE001
            pass
    else:
        print("关闭网格：%s" % disable_grid(doc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
