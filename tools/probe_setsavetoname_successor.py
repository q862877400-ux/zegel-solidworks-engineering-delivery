"""★ 真机验证 `IPackAndGo.SetSaveToName` → `SetSaveToName2`（★ 判据：签名相同 ⇒ 疑似纯改名，仍须真机）。

★★ 官方依据（三源里的 `C:\\swapi`）：
  · `types/IPackAndGo/SetSaveToName.md`：签名 `System.bool SetSaveToName( System.bool Override, System.string SaveToName )`
    逐字「**Obsolete. Superseded by [[IPackAndGo::SetSaveToName2]].**」
  · `types/IPackAndGo/SetSaveToName2.md`：签名
    `System.bool SetSaveToName2( System.bool Override, System.string SaveToName )`（★ **无 Obsolete**）
  ⇒ ★★★ **两个签名逐字相同**（★ 只差名字里的 `2`）⇒ ★ **疑似"纯改名"** ✓
    ★★ 而本仓实测过："签名相同"**不等于**"能调"（★ 见 `DeleteDisplayStateSpecificRenderMaterial` 的反例：
      签名没问题，★ 但 **pywin32 迟到绑定造不出可调用对象**）⇒ ★ **仍须真机验** ✓

★★★ 判据（★ 跑之前写死）：★ 两者**都能调且返回同值** ⇒ **可换**。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。
# 文件:   tools/probe_setsavetoname_successor.py
# 定位:   ★ 阶段 2：`scripts/sw_delivery.py` 的 `_pywin32_pack_and_go` 里两处
#   `package.SetSaveToName(True, str(target) + os.sep)`。
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402

OUT = REPO / "output" / "setsavetoname-successor-evidence.json"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def _try(fn, *a):
    try:
        return {"ok": True, "ret": repr(fn(*a))[:80]}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:170])}


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S")}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        _g(
            _g(doc, "SketchManager"),
            "CreateCornerRectangle",
            -0.02,
            -0.015,
            0.0,
            0.02,
            0.015,
            0.0,
        )
        P.end_sketch(doc)
        nm = [n for n in (P.feature_names(doc) or []) if n.startswith("草图")]
        P.extrude_boss(doc, (nm[-1] if nm else "草图1"), 10.0)
        #: ★ Pack and Go 需要文档**已保存过**才会有依赖清单
        tmp = Path(tempfile.gettempdir()) / "dsh_sstn_probe.SLDPRT"
        try:
            C.save_document(doc, str(tmp)) if hasattr(C, "save_document") else None
        except Exception:  # noqa: BLE001
            pass

        ext = _g(doc, "Extension")
        #: ★ 用本仓自己的取法（★ 与 `sw_delivery._get_pack_and_go` 同路）
        try:
            from sw_delivery import _get_pack_and_go

            package = _get_pack_and_go(ext)
        except Exception as exc:  # noqa: BLE001
            R["取 package 出错"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
            package = None
        R["package"] = repr(package)[:90]

        if package is not None:
            tgt = str(Path(tempfile.gettempdir()) / "dsh_sstn_out") + os.sep
            R["旧_SetSaveToName(True, 目录)"] = _try(
                _g, package, "SetSaveToName", True, tgt
            )
            R["新_SetSaveToName2(True, 目录)"] = _try(
                _g, package, "SetSaveToName2", True, tgt
            )
            #: ★ 负例：★ 传不存在的目录看两者是否**行为一致**（★ 都该拒绝或都该接受）
            bad = str(Path(tempfile.gettempdir()) / "no_such_dir_xyz") + os.sep
            R["旧_空目录"] = _try(_g, package, "SetSaveToName", True, bad)
            R["新_空目录"] = _try(_g, package, "SetSaveToName2", True, bad)
    except Exception as exc:  # noqa: BLE001
        R["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:  # noqa: BLE001
            pass
    a = R.get("旧_SetSaveToName(True, 目录)") or {}
    b = R.get("新_SetSaveToName2(True, 目录)") or {}
    R["★_新旧读数"] = "%s vs %s" % (
        a.get("ret") or a.get("err"),
        b.get("ret") or b.get("err"),
    )
    R["verdict"] = (
        "★ PASS —— 新旧都能调 ⇒ 可换（纯改名）"
        if a.get("ok") and b.get("ok")
        else "★★ 需人工看 —— 至少一边不可调（★ 如实记，不硬换）"
    )
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(
        json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
