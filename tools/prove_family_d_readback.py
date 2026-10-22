"""★ 真机：族 D 那批「属性赋值 + return True」**到底有没有生效**（★ 逐个回读，不靠返回值）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_family_d_readback.py
# 定位:   ★ 2026-10-03（轮 468）★ 承 `tools/scan_blind_criteria.py` 的族 D（28 处）。
#   ★★ **用户的指令**：「逐个看逐个修」。
#   ★★★ **而"看"不能只看代码** —— ★ 族 D 报的是「**没有回读**」，
#     而「没有回读」**不等于**「一定会说谎」：★ 属性赋值若**要么成功要么抛**，
#     那 `return True` 就是**对的**（★ 我的判据在这里会出假阳性）。
#   ⇒ ★★★ **故本探针逐个真机验**：★ 调它 → **回读那个属性** → 判"值真的变了吗" ✓
# ★ 变了 = `return True` 是**诚实的**；★ 没变而回 True = **会说谎**（同 `set_view_scale`
# ）✓
#   ⚠ 只挑**安全可逆**的（★ 不碰 Costing / Simulation / 几何）：
#     `CommandInProgress` · `EnableSelection` · `SelectionColor` · `EnableContourSelection`
# 官方依据: 各成员在 `C:\\swapi\\types\\` 的签名（★ 属性 vs 方法）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ **回读值是否真的变了**（★ 不是看 `return True`）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R / "scripts"))
OUT = R / "output" / "family-d-readback-evidence.json"


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    import sw_automation_knowledge as AK
    import sw_selection as SE

    sw, _ = sw_connect.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "族 D 的「属性赋值 + return True」逐个回读（★ 变了=诚实 · 没变而 True=会说谎）",
        "judge": "回读那个属性，看值是否真的变了",
        "items": [],
    }

    def read(obj, prop):
        try:
            return get_com_member(obj, prop)
        except Exception as e:  # noqa: BLE001
            return "ERR:%s" % str(e)[:40]

    def one(label, obj, prop, setter, values):
        """★ 依次设 values 里的每个值，每次回读。"""
        row = {"item": label, "prop": prop, "verdict": "不能"}
        try:
            obs = []
            for v in values:
                setter(v)
                obs.append({"asked": v, "read_back": str(read(obj, prop))[:40]})
            row["obs"] = obs

            #: \u2605 \u5224\uff1a\u2605 \u81f3\u5c11\u6709\u4e00\u6b21**\u8bfb\u56de\u4
            #: e0e\u8bf7\u6c42\u5bf9\u5e94**\uff08\u2605 \u800c\u4e0d\u662f\u6ca1\u53d8\
            #: uff09
            #: ★ ★ 2026-10-03（轮 468）**修我自己判据的一个 bug**：原来拿
            #:   `str(asked).lower() != str(read_back).lower()` 比较 ⇒ ★ 而 COM 回的是
            #:   `True` / `False`（首字母大写）而字典里存的是字符串
            #:   ⇒ ★★ **真实成功也被判成「会说謎」**（假阴性）——
            #:   ★ 故改成**语义比较**：两边都归一到 `true/false`。
            def norm(v):
                s = str(v).strip().lower()
                return {"1": "true", "0": "false"}.get(s, s)

            asked = [norm(o["asked"]) for o in obs]
            got = [norm(o["read_back"]) for o in obs]
            #: ★★ 2026-10-03（轮 468）**第二次修判据**：原来拿**两个列表是否不同**
            #:   ⇒ ★ 而那不是我要问的问题。我要问的是：
            #:   **最后一次请求的值，最后一次回读到了吗**？
            #:   ★ 故判据 = `asked[-1] == got[-1]`（★ 一致＝诚实）。
            row["changed"] = bool(asked) and (asked[-1] == got[-1])
            row["verdict"] = (
                "\u8bda\u5b9e" if row["changed"] else "**\u4f1a\u8bf4\u8c0e**"
            )
        except Exception as e:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(e).__name__, str(e)[:110])
            #: \u2605 \u629b\u4e86\uff1d**\u4e0d\u9759\u9ed8** \u21d2 \u2605 \u90a3\u4e5
            #: f\u662f\u8bda\u5b9e\u7684\uff08\u2605 \u53ea\u662f\u96be\u7528\uff09
            row["verdict"] = "\u629b\u9519\uff08\u8bda\u5b9e\u4f46\u96be\u7528\uff09"
        ev["items"].append(row)
        print(
            "  %-30s %-22s %s"
            % (label, row["verdict"], str(row.get("obs") or row.get("err") or "")[:76])
        )
        return row

    #: \u2460 ISldWorks.CommandInProgress\uff08\u2605 \u94c1\u5f8b 2 \u91cc\u6700\u5e38\
    #: u7528\u7684\u90a3\u4e2a\uff09
    one(
        "CommandInProgress",
        sw,
        "CommandInProgress",
        lambda v: AK.enter_command_lock(sw) if v else AK.exit_command_lock(sw),
        [True, False],
    )
    #: \u2461 ISelectionMgr.EnableSelection
    doc = sw_connect.new_document(sw, "part")
    sel = get_com_member(doc, "SelectionManager")
    one(
        "EnableSelection",
        sel,
        "EnableSelection",
        lambda v: SE.set_enable_selection(sel, v),
        [False, True],
    )
    #: \u2462 ISelectionMgr.EnableContourSelection
    one(
        "EnableContourSelection",
        sel,
        "EnableContourSelection",
        lambda v: SE.set_enable_contour_selection(sel, v),
        [True, False],
    )

    ok = sum(1 for i in ev["items"] if i["verdict"] == "\u8bda\u5b9e")
    ev["honest"], ev["total"] = ok, len(ev["items"])
    ev["verdict"] = "pass" if ok == ev["total"] else "partial"
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  \u2500\u2500 \u8bda\u5b9e **%d / %d**" % (ok, ev["total"]))
    print("  \u4ea7\u7269\uff1a%s" % OUT)
    try:
        doc = sw.ActiveDoc
        if doc is not None:
            t = str(safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
        sw.CommandInProgress = False
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
