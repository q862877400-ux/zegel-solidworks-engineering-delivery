"""★ 真机验证 `ISketch.AutoDimension2` → `ISketchManager.FullyDefineSketch`。

★★ 官方依据（三源里的 `c:\\swapi`）：
  · `types/ISketch/AutoDimension2.md` 逐字：
    「**Obsolete. Superseded by [[ISketchManager::FullyDefineSketch]].**」
    ★ 而 `types/ISketchManager/AutoDimension2.md` —— ★★ **官方页**不存在****
    （★ 我们调的 `active` 是**活动草图** ⇒ `ISketch` ⇒ ★ **所以这条命中是真的**）✓
  · `types/ISketchManager/FullyDefineSketch.md` —— ★ **11 参**，`## Parameters` 逐字：
    ```
    EntitiesToFullyDefine : bool   ← True = 全部实体
    UseRelations          : bool   ← True = 用几何关系
    RelationsToApply      : int    ← swSketchFullyDefineRelationType_e
    UseDimensions         : bool
    HorizontalDimScheme   : int    ← 0=Chain · 1=Baseline · 2=Ordinate
    HorizontalDatumDisp   : object ← 基准；Nothing/null ⇒ 用实体
    VerticalDimScheme     : int
    VerticalDatumDisp     : object
    HorizontalDimPlacement: int    ← 0=Above · 1=Below
    VerticalDimPlacement  : int    ← 0=Right · …
    （第 11 参见官方页）
    ```
    ★★ 官方那句描述逐字：「**Fully defines a sketch.**」⇒
      ★ 与本仓调用它的**意图**（docstring 逐字「为当前草图创建**真实模型尺寸**」）一致 ✓

★★★ 判据（★ 跑之前写死）：★ **草图里出现尺寸**（★ `ISketch` 的尺寸数 > 0）才算"建成"
  —— ★ 只回状态码不算（★ 事实 40 那一族）✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。
# 文件:   tools/probe_autodimension_successor.py
# 定位:   ★ 阶段 2：`scripts/sw_part.py::sketch_auto_dimension` 的 `ISketch.AutoDimens
#           ion2`。
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts import sw_connect as c  # noqa: E402
from scripts import sw_part as p  # noqa: E402
from scripts.sw_connect import create_empty_dispatch_variant as _empty  # noqa: E402

OUT = REPO / "output" / "autodimension-successor-evidence.json"


def _g(o, n, *a):
    return c.get_com_member(o, n, *a)


def _try(fn, *a):
    try:
        return {"ok": True, "ret": repr(fn(*a))[:100]}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:180])}


def _dim_count(sketch) -> int:
    """★ 草图的尺寸数（★ 那才是"真加了尺寸"的判据）。"""
    for nm in ("GetDimensionCount", "GetDisplayDimensionCount"):
        try:
            return int(_g(sketch, nm) or 0)
        except Exception:  # noqa: BLE001
            continue
    try:
        n = 0
        dd = _g(sketch, "GetFirstDisplayDimension")
        while dd is not None and n < 200:
            n += 1
            dd = _g(sketch, "GetNextDisplayDimension", dd)
        return n
    except Exception:  # noqa: BLE001
        return -1


def main() -> int:
    started = time.time()
    r: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S")}
    sw, _ = c.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = c.new_document(sw, "part")
        p.start_sketch(doc, plane_name="Front Plane")
        _g(
            _g(doc, "SketchManager"),
            "CreateCornerRectangle",
            -0.04,
            -0.03,
            0.0,
            0.04,
            0.03,
            0.0,
        )
        sketch = _g(_g(doc, "SketchManager"), "ActiveSketch")
        r["草图"] = repr(sketch)[:70]
        r["★_基线尺寸数"] = _dim_count(sketch)

        #: ★★ 旧入口（★ 与我们生产代码**逐字相同的 5 参**）
        r["旧_AutoDimension2(1, 1, -1, 1, -1)"] = _try(
            _g, sketch, "AutoDimension2", 1, 1, -1, 1, -1
        )
        r["★_旧后尺寸数"] = _dim_count(sketch)

        #: ★★ 新入口 `FullyDefineSketch`（★ 11 参，★ 照官方 `## Parameters` 的语义填）
        sm = _g(doc, "SketchManager")
        r["新_FullyDefineSketch(11 参)"] = _try(
            _g,
            sm,
            "FullyDefineSketch",
            True,  # EntitiesToFullyDefine
            True,  # UseRelations
            -1,  # RelationsToApply（★ -1 = 官方示例里的"全部"）
            True,  # UseDimensions
            1,  # HorizontalDimScheme = 1 Baseline
            _empty(),  # HorizontalDatumDisp（★ 事实 33：pywin32 下传裸 None 报类型不匹配）
            1,  # VerticalDimScheme
            _empty(),  # VerticalDatumDisp
            0,  # HorizontalDimPlacement = Above
            0,  # VerticalDimPlacement = Right
            _empty(),
        )  # 第 11 参
        r["★_新后尺寸数"] = _dim_count(sketch)
        p.end_sketch(doc)
    except Exception as exc:  # noqa: BLE001
        r["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:  # noqa: BLE001
            pass
    b = r.get("★_基线尺寸数")
    o = r.get("★_旧后尺寸数")
    n = r.get("★_新后尺寸数")
    r["★_旧加了尺寸吗"] = (
        "★ 是" if isinstance(o, int) and isinstance(b, int) and o > b else "★★ 否"
    )
    r["★_新加了尺寸吗"] = (
        "★ 是" if isinstance(n, int) and isinstance(b, int) and n > b else "★★ 否"
    )
    r["★★_结论"] = (
        "★ 旧的加上了 ⇒ 按判据**没有换的必要**"
        if r["★_旧加了尺寸吗"].startswith("★ 是")
        else "★★ 旧的没加上 ⇒ 值得试新入口"
    )
    r["seconds"] = round(time.time() - started, 2)
    OUT.write_text(
        json.dumps(r, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
