import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           442 🎯 **Spec Kit `074`：回读着 mark 计数把实体真的选上 —— ****查到卡点****，按纪律强停止**（轮 155）——
               做法：沿用 `073` 的结论（判「选上没有」**一律回读** `GetSelectedObjectCount2(<mark>)`）
               ⇒ **每一次选完都回读**，**只有计数对了才去调功能**。
            443 ★ **6 种选法**（本轮补上了「草图实体」这一类）：
               ```
               ① 草图**整体** × 2（**官方示例原样**，按名 + mark=1）  ⇒ False
               ② 实体**边** × 2（Select4，(-1)=2 但 **mark=0**）      ⇒ False
               ③ 实体边（**按点** + mark=1）⇒ 返回 True 但 (1)=**0**（事实 94）
               ④ ★ **草图段** × 2（Select4，**(-1)=2 回读确认**）     ⇒ False   ← 本轮新的
               ⑤ ★ 草图段（按名 + mark=1）⇒ **命中 0**
               ⑥ 按名选边 ⇒ 0（事实 32）
               ```
            444 ★★★ **卡点查明**：
               ```
               `IEntity.Select4(Append, Callout)` **没有 mark 参数** ⇒ 选完 mark 仍是 **0**
               而 `SelectByID2` 需要**名字**，可是 ——
               ★ 实测：**草图段的 `GetID` 返回的是端点对**（`'(0, 1)'` / `'(1, 2)'`），
                 **不是** `Line1` 那样的名字 ⇒ 边与草图段**都没有可用名字**
               ⇒ **「选中 2 个实体 + mark=1」这个官方前提，在这条后端上我没能同时满足。**
               ```
            445 ★★ **按事实 53 强停止**（已 **6 种**）⇒ **候选解释一律列为未验证** ——
               例如「该后端下 `InsertCompositeCurve` 结构性不可用」（与事实 47 那族同类：
               `AccessSelections` 等**进程内非托管指针接口**在 pywin32 下到不了）。
               ⚠ **但这只是候选，本轮没有证据** ⇒ **不写进结论**。
               ★★ **本轮的定性必须精确**：查到的是**卡点**（现象在哪里卡住），
                 **不是真因**（为什么），更**不能**说「这功能不行」——
                 ★ 这与 `070`→`071` 的教训**正面呼应**：那次我把「我没摆对前提」错读成「功能不行」，
                   这一轮**不再犯**。
               ★ **两条可复用的**：① **草图段没有名字**（`GetID` 是端点对）⇒ **按名选段不可能**；
                 ② **`Select4` 与 mark=1 二者不可兼得** ⇒ 凡官方要求 mark 的地方**必须走 `SelectByID2`**。
               ⚑ **未查证**：⚠ **真因仍未查明**（只到卡点）；⚠「后端结构性不可用」是**候选、无证据**；
                 ⚠ 按点选边为什么计数 0 **未查明**；⚠ `composite_curve` **不升级**。
               已知事实 **95** 入库 · 回归 **1232 passed** · `release_check` exit 0。
               下轮候选：① **换后端**（`comtypes`）验证「结构性不可用」这个候选；
               ② 回到「真缺」继续补（**不要**再在 composite_curve 上打补丁）；③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+442 ", before, re.M):
    print("  游标 442 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+445 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 445 行已存在 ✓")
