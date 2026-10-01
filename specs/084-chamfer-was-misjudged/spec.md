# 084 · `CreateChamfer` 被判「架构性限制」是**误判** —— 倒角其实建成了

**Status**: Implemented（轮 164）· ✅ **`sketch_chamfer` 升 `verified`**

## 一、动机（A4 的正面工作）
5 条 `stitched` 里 **`sketch_edit_ops` 最近**（8/10，只有倒角失败）⇒ 修好即可升 `verified`。

## 二、★★★ 真机现象与仓库文档**不一致**
```
仓库 docstring（轮 122）：type=2 ⇒ **com_error 0x80010105**（判为"架构性限制"，按事实 53 停手）
**轮 164 真机**（默认 type=0）：**返回 None**（不是 com_error）
⇒ ★★ 表现不一样 ⇒ 按「一条的性质不能推广成整族」的纪律，**值得逐类型试**
```

## 三、★★ 逐类型试 + **回读线段数**（`tools/probe_chamfer_forms.py`）
```
type=0（默认 distance_angle，角度 0）  ⇒ 段数 2 → 2（没变）· 返回 None
type=0（角度 45°）                     ⇒ 段数 2 → 2（没变）· 返回 None
type=1（distance_distance 5/3）       ⇒ 段数 2 → 2（没变）· 返回 None
type=2（distance_equal，d=5）         ⇒ 段数 **2 → 3**（**变了 ✚**）· com_error 0x80010105
```
⇒ ★★★ **`type=2` 的倒角真的建出来了** —— 那个 `com_error` 是在**取返回值**（`SketchSegment`）
那一步抛的，**不影响倒角本身**。
⇒ ★★ 真正的限制是「**拿不到返回对象**」，**不是**「做不了倒角」。

## 四、★ 根因（一条可复用的）
```
轮 122 **只看异常、没回读副作用** ⇒ 与**事实 94**（「不信返回值，回读状态」）同源
⇒ 扩展一句：**也别只信异常** —— 异常可能只发生在**取值**那一步。
```

## 五、★ 修法与取证
```
修：create_sketch_chamfer 改为**回读线段数**判定（建成则返回 None 而不抛）
拆：独立条目 `sketch_chamfer`（level: verified）—— 因为冒烟**只覆盖了倒角这一条**
    ★ 这正是「一条的性质不能推广成整族」的**正面应用**：
      `sketch_edit_ops`（含 mirror / convert_entities）**仍为 stitched**
取：python tools/verify_sketch_edit_smoke.py ⇒ **10/10 verdict: pass**（段数 2 → 3）
```

## 六、★★★ 同一轮我还踩了**事实 61** 那个坑（如实记）
```
我用「按行切分字符串」的方式改 sw_sketch_edit.py ⇒ **切多了**，
删掉 `sketch_mirror` 与 `convert_entities` 共 **90 行**（git diff --stat: 46 insertions, 90 deletions）
⇒ 回归当场 **9 failed**
⇒ 修法照 61 的定则：**git checkout -- 恢复 → 改用 `edit` 工具逐处改** ⇒ `+44/-4`（**只加不删**）
⇒ 真机 10/10 · 契约 16 passed · 回归 1246 passed
⚠ **61 的定则我明明知道** ⇒ ★ 教训：**知道定则 ≠ 会照着做**；
  定则要变成**动作的固定顺序**（改完先看 `git diff --stat`）才有用。
```

## 七、判据
| ID | 判据 |
|---|---|
| SC-8401 | ★★ 发现「真机现象」与「仓库文档」**不一致** ⇒ 值得重验 |
| SC-8402 | ★★★ **逐类型试 + 回读线段数** ⇒ 定位 `type=2` 能成 |
| SC-8403 | ★★★ **更正**「架构性限制」这个定性（真因是**拿不到返回对象**）|
| SC-8404 | ★ 修 `create_sketch_chamfer`（回读线段数判定）|
| SC-8405 | ★★ 拆出 `sketch_chamfer`（`verified`，真机 **10/10**）· `sketch_edit_ops` 留 `stitched` |
| SC-8406 | ★★★ **如实记下自己踩的事实 61 那个坑**（-90 行）与修法 |
| SC-8407 | 能力 **37 → 38**（verified **31 → 32**）；门禁 + 回归不退化（回归 **1246 passed**）|

## ⚠ 明确记下的限度
* ⚠ 只证「**线段数 2 → 3**」（倒角建出来了），**不证倒角距离 5mm 的数值对不对**；
* ⚠ `sketch_mirror` / `convert_entities` **仍未单独取证** ⇒ `sketch_edit_ops` 留 `stitched`；
* ⚠ `type=0`/`type=1` **为什么不做任何事**，**未查明**（只记录了它们的表现）。
