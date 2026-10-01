# Feature Specification: B 级缺口分诊 —— 把「缺 339」拆成可定范围的四类

**Feature Branch**: `010-gap-triage`

**Created**: 2026-10-01 · **Status**: Implemented

**Input**: 目标 ②「**B 级并入 339 个缺口操作**」—— 那是目标里**最大的一块未动**。
动它之前必须先答一个问题：**那 339 里，有多少是"真的没有"、有多少是"有但名字/暴露方式不同"？**
本特性就是**去量**，并**顺手修掉量它时撞见的一个真缺陷**。

---

## 一、起点：一个从模具域撞出来的怀疑

随手查模具域的 3 个「缺口」，发现 **2 个我们明明有**：
```
parting_line      → solidworks_mold_parting_line     （在 tool_specs_batch1.py）
shut_off_surface  → solidworks_mold_shut_off_surface （同上）
tooling_split     → 真的没有
```
⇒ 怀疑「339」被**命名差异**灌水。

---

## 二、★ 第一个真缺陷：暴露面被低估 20 个（**已修**）

`tools/build_union_map._our_tools()` **只读 `server.py` 的 `@mcp.tool(name=...)` 装饰器形式**，
而本仓库后补的工具注册在 **`mcp-server/tool_specs_batch*.py`**（`name="solidworks_*"`），
**与装饰器形式零交集**。实测：

```
server.py 装饰器          : 45 个
tool_specs_batch*.py      : 20 个（**与装饰器交集 = 0**）
合并                      : **65** 个        ← 修前只数到 45
```
★ **后果**：暴露面低估 20 ⇒ 缺口数被灌水。
⇒ 已修 `_our_tools()`（两个来源都读），并更新它的 docstring 说明这件事。

---

## 三、★ 第二个发现：**归一不去域词** ⇒ 同一条操作在两边是**不同的键**
```
solidworks_mold_parting_line → mold_parting_line   ≠   parting_line（外部）
```
根因：`build_union_sources._normalize` 只剥**厂商前缀**与**动词前缀**，**不剥域词**。

⚠ **但本特性不给主匹配器加模糊启发式** —— 已知事实 53：
**「调到看起来对」的信号是同一个启发式连续修补 ≥3 次还没稳定，就该停下回退。**
⇒ 主匹配器**一个字没动**（339 仍是**严格名口径**的诚实数字）；
另出一张**分诊表**（`docs/union-gap-triage.md`），按**有原则的规则**分类。

---

## 四、分诊结果（三个口径，分开量）

| 类 | 个数 | 占比 | 规则 | 含义 |
|---|---|---|---|---|
| **别名（强）** | **26** | 8% | 我们的归一操作名以缺口名结尾，且多出的词**全是域词** | 极可能**同一操作** |
| **别名（弱）** | 37 | 11% | 以缺口名结尾，但多出的词**含动词** | 疑似，**语义可能不同** |
| **后缀候选（需人工核）** | 144 | 42% | `scripts/sw_*.py` 里有函数名以缺口名结尾 | ⚠ **假阳性约一半**（见 §五）|
| **真缺** | 132 | 39% | 连 `scripts/` 里也没有同名函数 | **要从零实现** |

**三个口径为什么必须分开**：
* **MCP 暴露面**（65 个工具名）= 「四家有、我们没**暴露**」；
* **能力面**（779 个 `scripts/sw_*.py` 公开函数）= 「我们**写没写**」；
* 两者**不可合并**（已知事实 25：`server.py` 只引用 25 个模块）。

---

## 五、⚠★ 抽验揭穿了自己的分类规则（**如实记下**）

对「后缀候选」抽验 **10 条**：
```
✅ 真命中: parting_line→insert_parting_line · export_drawing_pdf→export_to_pdf
          · add_dimension→add_dimension · create_mate→add_mate
❌ 假阳性: shut_off_surface→create_bspline_surface（都是 surface，但不是 shut-off）
          · set_material→add_render_material · create_section_view→activate_view
          · get_mass_properties→apply_visual_properties
⛔ 正确拒绝: run_simulation · unfold_sheet_metal（确实没有）
```
⇒ 该规则**只比最后一个词** ⇒ **假阳性率约一半**。
⇒ **处置（不调启发式，按事实 53）**：
1. 把这个类别**改名为「后缀候选（需人工核）」** —— 它不是结论；
2. 把**抽验率写进工具的输出**（跑的时候就看得到）；
3. `docs/union-gap-triage.md` **只用于定范围**，每个候选**都要人工核**。

---

## 六、验收判据

| ID | 判据 | 怎么验 |
|---|---|---|
| **SC-601** | `_our_tools()` 读**两个来源**（45 + 20 = 65）| `python tools/probe_exposure_surface.py` |
| **SC-602** | 分诊表可重新生成，四类计数稳定 | `python tools/triage_union_gaps.py` |
| **SC-603** | 工具输出含**抽验警告**（不夸大候选类）| 同上 |
| **SC-604** | 主匹配器**未被改动**（339 口径不变）| `git diff tools/build_union_sources.py`（应无输出）|
| **SC-605** | 门禁 + 回归不退化 | `release_check` · `pytest tests -q` |

---

## 七、明确**不做**的

* **不**给主匹配器加模糊启发式（§三）；
* **不**为了"降低 339"而调候选规则（§五）；
* **不**把「后缀候选」当结论（改名 + 警告）。

---

## 八、结果

见 [converge.md](converge.md)。
