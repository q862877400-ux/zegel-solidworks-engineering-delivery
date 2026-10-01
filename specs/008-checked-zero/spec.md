# Feature Specification: `checked == 0` 的 SKIP 语义（07 同族的最后一处）

**Feature Branch**: `008-checked-zero`

**Created**: 2026-10-01 · **Status**: Implemented

**Input**: 轮 83（`007-skip-semantics`）系统排查 SKIP 语义时，**如实记下一处未查证**：
```
check_signature_audit_freshness.py
  if checked == 0:
      print("**SKIP** —— 一个模块都没能实跑（便携性守卫）")
      return 0
```
⚠ 而**轮 55 首跑就撞上过这个形态**：`resolve_module` 的解析写法不对
⇒ **6/6 全报「跑不了」⇒ 误 SKIP**（当时靠人发现才修，注释留在 `resolve_module` 的 docstring 里）。
本特性就是去查证并修掉它。

---

## 一、为什么它**必然**是 FAIL 而不是 SKIP（**推理链，不是猜**）

```
① 能走到 `checked == 0` 这行 ⇒ `refs` 必然非空
   （上游 L238 已把「拿不到 iface_*.txt」那条 SKIP 掉了）
② 表里的模块是**本仓库自己的 `.py`**（`scripts/*.py` / `subskills/**/*.py`）
③ 它们的映射由 `resolve_module` 的解析顺序给出（`scripts/<name>` → `subskills/**/<name>` → 全仓 rglob）
⇒ ④ 「反射在、却一个都解析不出」只可能是：**解析坏了** 或 **仓库残缺**
   —— **两者都是故障，不是便携性**。
```
★ 这正是 `007` 定下的那条判据的又一次应用：
> **被读的那个东西，是本仓库自己的产物，还是本机/外部才有的数据源？**

---

## 二、实测复现（**先复现，再改**）

`tools/probe_checked_zero_skip.py`：把 `--repo` 指向**空临时目录**（模块全解析不出）
+ `--raw` 指向**真实反射转储** ⇒ 逼出「`refs` 非空、`checked == 0`」那条路径：

```
修前:  反射文件 **13** 份（已去重）· 文档列了 **6** 个模块
       ⚠ 6 个模块跑不了（文件不在）：drawing_workflow.py, sw_connect.py, …
       **SKIP** —— 一个模块都没能实跑（便携性守卫）
       ⇒ exit=0        ← **全绿**
```
⚠ 那正是**轮 55 的误 SKIP 形态**，**一模一样**。

---

## 三、验收判据

| ID | 判据 | 怎么验 |
|---|---|---|
| **SC-401** | 正例（真仓库 + 真反射）⇒ exit 0，6 个模块逐项相符 | `python scripts/check_signature_audit_freshness.py` |
| **SC-402** | **空仓库 + 真反射（`checked == 0`）⇒ exit 1** | `python tools/probe_checked_zero_skip.py` |
| **SC-403** | **便携性未受损**：拿不到反射转储 ⇒ 仍 `SKIP` exit 0 | 同上（`--raw` 指向不存在路径）|
| **SC-404** | 轮 83 修的「文档在但表读不出 ⇒ FAIL」**未退化** | `python tools/probe_skip_semantics.py` |
| **SC-405** | ★ **探针自己的用例必须成立**（见 §五）| 同上：`--doc <坏文档> ⇒ exit=1` |

---

## 四、明确**不做**的

* **不新增**门禁（改的是既有分支的语义）；
* **不动**「拿不到反射转储 ⇒ SKIP」那条（**那才是真正的便携性守卫**）；
* **不引入**新依赖。

---

## 五、★ 顺带修掉一个**假用例**（比没有用例更糟）

`tools/probe_skip_semantics.py`（`007` 的交付物）里有一个用例：
「把逐模块表用正则删掉，看门禁是否红」。轮 84 回看发现——
**那条正则根本没匹配上** ⇒ 产出的"坏文档"**仍带着完整的表** ⇒ 门禁照常 `[PASS]`，
而**我当时把它当成了"修好了"的证据**。

⇒ 改成**直接造一份「只有标题、不含表」的文档**（那才是「文档在、表读不出」的定义）
⇒ 实测 `exit=1`，用例这才成立。

★ **教训：假用例比没有用例更糟** —— 它会给出一份**看起来验过的**证据。

---

## 六、结果

见 [converge.md](converge.md)。
