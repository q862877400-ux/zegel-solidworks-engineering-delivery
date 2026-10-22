"""★ 真机：**`IMathUtility` 那一族的可达性** —— ★ 逐个试它的成员。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_imathutility_family.py
# 定位:   ★ 2026-10-03（轮 578）★ 执行**事实 455 留的下一步**。
#
#   ★★ 事实 455 查明：`ISldWorks.GetMathUtility` **能拿到对象**（`ok`），
#     ★ 而 `CreateVector` 报**找不到成员**、`ICreateVector` 报**无法读只写属性**。
# ⇒ ★ 故本探针问一个更大的问题：★ **这一族是"只有 CreateVector 不行"还是"整族都不行"？**
#  ⚠
#
#   ★ 反射里的成员（`C:\swapi\types\IMathUtility\`）共 **9** 个：
#     ```
# ComposeTransform \u00b7 CreatePoint \u00b7 CreateTransform \u00b7 CreateTransformRotat
# eAxis \u00b7
# CreateVector \u00b7 ICreatePoint \u00b7 ICreateTransform \u00b7 ICreateTransformRotate
# Axis \u00b7 ICreateVector
#     ```
#     ★ 而它们**都是"造对象"**（★ 无参可省）⇒ ★ 故**逐个调一次**就能画出可达性地图 ✓
#
# ★ 判据：★ **回对象**（`CDispatch` 等）⇒ 可达；★ **报错** ⇒ 记错码；★ **回 `None`** ⇒ 
# 记 None。
#   ⚠ 全程走 `tools/sw_guard.py`（★ 只调"造对象"，★ 不改模型）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

import pythoncom                                                     # noqa: E402
import win32com.client                                               # noqa: E402
from scripts import sw_connect as C                                   # noqa: E402


def _arr(values, vt=pythoncom.VT_R8):
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | vt, list(values))


#: \u2605 \u6bcf\u4e2a\u6210\u5458\u4e00\u7ec4\u201c**\u5408\u6cd5\u53c2\u6570**\u201d\u
#: ff08\u2605 \u7167\u5b98\u65b9\u7b7e\u540d\uff09
#: ★★ 注意：`call_com_member` 是 **`*args`**（★ 不收关键字参）
#:   —— 本探针第一版用了 `**vars_` ⇒ **报的是我自己的错** ⚠
CASES = [
    ("CreatePoint", ((_arr([0.0, 0.0, 0.0]),),)),
    ("CreateVector", ((_arr([0.0, 0.0, 1.0]),),)),
    ("CreateTransform", ((_arr([1.0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1]),),)),
    ("ICreatePoint", ((_arr([0.0, 0.0, 0.0]),),)),
    ("ICreateVector", ((_arr([0.0, 0.0, 1.0]),),)),
]


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "`IMathUtility` \u90a3\u4e00\u65cf\u7684**\u53ef\u8fbe\u6027\u5730\u56fe**"
               "\uff08\u2605 \u95ee\u7684\u662f\u201c\u53ea\u6709 CreateVector \u4e0d\u884c\u201d\u8fd8\u662f\u201c\u6574\u65cf\u4e0d\u884c\u201d\uff09",
          "official": "ISldWorks.GetMathUtility\uff080 \u53c2\uff09\u2192 IMathUtility\uff1b"
                      "\u5171 9 \u4e2a\u6210\u5458\uff0c\u90fd\u662f\u201c\u9020\u5bf9\u8c61\u201d",
          "get_math_utility": None,
          "cases": []}
    mv = None
    try:
        mv = C.get_com_member(sw, "GetMathUtility")
        ev["get_math_utility"] = "ok" if mv is not None else "None"
    except Exception as exc:                                              # noqa: BLE001
        ev["get_math_utility"] = "%s: %s" % (type(exc).__name__, str(exc)[:80])
    if mv is not None:
        for name, variants in CASES:
            row = {"member": name, "ok": False}
            for args_ in variants:
                try:
                    ret = C.call_com_member(mv, name, *args_)
                    row["returned"] = type(ret).__name__ if ret is not None else "None"
                    row["ok"] = ret is not None
                except Exception as exc:                                  # noqa: BLE001
                    row["returned"] = "ERR"
                    row["err"] = "%s" % str(exc)[:110]
                if row["ok"]:
                    break
            ev["cases"].append(row)
    ev["reachable"] = [c["member"] for c in ev["cases"] if c.get("ok")]
    ev["unreachable"] = [c["member"] for c in ev["cases"] if not c.get("ok")]
    ev["verdict"] = ("family_partly_reachable" if ev["reachable"] else "family_unreachable")
    p = R / "output" / "imathutility-family-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**" % ev["verdict"])
    print("     GetMathUtility = %s" % ev["get_math_utility"])
    print("     \u2605 \u53ef\u8fbe\uff1a%s" % (ev["reachable"] or "\u65e0"))
    print("     \u2605 \u4e0d\u53ef\u8fbe\uff1a%s" % (ev["unreachable"] or "\u65e0"))
    print()
    for c in ev["cases"]:
        print("  %-22s ok=%-6s \u56de=%s" % (c.get("member"), c.get("ok"), c.get("returned")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:120])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
