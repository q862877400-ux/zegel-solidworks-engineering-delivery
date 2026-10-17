"""★ 真机：切割清单属性名要**中文（本地化）**还是英文？—— ★ 用 `update_cut_list` 报的**真实属性名**去写。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_cut_list_property_names.py
# 定位:   ★ 2026-10-03（轮 429）承本轮的**链验证结果**。
#   ★★ 真机（`tools/prove_cut_list_chain.py`，★ `verdict: pass`）走通了那条链，★ 而**一条**没过：
#     ```
#     set_cut_list_properties(doc, {"Description": …, "Material": …})
#       ⇒ RuntimeError: 切割清单属性回读失败: 切割清单项目1 / **Material**
#     ```
#   ★★★ **而同一份证据里有一条强线索**：★ `update_cut_list` 列出的属性里有
#     **中文名**「**长度**」⇒ ★★ 那是**中文 UI 的本地化名**那个家族
#       （★ 与 `前视基准面` · `凸台-拉伸1` · `基体-法兰1` **同族**）✓
#   ⇒ ★★ **本探针就试中文名**（★ 而★ 它用的属性名**不是猜的**：★ 用 `update_cut_list`
#     ★ **实际报出来的**那些 + 加一个已知的国标列名）。
#   ★ 判据：★ **能写入且回读得到**（★ 那正是 `set_cut_list_properties` 自己的判据 ——
#     ★ 它"回读失败就抛"，★ 所以**不抛**就是成）。
# 官方依据: 本仓事实（中文 UI 下实体/特征/面名都是本地化名）· 本轮的 `update_cut_list` 真机输出
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 用**中文属性名**写 ⇒ **不抛且回读得到**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "cut-list-property-names-evidence.json")
PROFILE = Path(r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\weldment profiles\GB\square-rods.sldlfp")


def main() -> int:
    import sw_connect
    from sw_connect import safe_get_com_member
    from scripts.sw_part import current_sketch_name, end_sketch, sketch_line, start_sketch
    from scripts.sw_weldment import (create_structural_member_from_sketch, ensure_cut_list,
                                     set_cut_list_properties, update_cut_list)

    ev: dict = {"trials": [], "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_line(doc, 0.0, 0.0, 100.0, 0.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        rep = create_structural_member_from_sketch(doc, sk, str(PROFILE))
        ensure_cut_list(doc)
        #: ★ **先看真实属性名**（★ 不猜）
        up = update_cut_list(doc) or []
        names = []
        for folder in (up if isinstance(up, list) else [up]):
            props = (folder or {}).get("properties") or {}
            names.extend(list(props.keys()))
        ev["observed_property_names"] = names

        #: ★ 逐组试：★ 英文名 · 中文名（本地化）
        for label, props in (("english", {"Description": "DSH", "Material": "Q235"}),
                             ("chinese", {"说明": "DSH", "材料": "Q235"}),
                             ("chinese_only_material", {"材料": "Q235"})):
            rec = {"trial": label, "props": props}
            try:
                got = set_cut_list_properties(doc, props)
                rec["ok"] = True
                rec["returned"] = json.dumps(got, ensure_ascii=False, default=str)[:180]
            except Exception as exc:                           # noqa: BLE001
                rec["ok"] = False
                rec["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
            ev["trials"].append(rec)
        win = [t["trial"] for t in ev["trials"] if t.get("ok")]
        ev["verdict"] = "pass" if win else "partial"
        ev["successes"] = win
        ev["note"] = ("★ 试切割清单属性名：★ 英文 vs **中文（本地化）** —— "
                      "★ 而中文名不是猜的：★ `update_cut_list` 真机报出来的属性名是中文（「长度」）。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1, default=str)[:1600])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        try:
            if doc is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:                                      # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
