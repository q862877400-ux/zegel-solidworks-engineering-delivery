"""★ 真机探针：定位并验证 `_export_generic` 的 SaveAs3 实参个数缺陷（STEP/STL 导出失败）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   probe_export_saveas3_arity.py
# 定位:   规格 206 / 本轮真机实测 —— 用户问「项目能不能用」，实测发现 **STEP/STL/IGES 导出全失败**：
#           `com_error: (-2147352571, '类型不匹配。', None, 5)` ✓
# 官方依据（★ 逐字，本探针不猜）：
#   · `C:\swapi\types\IModelDocExtension\SaveAs3.md` 的 `**Signature**:` 逐字：
#       `System.bool SaveAs3( System.string Name, System.int Version, System.int Options,
#        System.object ExportData, System.object AdvancedSaveAsOptions,
#        out System.int Errors, out System.int Warnings )`   ⇒ ★★ **7 参** ✓
#   · 本仓 `scripts/sw_export.py` 的 `_export_generic`（L501-505）**只传 6 个** ⇒
#       ★ `AdvancedSaveAsOptions` 整段缺席 ⇒ `errors` 落到**位置 5** ⇒ 报错正是「位置 5」✓
#   · ★ 对照（同文件里**能用**的那个）：`export_to_image`（L724-731）传的是 **7 个** ✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from sw_connect import connect_solidworks, create_empty_dispatch_variant, get_com_member, out_i4  # noqa: E402

OUT = ROOT / "output"
CASES = [
    ("现状_6参（apps 现状写法）", lambda ext, p, eo, wo: get_com_member(
        ext, "SaveAs3", str(p), 0, 1, create_empty_dispatch_variant(), eo, wo)),
    ("★_7参_补空Dispatch（本案修法）", lambda ext, p, eo, wo: get_com_member(
        ext, "SaveAs3", str(p), 0, 1, create_empty_dispatch_variant(),
        create_empty_dispatch_variant(), eo, wo)),
    ("7参_位置5传None", lambda ext, p, eo, wo: get_com_member(
        ext, "SaveAs3", str(p), 0, 1, create_empty_dispatch_variant(), None, eo, wo)),
    ("7参_位置5传空VARIANT", lambda ext, p, eo, wo: get_com_member(
        ext, "SaveAs3", str(p), 0, 1, create_empty_dispatch_variant(),
        create_empty_dispatch_variant(), eo, wo)),
]


def main() -> int:
    sw = connect_solidworks(visible=True)
    #: ★ 本仓 `connect_solidworks` 回的是 **(app, metadata)** 或 app 本身 ⇒ 两种都收（★ 不猜一种）
    if isinstance(sw, tuple):
        sw = sw[0]
    model = get_com_member(sw, "ActiveDoc")
    if model is None:
        print("★ 没有活动文档 ⇒ 先建一个再跑本探针")
        return 1
    title = get_com_member(model, "GetTitle")
    print("★ 活动文档: %r" % title)
    ext = get_com_member(model, "Extension")

    results = []
    for label, call in CASES:
        out = OUT / ("_probe_arity_%s.step" % label.replace("★", "S").replace("（", "_").replace("）", ""))
        if out.exists():
            out.unlink()
        errors, warnings = out_i4(), out_i4()
        row = {"case": label, "path": str(out)}
        try:
            ok = call(ext, out, errors, warnings)
            row["ok_ret"] = bool(ok) if ok is not None else None
            row["errors"] = getattr(errors, "value", None)
            row["warnings"] = getattr(warnings, "value", None)
        except Exception as exc:                                   # noqa: BLE001
            row["exception"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        row["file_exists"] = out.exists()
        row["size"] = out.stat().st_size if out.exists() else 0
        results.append(row)
        print("  %-34s ⇒ %s" % (label, json.dumps(row, ensure_ascii=False)[:180]))

    (OUT / "export-saveas3-arity-evidence.json").write_text(
        json.dumps({"active_doc": title, "results": results}, ensure_ascii=False, indent=1), encoding="utf-8")
    good = [r for r in results if r.get("file_exists") and r.get("size", 0) > 0]
    print()
    print("★ 产出真文件的写法: %s" % ([r["case"] for r in good] or "**一个都没有**"))
    print("★ 证据: %s" % (OUT / "export-saveas3-arity-evidence.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
