"""★ 真机验证：修补后的 `sw_export._export_generic`（STEP）与 `export_to_stl` 是否真出文件。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   probe_export_generic_fixed.py
# 定位:   规格 206 / 本轮 —— 上一步 `probe_export_saveas3_arity.py` 已定案根因（少传第 5 参
#         `AdvancedSaveAsOptions`）；本探针**验证修补后的实现**，走**真函数**（不是重写一遍调用）：
#           `scripts/sw_export.py` 的 `export_to_step` / `export_to_stl` ✓
# ★★ 为什么要单独验：★ MCP 工具层跑在**长驻进程**里，它启动时就把 `sw_export` 载入内存了 ⇒
#   ★ 改盘上的 .py **不会**让已连着的 MCP server 拿到新代码 ⇒ 必须**进程内直接调**才能验本轮修复 ✓
# 官方依据: `IModelDocExtension/SaveAs3.md`（7 参）· 本仓 `export_to_image`（同文件里 7 参的对照）✓
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

import sw_export  # noqa: E402
from sw_connect import connect_solidworks, get_com_member  # noqa: E402

OUT = ROOT / "output"


def main() -> int:
    sw = connect_solidworks(visible=True)
    if isinstance(sw, tuple):
        sw = sw[0]
    model = get_com_member(sw, "ActiveDoc")
    if model is None:
        print("★ 没有活动文档")
        return 1
    print("★ 活动文档: %r" % get_com_member(model, "GetTitle"))

    rows = []
    for label, fn, name in (("STEP", sw_export.export_to_step, "_fixed_generic.step"),
                            ("STL", sw_export.export_to_stl, "_fixed_generic.stl")):
        p = OUT / name
        if p.exists():
            p.unlink()
        row = {"format": label, "path": str(p)}
        try:
            fn(model, str(p))
            row["call"] = "ok"
        except Exception as exc:                                   # noqa: BLE001
            row["call"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        row["exists"] = p.exists()
        row["size"] = p.stat().st_size if p.exists() else 0
        rows.append(row)
        print("  %-5s ⇒ exists=%s size=%s  %s" % (label, row["exists"], row["size"], row["call"]))

    (OUT / "export-generic-fixed-evidence.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = all(r["exists"] and r["size"] > 0 for r in rows)
    print()
    print("★ 判据（★ 文件，不是返回值）: %s" % ("PASS —— 两种格式都真出了文件" if ok else "FAIL"))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
