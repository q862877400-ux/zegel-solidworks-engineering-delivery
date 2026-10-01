# 062 · 补 `dome` —— 顺带查出「**取一个方法**」这个动作**会把它调一次**

**Status**: Implemented（轮 143）

## 一、`dome` 本身：官方 Remarks 是钥匙
```
官方 IModelDoc2.InsertDome（**void** 返回、**未标** Obsolete）:
  「Before using this method, you must select the face for the dome using a
    **selection mark of 1**.」
```
⚠ 用 `mark=0` 时 `InsertDome` 报 **`0x8002000F`**（`DISP_E_PARAMNOTOPTIONAL`）
★ **那个错误看不出是 mark 的问题**（与事实 33 同一类坑）。
★ 官方还给了 **C# 示例**（`Create_and_Modify_Dome_Feature_Example_CSharp.md`）⇒ 照着走。

### `swFmDome` **不存在**
```
枚举转储 enum_values_sldworks.txt：**0 命中**
CreateDefinition 的 **35 个**合法常量里：**没有**
⇒ 圆顶**走不了 CreateDefinition**（与事实 43 的 swFmOneBend / swFmDraft 同族）
⇒ 只能走 IModelDoc2.InsertDome
```

## 二、★★★ 真正的收获：`get_com_member` 的**危险设计**
```python
member = getattr(obj, attr_name)
if args: return member(*args)
try:
    return member() if callable(member) else member   # ← 没有实参就"先试调一次"
except Exception as exc:
    if "-2147352573" in message or "找不到成员" in message: return member
    raise
```
⇒ ★★ **对 COM 成员，「取」就等于「调」**！
```
实证：`get_com_member(doc, "InsertDome")` **自己抛** `0x8002000F`
     （因为 InsertDome 有 3 个必填参数）⇒ 说明它**真的调了一次**
```
⚠⚠ **危险面**：**无必填参数且有副作用**的成员
（`InsertDeleteHole()`、任何 `File*` 写盘方法）会**被「取」这个动作静默执行**。

### 处置（最小、不动既有语义）
把 `DISP_E_PARAMNOTOPTIONAL`（`0x8002000F` / 「非选择性的参数」）
也纳入「**返回成员、不调用**」——**未**改成「永不调用」（那会动到全仓库依赖的既有语义）。

★★ **而 `insert_dome` 起初完全不能工作，根因就是这个**（不是圆顶本身的问题）。

## 三、★ 真机冒烟 **9/9**（含两条**如实标注**）
```
✓ 造出 100×60×20 的板
✓ ★★ 按面上的点 + **mark=1** 选中顶面（官方 Remarks 要求）
✓ insert_dome(8) 未抛异常（⚠ 这什么也证明不了 —— void 返回）
✓ ★★ **证据 A-1**：边界框**逐分量**变了   size [20,60,100] → [34.2222,60,100]
✓ ⚑ **证据 A-2**：增长 14.2222，传的是 8 ⇒ **如实记为未查明**
✓ ⚑ **证据 A2**：IDomeFeatureData2 读回 ⇒ **标为不可达**（事实 47/68）
✓ ★★ **证据 B**：特征树 19 → 20（⚠ 哪个是圆顶未查明）
✓ 收尾无残留模态框
```

## 四、⚠ 本轮我自己的判据错了 **4 次**（都记下来）
```
① `GetFeatureCount(True)` ⇒ 'int' object is not callable ⇒ **它是属性不是方法**
② A-1 用 `max(size1) > max(size0)` ⇒ **错**（变的那个方向在 max 里排不上号）
③ `growth` 用 `max()-max()` ⇒ **抓不到"最小方向在长"**
④ 特征树"新增"取 `names[n_before:]` ⇒ **错**（`FeatureByPositionReverse` 从**新到旧**）
⇒ ★ 四条都是**同一个毛病：对第三方 API 的"形状"作了未验证的假设**。
```
★ 而修法也一致：**先用一个对照量清形状，再写判据**（本轮补了 A-1/A-2 的**两段式**：
先证"变了"，再单独记"变多少"）。

## 五、判据
| ID | 判据 |
|---|---|
| SC-5801 | ★★ 走**官方 Remarks**那条路（选面 `mark=1`）⇒ 建成 |
| SC-5802 | ★ `swFmDome` **不存在**的核实（枚举 + 35 常量表）|
| SC-5803 | ★★★ 查出 **`get_com_member` 「取」会「调」** 并最小修复 |
| SC-5804 | ★★ 指出**危险面**（无必填参数且有副作用的成员会被静默执行）|
| SC-5805 | ★ 冒烟 **9/9**，两条**如实标注**（未查明 / 不可达）|
| SC-5806 | ★ 记下我自己的 **4 次判据错**，并归结为同一个毛病 |
| SC-5807 | 已知事实 84 入库；门禁 + 回归不退化（回归 **1201 passed**）|

## ⚠ 明确记下的限度
* ⚠ **未查明**：`Height=8` 而 Z 增长 **14.2222**（语义待查）；
* ⚠ **未查明**：特征树里哪一个是圆顶（`FeatureByPositionReverse` 顺序语义没查清）；
* ⚠ **不可达**：`IDomeFeatureData2` 的读回（官方示例那条路，事实 47/68）；
* ⚠ `get_com_member` **仍是"会调"**的语义（本轮只是把一种错误码纳入白名单）——
  **彻底修（永不调用）会动到全仓库，未做**。
