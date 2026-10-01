"""记录**决定性结论**：那三条卡在 pywin32 后端限制（事实 47）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（文档更新）
# 文件:   D:\\AI\\SW\\probe_setfixedface_forms.py（七种数组包装）
#         D:\\AI\\SW\\probe_setfixedface_overloads.py（两个重载）
#         D:\\AI\\SW\\probe_access_selections.py（AccessSelections 两种传法）
# 定位:   两轮 20+ 种形态实测全部失败 ⇒ 结论是**后端限制**，不是参数没找对。
#         `0x80010105` 与已知事实 28 的 `CreateBsplineSurface` 同码；
#         `capabilities.yaml` 的 `backend_catalog` 早已记录
#         「不能调用官方标记为仅进程内非托管 C++ 的指针接口」。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
WS = Path(r"D:\AI\SW")

FACT47 = (
    "| 47 | **`ISketchedBendFeatureData` 的 `AccessSelections` / `SetFixedFace` "
    "在 pywin32 迟到绑定下**不可调用** —— 这是**架构性限制**，不是参数没找对**"
    "（2026-10-01，**两轮 20+ 种形态**实测）："
    "`SetFixedFace(X,Y,Z,EdgeArray)` 的**七种数组包装 × 两个重载**全部报 "
    "`类型不匹配`（位置 1 或 4）；`AccessSelections(model, None)` 报 `类型不匹配`（位置 2）、"
    "改传 `VARIANT(VT_DISPATCH, None)` 则报 **`服务器出现意外情况`（`0x80010105`）**"
    "——**与已知事实 28 的 `CreateBsplineSurface` 同一个错误码**。"
    "**⇒ 这与 `capabilities.yaml` 里**早已记录**的后端限制吻合**："
    "「**不能调用官方标记为仅进程内非托管 C++ 的指针接口**」；"
    "反射里那对 **`IAccessSelections` / `IAccessSelections2`** 正是那种 `I` 前缀的**指针变体**。"
    "**⇒ 结论：`create_one_bend` / `create_edge_flange` / `create_gusset` 三条**
    "**在 pywin32 这条后端上到不了「建成」**（除非换 `comtypes` 或进程内 C++ 后端）。"
    "⚠ **不要再用「换个参数试试」的方式继续试** —— 20+ 种已穷尽 | "
    "`D:\\AI\\SW\\probe_setfixedface_forms.py` / `probe_setfixedface_overloads.py` / "
    "`probe_access_selections.py`；`capabilities.yaml` 的 `backend_catalog` 限制段 |\n"
)

DOC_SECTION = """

---

## 二十八、**决定性结论**：那三条不是「参数没找对」，是**后端到不了**（2026-10-01）

### 28.1 两轮 20+ 种形态，全部失败
```
SetFixedFace(X,Y,Z,EdgeArray):
  · **七种数组包装**（None / [] / VT_ARRAY|VT_DISPATCH / VT_ARRAY|VT_VARIANT /
    裸边列表 / 逐元素 VARIANT / VT_DISPATCH(边)）× **两个重载**（4 参 / 1 参）
    ⇒ 全部 `类型不匹配`（位置 1 或 4）
  · 先**预选边**再传空数组 ⇒ 同样失败
AccessSelections(model, None)                        ⇒ `类型不匹配`（位置 2）
AccessSelections(model, VARIANT(VT_DISPATCH,None))   ⇒ **`服务器出现意外情况`（0x80010105）**
```

### 28.2 ⇒ 这是**已记录的架构性限制**
`0x80010105`（`RPC_E_SERVERFAULT`）**与已知事实 28 的 `CreateBsplineSurface` 同一个错误码**。
而 `capabilities.yaml` 的 `backend_catalog` 里**早就写着**：
> 「**不能调用官方标记为仅进程内非托管 C++ 的指针接口**」

反射里那对 **`IAccessSelections` / `IAccessSelections2`** 正是那种 **`I` 前缀的指针变体**。

### 28.3 结论（写死，避免后人重走）
**`create_one_bend` / `create_edge_flange` / `create_gusset` 三条在 **pywin32 迟到绑定**这条后端上
到不了「建成」** —— 除非换后端（`comtypes`，或进程内 C++）。
**⚠ 「换个参数试试」这条路已穷尽（20+ 种），不要再试。**

### 28.4 本轮修正的**是另一个方向**的事
虽然创建层到不了，但本会话在这个模块上**确证并修掉了**：
* `create_one_bend` 的常量错（`swFmOneBend(33)` → `swFmSketchBend(35)`，事实 43）
* `create_gusset` 整步缺失的官方步骤 3（事实 44）
* `create_edge_flange` 的属性跨接口泄漏（`ReverseDirection`）
* 报告错层次**前推**（`CreateDefinition` → `CreateFeature`）
**⇒ 「到不了」与「一直没往前走」是两件事 —— 这几轮确实往前走了。**
"""


def main() -> int:
    f = WS / "AGENTS.md"
    t = f.read_text(encoding="utf-8")
    i = t.find("| 46 |")
    if i >= 0 and "| 47 |" not in t:
        e = t.find("\n", i) + 1
        f.write_text(t[:e] + FACT47 + t[e:], encoding="utf-8")
        print("  ✓ AGENTS.md 已加已知事实 47")
    else:
        print("  ⚠ AGENTS.md：未匹配或已加")

    with (WS / "docs" / "T-011-expose-capabilities-assessment.md").open("a", encoding="utf-8") as fh:
        fh.write(DOC_SECTION)
    print("  ✓ T-011 文档已追加「二十八」")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
