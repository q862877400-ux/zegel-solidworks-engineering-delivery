"""★ 真机补 `custom_properties_and_bom` 的运行证据（★ A4 的待补项）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   `scripts/sw_document_data.py::set_custom_properties` / `read_custom_property`
# ·
#         `scripts/sw_connect.py`（`new_document`）
# 定位:   ★ **为什么另写一个**：★ 轮 55 那个 `tools/probe_a4_runtime_evidence.py` **读
#           错了键** ——
#   ★★ 它取 `readback.get("value")`、★ 而 `read_custom_property` 回的是 **`raw`** ✓
#   ★★★ **而纪律是「`tools/` 只报不动」**（★ 改了会破坏"证据不可变"）⇒
#     ★★ **旧探针原样保留**（★ 它那次 `readback_value: None` 是**真的历史读数**）、
#     ★★★ **本探针另写一份**（★ 用**对的键**）✓
#   ★★★★ **判据（★ 两层）**：
#     · ★ `set_custom_properties` 的 **`verified`** 必须全 `True` ✓
#     · ★★ 而**独立回读**（★ 本探针自己调 `read_custom_property`）必须**逐条相等** ✓
#       ★★★ **两条要**分开算**** —— ★ 否则又变成"用被测者的回读去证明被测者" ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = REPO / "output" / "a4-custom-properties-evidence.json"
WANT = {"A4_探针_甲": "alpha", "A4_探针_乙": "beta", "A4_探针_丙": "gamma"}


def main() -> int:
    import sw_document_data as D
    from sw_connect import connect_solidworks, get_com_member, new_document

    app, _ = connect_solidworks(visible=True)
    model = new_document(app, "part")
    units = None
    try:
        units = list(get_com_member(model, "GetUnits"))
    except Exception:  # noqa: BLE001
        pass

    wrote = D.set_custom_properties(model, WANT)
    rows = (wrote or {}).get("properties") or []
    per_service = {}
    for r in rows:
        rb = r.get("readback") or {}
        per_service[r.get("name")] = {
            "add_status": r.get("add_status"),
            "verified": r.get("verified"),
            #: ★★ **对的键是 `raw`**（★ 能力层自己的判据用的就是它）✓
            "readback_raw": rb.get("raw"),
            "readback_exists": rb.get("exists"),
        }

    #: ★★★ **独立回读**（★ 本探针**自己**再调一次，★ 不用 `set_custom_properties` 的回读
    #: ）✓
    independent = {}
    for k in WANT:
        rr = D.read_custom_property(model, k)
        independent[k] = {
            "raw": rr.get("raw"),
            "exists": rr.get("exists"),
            "status": rr.get("status"),
        }

    service_ok = (
        bool((wrote or {}).get("success"))
        and len(rows) == len(WANT)
        and all(r.get("verified") is True for r in rows)
    )
    independent_ok = all(independent[k]["raw"] == v for k, v in WANT.items())

    R = {
        "★_判据": "★ 两层独立：★ ① 服务的 `verified` 全 True（★ 它自己的回读）· "
        "★ ② **本探针独立再读一次**、★ 逐条等于所写（★ 不借服务的回读）",
        "GetUnits": units,
        "asked": WANT,
        "service_reported": per_service,
        "service_ok": service_ok,
        "independent_readback": independent,
        "independent_ok": independent_ok,
        "★_说明": '★★ 轮 55 的旧探针读 `readback.get("value")` ⇒ 那里没有 `value` 键'
        "（★ 只有 `raw`）⇒ ★ 它记的 `readback_value: None` 是**探针的错**、"
        "★ **不是能力层的错** ✓",
    }
    OUT.write_text(
        json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print("★ service_ok:", service_ok, "· independent_ok:", independent_ok)
    for k, v in per_service.items():
        print("   %s ⇒ verified=%s raw=%r" % (k, v["verified"], v["readback_raw"]))
    print("★ independent:", json.dumps(independent, ensure_ascii=False)[:220])
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
