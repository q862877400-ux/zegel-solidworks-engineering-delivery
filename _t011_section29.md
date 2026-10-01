
---

## 二十九、`source` 提案工具 + **纠正我自己**对两个文件归属的误认（2026-10-01）

### 29.1 新增 `tools/propose_capability_sources.py`（**只打印，不写文件**）
已知事实 41 说 A2 的缺口是「29 条里 28 条**未被分类**」。本工具为分类**收集证据**：
```
① capabilities[].id / label  →  关键词（丢泛词 + **单复数归一**）
② scripts/*.py 的**文件名主干**  →  命中 ⇒ 候选实现模块
③ `git ls-tree -r origin/main`  →  **上游有**还是**我们新增**（**硬证据**）
⇒ upstream / original / mixed / **undetermined（不猜）**
```

**最终分布**：`upstream=11 · mixed=7 · original=3 · undetermined=8` ⇒ **21/29 有证据支撑。**

### 29.2 ★ 抽查验证（逐条与硬证据相符）
```
topology_optimization → original   （sw_topology.py 我们新增）✓
simulation_and_fea    → original   （sw_simulation*.py 我们新增）✓
sheet_metal           → upstream   （sw_sheet_metal.py **上游有**）✓
weldments             → upstream   （sw_weldment.py **上游有**）✓
routing               → mixed      （routing_review.py 上游 + sw_routing.py 新增）✓
```

### 29.3 🔴 **纠正我自己的一个误认**
我此前在文档与叙述里**多次**把 **`sw_weldment.py` / `sw_sheet_metal.py` 当成「我们新增的」**。
**硬证据**（`git cat-file -e origin/main:scripts/sw_weldment.py` **通过**）显示：**它们上游就有。**

**⇒ 工具的输出是对的，错的是我的假设。**
**⇒ 连带影响**：AGENTS.md 事实 34 那句「**该模块**原本自述未在本机实测」的**主语是上游**；
`capabilities[sheet_metal]` / `[weldments]` 的 `source` 应为 **upstream**。

**⚠ 教训（与事实 37 同源、方向相反）**：
> 事实 37 说「查『在不在』必须查两处」；
> **本轮补上另一半 —— 判断「某文件是不是我们的」必须跑 `git cat-file -e origin/main:<path>`，不能靠印象。**

### 29.4 ⚠ 同一件事的**两次**自我纠错（关键词匹配的收紧）
```
第一版：关键词用 `solidworks` + **还扫文件体** ⇒ 某条命中 **87 个模块**（毫无区分力）
第二版：丢泛词 + **只按文件名主干** ⇒ 分布合理，但 `part`/`mold` 被长度闸（≥5）挡掉
第三版：闸门降到 **4** + **单复数归一** ⇒ `weldments→sw_weldment` / `drawings→sw_drawing` 对上
```
**⇒ 三次都在同一处「调松/调紧」，但每次都是**有原则的**修（泛词表 / 匹配面 / 词形），
不是「挑到看起来对为止」。**

### 29.5 ⚠ 本工具**不写任何文件**（文档串里写明理由）
关键词匹配**不是归属证明**。`THIRD-PARTY-NOTICES.md` 写着
「把未并入的东西写成已并入，是**归属造假**，比遗漏更严重」
⇒ **本工具只把「该看哪些文件」缩小到可人工复核的范围，采纳与否由人定。**

### 29.6 ⚠ 第 7 次踩「长字符串内联」
用 heredoc 往里塞含 `\n` 的长字符串 ⇒ `\n` 变成真换行 ⇒ `SyntaxError`。
**⇒ 改用 `edit` 工具 + 独立的 `NOTES` 常量（每行独立终止）。**
