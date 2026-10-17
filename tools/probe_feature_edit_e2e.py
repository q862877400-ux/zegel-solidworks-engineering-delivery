"""★ 真机验证 `sw_part.feature_delete`（★ 阶段 5 补的第二个 `改 × 特征` 能力）。

★★ 官方依据：★ `C:\\swapi\\types\\IModelDoc2\\EditDelete.md` 逐字
  「**void EditDelete()**」（★ 0 参、★ 无废弃）
  ★★ 它返回 `void` ⇒ ★★★ **判据只能是"特征树里它没了"**（★ 没有返回值可看）✓

★★★ 判据（★ 跑之前写死）：
  ① ★ 建件 ⇒ 记特征名列表
  ② ★ `feature_delete(doc, 特征名)` ⇒ ★★ **特征名列表里它消失** ⇒ **PASS**
  ③ ★ **负例**：★ 不存在的特征名 ⇒ ★ **必须抛错**（★ 事实 62：守卫要能被证伪）✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。
# 文件:   tools/probe_feature_edit_e2e.py
# 定位:   ★ 阶段 5：验证新增的 `sw_part.feature_delete`。
#   官方依据: `C:\\swapi\\types\\IModelDoc2\\EditDelete.md`
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

from scripts import sw_connect as C                                       # noqa: E402
from scripts import sw_part as P                                          # noqa: E402

OUT = REPO / "output" / "feature-edit-e2e-evidence.json"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def _try(fn, *a):
    try:
        r = fn(*a)
        return {"ok": True, "ret": repr(r)[:80]}
    except Exception as exc:                                              # noqa: BLE001
        return {"ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:170])}


def _names(doc) -> list:
    try:
        return [str(x) for x in (P.feature_names(doc) or [])]
    except Exception:                                                     # noqa: BLE001
        return []


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S")}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        _g(_g(doc, "SketchManager"), "CreateCornerRectangle", -0.02, -0.015, 0.0, 0.02, 0.015, 0.0)
        P.end_sketch(doc)
        nm = [n for n in (P.feature_names(doc) or []) if n.startswith("草图")]
        P.extrude_boss(doc, (nm[-1] if nm else "草图1"), 10.0)
        before = _names(doc)
        R["★_删除前特征"] = before
        target = next((n for n in before if ("拉伸" in n or "Extrude" in n or "凸台" in n)), None)
        R["目标"] = target

        #: ★ 正例
        R["feature_delete"] = _try(P.feature_delete, doc, target)
        after = _names(doc)
        R["★_删除后特征"] = after
        R["★_它消失了吗"] = ("★ 是（%r 已不在）" % target) if target not in after else "★★ 否（还在）"

        #: ★★ 负例（★ 事实 62）
        R["负例_不存在的特征"] = _try(P.feature_delete, doc, "这个特征不存在_xyz")
        R["★_负例抛错了吗"] = "★ 是 ✓" if not R["负例_不存在的特征"].get("ok") else "★★ 否（守卫没生效）"
    except Exception as exc:                                              # noqa: BLE001
        R["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:                                                 # noqa: BLE001
            pass
    R["★★_结论"] = ("★ PASS —— 特征被删掉了、★ 且负例被守卫拒绝"
                    if str(R.get("★_它消失了吗", "")).startswith("★ 是")
                    and str(R.get("★_负例抛错了吗", "")).startswith("★ 是")
                    else "★★ 需人工看")
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
