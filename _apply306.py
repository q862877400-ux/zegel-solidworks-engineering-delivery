import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# ── ① 更正事实 301（加指向 306 的标注，★ 不改原文 —— 保留错误记录）────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
body = (Path(r"D:\AI\SW\_fact306.txt")).read_text(encoding="utf-8").strip().replace("\n", " ")
if "\n| 306 |" not in tk:
    tk = tk.rstrip() + "\n\n" + body + "\n"
    K.write_text(tk, encoding="utf-8")
    print("  (1) wrote 306")
tk2 = K.read_text(encoding="utf-8")
if "本条定性已被事实 306 推翻" not in tk2:
    tk2 = tk2.replace("| 301 | **`mold_parting_geometry` 的写入那半：官方要 mark 1 + mark 4",
                      "| 301 | \u26a0 **本条定性已被事实 306 推翻**（\u2605 \u201c\u505a\u4e0d\u5230\u201d\u662f**\u8bef\u5224** \u2014\u2014 "
                      "\u771f\u56e0\u662f\u5f53\u65f6\u7ed9\u7684\u662f**\u731c\u6d4b\u7684\u70b9**\u800c\u672a\u547d\u4e2d\u8fb9\uff1b"
                      "\u2605 \u7528**\u8fb9\u7684\u4e2d\u70b9**\u5c31\u6709\u6548\uff0c\u5df2\u771f\u673a PASS\uff09\u3002"
                      "**`mold_parting_geometry` \u7684\u5199\u5165\u90a3\u534a\uff1a\u5b98\u65b9\u8981 mark 1 + mark 4")
    K.write_text(tk2, encoding="utf-8")
    print("  (2) 已在 301 加更正指向")

# ── ② capabilities：mold_parting_geometry 补 evidence + 改 limitations ──────
c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
x = next(y for y in d["capabilities"] if y["id"] == "mold_parting_geometry")
EV = ("python 真机（轮 389）★ **PASS** —— 写入那半的 `insert_parting_line` 打通：按官方 Remarks 的 mark 表"
      "（**direction of pull = 1** · **parting line edges = 4**），★ 方向选基准面、"
      "★ 边按**中点**（`GetStartVertex`/`GetEndVertex` 求平均）用 `SelectByID2` 选 ⇒ "
      "**回读 `GetSelectedObjectCount2(-1)` = 5**（1 基准面 + 4 条边）· `insert_parting_line` ⇒ **`分型线1`**。"
      "证据 output/mold-parting-line-marks-evidence.json。"
      "★★ **更正事实 301**：先前判「给边线打 mark 4 在 pywin32 上做不到」是**误判** —— "
      "真因是当时给的 `x, y, z` 是**猜测的点**、没落在边上（静默成功：回 true 而计数 0）；"
      "★ 用**边的中点**即有效。")
ev = list(x.get("evidence") or [])
if not any("insert_parting_line" in s and "PASS" in s for s in ev):
    ev.insert(0, EV)
x["evidence"] = ev
LIM = ("★★ 2026-10-03（轮 389）**更正**：`insert_parting_line` **真机 PASS**（`分型线1`）—— "
       "边界边按**中点** + `mark = 4` 用 `SelectByID2` 选即可（★ 回读计数 = 5）。"
       "★ 先前那条「给边线打 mark 4 做不到」**作废**（事实 306）；真因是当时给的是**猜测的点**。"
       "⚠ **仍未验的三个**：`insert_parting_surface` · `insert_shut_off_surface` · "
       "`insert_core_cavity_solids`（★ 硬约束③：没有 pass 不升）。")
lim = list(x.get("limitations") or [])
lim = [t for t in lim if "走到死路（穷尽式）" not in t]
if not any("更正" in t and "insert_parting_line" in t for t in lim):
    lim.insert(0, LIM)
x["limitations"] = lim
#: ★ 只验了一个工具 ⇒ 不升 verified（★ 保持 stitched）
c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  (3) mold_parting_geometry level=%s ev=%d lim=%d" % (x.get("level"), len(ev), len(lim)))
