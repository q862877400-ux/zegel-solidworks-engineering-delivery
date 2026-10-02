"""★ 真机：看**本会话累积了多少东西** —— 因为轮 418 的失败与 B 组无关、与会话状态有关。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_session_accumulation.py
# 定位:   ★ 2026-10-03（轮 418）承**轮 418 的判断**：★ 那两条判据（`Count` 属性 与
#   `GetLoadsAndRestraints(i, out_i4())`）**都在"施加之后"崩了**，★ 而错误码还不一样
#   （`0x80010105` 与 `0x800706BA`）⇒ ★★ **不是判据的问题，是"施加之后管理器不可用"**。
#   ★ 而它**在一个"已知成功"的场景上也复现**（`apply_force`）⇒ ★ **与 B 组无关**。
#   ⇒ ★★ 最可能的真因：★ **本会话累积了太多算例/文档**（★ 本会话已建过**几十个**算例）。
#   ★ 本探针**只量这个**：★ 打开的文档数 · 已有的算例名 —— ★ 不施加任何载荷、不改任何东西。
# 官方依据: `ISldWorks.GetDocumentCount`（★ 属性，不是方法 —— 真机实测）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 拿到**文档数**与**算例清单**（★ 若"算例很多、文档也不少" ⇒ 支持累积假设）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(r"D:\AI\SW\output\session-accumulation-evidence.json")


def main() -> int:
    import sw_connect
    from scripts import sw_simulation as sim

    ev: dict = {"at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    try:
        #: ★ `GetDocumentCount` 是**属性**（★ 真机：当方法调会报 `'int' object is not callable`）
        ev["document_count"] = sw_connect.safe_get_com_member(sw, "GetDocumentCount")
    except Exception as exc:                                   # noqa: BLE001
        ev["document_count_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
    try:
        studies = sim.list_studies(sw)
        ev["studies"] = studies
        ev["study_count"] = len(studies) if hasattr(studies, "__len__") else None
    except Exception as exc:                                   # noqa: BLE001
        ev["studies_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
    ev["verdict"] = "pass" if "document_count" in ev else "partial"
    ev["note"] = ("★ 只量「本会话积累了多少」（★ 文档数 + 算例清单）—— ★ 不动任何东西。"
                  "★ 若累积很多 ⇒ 支持「轮 418 的失败与会话状态有关」那个假设。")
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps(ev, ensure_ascii=False, indent=1, default=str)[:1200])
    print("  产物: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
