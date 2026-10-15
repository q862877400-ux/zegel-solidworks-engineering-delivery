# acceptance 242 · 靶子表扩容的准入

## 一、判据读数

| 判据 | 命令 | 读数 |
|---|---|---|
| ★ **红基线**（实现之前） | `pytest tests/test_deprecated_table_admission.py -q` | **`7 failed, 1 passed`**（缺 `ambiguous_deprecated_members`） |
| 新判据（实现之后） | 同上 | **`8 passed`** |
| ★ **变异检验**（判据跑在 `HEAD` 旧实现上） | 见 tasks T4 | 旧实现 `deprecated_successor('Select2')` = **`'Select3'`**（★ **猜了**）⇒ 判据能红 ✓ |
| 聚焦回归 | `pytest test_deprecated_table_admission test_deprecated_entry_interlock test_save_routing_interlock test_tool_specs_batch80 -q` | **`26 passed`** |
| 打包副本 | `scripts/sync_bundled_skill.py` | `files 471 · pruned []` |
| **门禁全套** @3.14.7 | `scripts/release_check.py` | **`EXIT 0` · `status pass` · `missing []`** |
| `gate_wiring` | 同上 | **44 个**（★ 未新增门禁文件） |
| `gate-classification.json` | — | **48**（★ 不变） |
| `param_binding` | 同上 | `pass`（479 个工具） |
| 互锁门禁族（既有） | 同上 | `dispatch_entry_guard 可见 1183 · 不可见 85` · `cd_site_disposition 站点 8` · `cd_host_scope 站点 8` —— ★ **全部不变** |

## 二、★ 量测读数（本轮**先量**的产出）

```
官方废弃索引 1671 条 / 1455 个成员名 / 扫 12123 页
  A 后继为空                    85
  B 后继名 == 自己              88
  C 真实现里出现（文本）        423 条索引行 / 328 个名
  D C 且后继页存在              390
  E D 且后继页无 Obsolete       302
  F E 且后继在仓库被调用        148
★★ 真树（两形态扫描器）**真的在调用**的废弃名 = **82** 个      ← ★ 这才是靶子规模
★★ 歧义名：字面后继口径 115 / 1455 · ★ **链终点口径 79** / 1455
   ★ 真树在调的 82 个名里真歧义 **11** 个：
     GetCorresponding · GetMassProperties · GetNext · GetSplines · GetType · KFactor ·
     Name · SaveAs · Scale · Select2 · Select3        ← ★ `Select2` 有 **6** 个不同终点
```

## 三、★★★ 核心事实

1. ★★★ **「官方那句 `Superseded by`」不是"该用哪个"** —— 它指向的后继**可能自己也已废弃**：
   `IModelDocExtension::SaveAs` ⇒ `SaveAs2` ⇒ `SaveAs3`（★ 三条都在官方索引里）。
   ⇒ ★★ 表里记的必须是**链终点**；★ 按字面值判会**假红**（本轮第一版口径就这么错了）。
2. ★★★ **「同名」≠「歧义」** —— `SaveAs` 按字面后继看有 2 个（`IModelDocExtension::SaveAs` / `SaveAs2`），
   ★ 而**两条链的终点都是 `IModelDocExtension::SaveAs3`** ⇒ ★ 对任何接口按名问它答案都对
   ⇒ ★★ 判歧义必须按**链终点**，不是按字面值（**115 → 79**）。
3. ★★★ **扩容的前置条件不是"多写几行表"** —— `deprecated_successor` 是**公开 MCP 工具**、只按成员名查；
   ★ 收进真歧义名（`Select2` 一族）会让它**静默给一个错的**后继
   ⇒ ★ 必须先有 `ambiguous_deprecated_members()` 把歧义**报出来**，★ 否则 `None` 与"不认识"**同形**。
4. ★★ **交接单待办 1 的前提被修了一半** —— 它说"逐条读两边的签名后收进表"（**方向对**），
   但没说**先量爆炸半径**；★ 量出来的第一件事就是"**表本身有按名歧义这个前置缺陷**"。

## 四、★ 踩到的坑

1. ★★ **第一版边界冻结口径按"字面后继"判 ⇒ `SaveAs` 立刻假红**（★ 它明明是**正确**的一条登记）。
   ⇒ ★ 修法：按**链终点**判（★ 先量、再改口径，而不是改数据去迁就判据）。
2. ★★ **`ambiguous_deprecated_members()` 必须能接收 `table`** —— ★ 否则单测无法喂合成表，
   而合成表是**唯一**能触发"歧义"的输入（★ 真表 4 条名字互不相同，永远触发不到）。
3. ★ **`docs/known-facts.md` 事实 272 是"活文档"** —— ★ 241 轮刚补过 6 个 test，本轮又加了 8 个（新文件）
   ⇒ ★ 顺手同步（★ 与 241 记的同一条纪律：**改判据数量时 grep 事实表**）。

## 五、未过门（★ 如实登记）

- ★ 准入判据**不是** `release_check` 的门禁 ⇒ 只在 pytest 面生效（★ 与 spec 241 同形）。
- ★ 关 3 是**静态**读数（AST），不判运行期；★ 关 2 依赖官方索引的**解析质量**（未经第二源复核）。
- ★ **仍未灌表** —— 82 个候选里 11 个真歧义，且每条要读两边签名（★ 独立工作）。
- ★ 真机未验；★ 未提交 / 未部署 / 未打 tag；★ 未删任何文件；★ 未调 COM / 真机。
