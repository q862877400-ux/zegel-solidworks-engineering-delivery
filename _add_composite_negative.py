import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
EV = ("python tools/verify_composite_curve_smoke.py（**真机**，轮 151）："
      "**阴性结果** —— `IModelDoc2.InsertCompositeCurve()` 返回 **False**，"
      "**根因是前提没满足**（真机上两次 `start_sketch`+`end_sketch` **只留下 1 个草图**，"
      "⇒ 选不出 2 个草图给它合成）")
L = ("⚠ **2026-10-01（轮 151）`composite_curve` 未能取证**：官方入口是 "
     "`IModelDoc2.InsertCompositeCurve()`（**零参**、返回 `Boolean`，Remarks 要求"
     "**用 mark=1 选实体**），但真机上它返回 **False**，**根因是前提没满足** ——"
     "★ 实测：连续两次 `start_sketch` + `sketch_line` + `end_sketch` **只留下 1 个草图**"
     "（特征树里数出来的），⇒ **选不出 2 个草图**。"
     "⚠ **为什么只留下 1 个草图，本轮未查明**（疑与事实 9「画草图前要先选基准面」有关，"
     "但**没有验证**）⇒ ★ **因此本条能力没有升级**，也没有把 `insert_composite_curve` 记为可用。"
     "★★★ **本轮最值钱的产出是修掉了冒烟里一个「硬编码 `True`」的检查** —— "
     "它让整个冒烟建在一个**从未被验证的前提**上；改成"真的数特征树"之后，"
     "那条**当场变红**，前提问题才暴露出来。")
if Q.is_file():
    for c in d["capabilities"]:
        if c.get("id") == "part_and_features":
            c["limitations"].insert(0, L)
            c["evidence"] = list(c.get("evidence") or []) + [EV]
            print("  ok part_and_features 已更新")
    Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

FACT = "| 91 | " + "".join([
    "**我自己写了一个「硬编码 `True`」的检查，它让整个冒烟建在未验证的前提上** —— ",
    "2026-10-01（轮 151）补 `composite_curve` 时：冒烟里有一句 `chk(\"造出 2 个草图\", True, ...)` ⇒ ",
    "★ **它不可能失败** ⇒ 而真机上**两次 `start_sketch`+`end_sketch` 只留下 1 个草图** ⇒ ",
    "前提**实际不成立**，`InsertCompositeCurve()` 因此返回 **False**，而冒烟**一路绿到第 4 条**才红。",
    "★★ 改成「**真的数特征树里 SKETCH 型条目**」之后，那条**当场变红** ⇒ 前提问题才暴露。",
    "★ 这是本会话反复记录的那个反模式的**我自己犯的一次**：",
    "「**一个不会失败的检查，等于没有检查**」（事实 62/79/81/88 同一族）。",
    "⚠ 本轮**未查明**：为什么两次建草图只留下 1 个（疑与事实 9「画草图前先选基准面」有关，",
    "**但没验证**）⇒ 因此 `composite_curve` **未取证、能力未升级**（不谎称可用）。",
    "★ 方法论上的一条：**写冒烟时，"环境准备"那一步也必须是被验证的断言，不能是 `True`** ——",
    "因为**前提错了，后面全错**，而错法看起来像"功能不行"。 | ",
    "`tools/verify_composite_curve_smoke.py`；`_diag_composite.py`（特征树诊断）；事实 9 / 62 / 88 / 90 |",
])
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
if "硬编码 `True`」的检查" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 91")
else:
    print("  已有 91")
