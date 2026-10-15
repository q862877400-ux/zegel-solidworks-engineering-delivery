import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

EV = ("python 真机（轮 383）★ **7/8 通过**（`tools/capture_topology_readback_evidence.py`，走 `sw_guard` 护栏，"
      "5.3 s 无弹窗）：`bindings` ✓ · `material` = `AISI 1020` ✓ · `create_study` ✓ · "
      "`collect_numbers` ✓（`status: no_results`，合理 —— 不跑求解）· `constraints` ✓（9 kinds）· "
      "`manager_report` / `options_report` ✓（`CDispatch`）· **`set_goal` ✓（`before_taken: 0 → "
      "after_taken: 1` ⇒ 设置真的生效）**；★ **`set_iteration_options` 报 "
      "`com_error: (-2147417851, '服务器出现意外情况。')`** = **`0x80010105`** ⇒ ★★ 那是**事实 47 同族的"
      "架构性后端限制**（「不能调用官方标记为仅进程内非托管 C++ 的指针接口」），★ **不是参数没找对**。"
      "证据 output/topology-readback-evidence.json。")

LIM = ("★★ 2026-10-02（轮 383）**真机 7/8**：★ **读数与设参的 7 项全部真机通过**"
       "（★ 含 `set_goal` 的「设置生效」判据：`before_taken 0 → after_taken 1`）；"
       "★ **唯一不过的是 `set_topology_iteration_options`**，报 **`0x80010105`**"
       "（`com_error: (-2147417851, '服务器出现意外情况。')`）—— ★ 与**事实 47 / 28 同一个错误码**，"
       "★ 定性为**后端限制**（pywin32 迟到绑定调不到那种指针接口），★ **不是代码问题**。"
       "⇒ ★ 定则：★ **不要再「换个参数试试」**（事实 47：20+ 种形态已穷尽）。"
       "⚠ 另一条（`solidworks_topology_run`）需要跑求解 ⇒ 见 `analysis_run_readback` 的同族限制。")

c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
x = next(y for y in d["capabilities"] if y["id"] == "topology_readback")
ev = list(x.get("evidence") or [])
if not any("7/8" in t for t in ev):
    ev.insert(0, EV)
x["evidence"] = ev
lim = list(x.get("limitations") or [])
lim = [t for t in lim if "未真机通过" not in t or "同族限制" not in t]
if not any("真机 7/8" in t for t in lim):
    lim.insert(0, LIM)
x["limitations"] = lim
c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  ok · topology_readback level=%s ev=%d lim=%d" % (x.get("level"), len(ev), len(lim)))
