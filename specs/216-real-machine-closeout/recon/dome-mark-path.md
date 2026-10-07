# 规格 216 · T-216-06b：圆顶「选面 + mark=1」这条路**真机定案**

> **测量脚本**：`output/_t216_dome_mark_probe.py`（一次性；★ `output/` 被 gitignore ⇒ **读数抄在这里**）✓
> **跑法**：★ `python tools/sw_guard.py --timeout 600 -- python output/_t216_dome_mark_probe.py`
> （★ 20.7 s · ★ **0 弹窗** · ★ `aborted_for_llm: false`）✓

## 一、★ 读数（两格对照，★ 逐字）

### 格 B —— **既有冒烟已被证明的形态** ⇒ ★★ **成立**

| 读数 | 值 |
|---|---|
| `select_mark1_returns` | ★ `True` |
| `mark_after` | ★ **`1`** |
| `insert_dome` | ★ `no-exception` |
| ★★ **`tree_delta`** | ★★ **`['圆顶1']`** ✓ |
| `before_n` → `after_n` | 7 → **8** ✓ |

★ 用的是冒烟逐字那一串（`tools/verify_dome_smoke.py` L133-136）：
```python
callout = sw_part._empty_callout()                     # ★ 事实 33：必须 VARIANT(VT_DISPATCH, None)
doc.Extension.SelectByID2("", "FACE", W/2, H/2, D, True,  0, callout, 0)   # 先 mark=0 选一次
doc.ClearSelection2(True)                                                   # 清选
doc.Extension.SelectByID2("", "FACE", W/2, H/2, D, False, 1, callout, 0)   # ★ 再 mark=1
```
⇒ ★★ **判据落地**：★ 圆顶这条路**成立**，★ 且**判据是特征树增量**（★ `insert_dome` 是 `void`、
★ 返回值什么也证明不了）✓

### 格 A —— **我原打算走的选择器路** ⇒ ★ **第一跳就失败**

★ 逐字异常：
```
EntitySelectionError: 非法的实体选择器 '+z'；合法形式：'__current_selection__' 或 'index:<n>' 或一个 COM 对象
```
★★ **这更正了我自己的一个假设**：★ 我以为 `"+z"` 是通用选择器 ——
★ 它其实是**别处**（仿真 `apply_normal_force(..., face_selector="+z")`）的词汇，
★ `sw_selection_spec.resolve_selection` **不认**它 ✗
★ `tree_delta = []`（★ 什么都没建成，★ 因为异常发生在选面那一步）✓

### 仍未定的一点（★ 如实记）

★ 格 A 没走到 mark 那一步 ⇒ **`SetSelectedObjectMark(AtIndex, Mark, Value)` 的第 3 参语义仍未定**
（反射 arity=3）⇒ ★ 两条路可选：★ **实测它** · ★ 或**走格 B 那条已被证明的按点+mark 路** ✓

## 二、★ 由此定下的实现方案（★ `insert_dome_report`）

★ 目标：★ 让**模型**能指定"给哪个面加圆顶"，★ 而 **规则 3 不许工具收裸坐标** ✓
```
① 入参用**声明式**：`face_index`（★ 或 `selection="index:<n>"` —— ★ 两者都在 `sw_selection_spec`
   认的合法形式里 ✓）
② 取到那个面实体（`entities_on_body(model, "FACE")[face_index]`）
③ **在这个面上算一个点**（★ 用官方 `IFace2::GetClosestPointOn`（arity 3，反射里有）★ 或该面的
   包围盒中心）—— ★ 点是**工具自己算的**，★ 所以不违反规则 3 ✓
④ 照格 B 那一串选它（★ 先 mark=0 → `ClearSelection2(True)` → **mark=1**）
⑤ 调 `insert_dome`；★ **判据取特征树增量**（★ 不看返回值）✓
```
⚠ ★ 另有一个**更省**的候选：★ 第 ④ 步换成"`select_object` 选上（mark=0）→ 再补 `mark=1`"
  ⇒ ★ 但那要**先实测** `SetSelectedObjectMark` 的 3 参语义 ⇒ ★ 本轮**未定** ✓

## 三、★ 与规格 215 的一条纪律一致（★ 顺手记）

★ 本轮**没有**新建"证据脚本"，而是先读了既有冒烟（★ known-facts 186 的教训：
「轮 249-251 重复造了证据脚本，而仓库里早有更强的既有冒烟」）⇒
★★ 本文件只是**把一次性测量的读数抄进可跟踪的地方**（★ 因为 `output/` 被 gitignore）✓

---

## 四、★★ 改完之后的**真机复验**（★ T-216-06b 的收口读数）

★ 改动：★ `sw_part.insert_dome_report(...)` **新增声明式 `face_index`** + 新助手
`sw_part.select_face_by_index_mark1`（★ 照格 B 那一串；★ 面点由官方 `IFace2::GetBox()` 取盒中心
—— ★ **点在工具内算**，★ 故不违反规则 3 的"不许收裸坐标"）✓

★ 跑法：`python tools/sw_guard.py --timeout 600 -- python output/_t216_dome_tool_verify.py`
⇒ ★ **6.0 s · 0 弹窗 · `aborted_for_llm: false`** ✓

| 用例 | ★ 读数 |
|---|---|
| ★ 正例 `insert_dome_report(doc, 8.0, **face_index=0**)`（★ **不预选任何东西**）| ★ `ok = True` · ★ **特征树增量 `['圆顶1']`** · 7 → **8** ✓ |
| ★ 反例 `face_index=999` | ★ `RuntimeError: face_index=999 越界（本件共 6 个面）⇒ ★ 这是**前置未成立**、★ 与「圆顶建不出来」是两件事` ✓ |

★★ **判据两段都落地**：★ ① 选区建起来了（否则助手会抛）· ★ ② **特征树真的多了 `圆顶1`** ✓
★ 而反例证明**失败是响亮的**（★ 不会静默混成"能力不行"）✓

★★ **门禁自动跟着变**：★ `check_preselect_family.py` 由「命中 12 · 基线 12」变成
「**命中 11 · 基线 11**」⇒ ★ 圆顶**离开了预选族名单**（★ 棘轮双向：修好了就不许留在名单里）✓
★ 同轮把门禁的"自选"判据**从逐个点名收成命名约定** `select_[a-z0-9_]+\s*\(`
（★ 起因：新助手叫 `select_face_by_index_mark1` —— ★ 逐个点名的名单**必然漏**）✓
