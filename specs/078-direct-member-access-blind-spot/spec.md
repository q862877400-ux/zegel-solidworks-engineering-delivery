# 078 · 补上「直接属性访问」这个盲区 —— 又修好一个**静默降级**的函数

**Status**: Implemented（轮 159）

## 一、动机（顺 `077` 的真缺陷）
`077` 修的 `GetSldWorksObject` 是**直接属性访问**形态。
⇒ ★ 而仓库里**有一个**查成员名的门禁 `scripts/check_member_names.py`（138 行）——
**它只认 `get_com_member` / `call_com_member` / `safe_get_com_member` 这三种包装形态**
⇒ ★★★ **直接属性访问是它的盲区**。本轮专门补它。

## 二、★★ 判据的两版（**第一版实测被弃用**）
```
第一版：「大驼峰 + 不在反射里」 ⇒ 扫出 **323 处**，逐条看**全是**
        argparse / pywin32 / OCP / winreg 的对象（`ArgumentParser` ×29 · `OpenKey` ×8 · …）
        ⇒ ★★★ **假阳性率 ≈ 100%** ⇒ **弃用**（事实 74 那一族：名字形态判不出"是不是 COM 成员"）

第二版（**有依据，不是猜**）：把对象名**限定到「被当作 COM 对象用过」的那些** ——
        即 `get_com_member(<OBJ>, …)` 的**第一个实参标识符**（90 个）
        ⇒ 扫出 **12 处**，人工判后**真可疑 2 处** ⇒ ★★ **两处都是真缺陷** ⇒ 判据**可用**
```

## 三、★★★ 查出并修好 `get_interference_detection` 的**三处**成员名
```
① `asm_model.InterferenceDetection`  ⇒ 官方是 **`InterferenceDetectionManager`**（**带 Manager**）
   （出厂反射 `get_InterferenceDetectionManager()`）
② `GetInterference(index)`           ⇒ 官方是 **`GetInterferences()`**（**复数**，无单数版）
③ `item.Name`                        ⇒ **`IInterference` 上根本没有 `Name`**
   （成员是 `Components` / `GetComponentCount` / `GetInterferenceBody` / `IGetComponents` /
     `Ignore` / `IsFastener` / `IsPossibleInterference` / **`Volume`**）
⇒ ⚠⚠ **三处都在 `try:` 里 ⇒ 此前静默降级**（不炸，但**永远拿不到数据**）
```

## 四、★★★ 真机 **6/6**，含本会话**最强的证据形态**
```
✓ 干涉数 = 1
✓ ★★★ **干涉体积读回 `15999.999999999998`** ⇒ 对上 **20×40×20 = 16000 mm³**
   ⇒ **一个能独立算出来的物理量，读回来数值吻合** —— 空操作满足不了
✓ `GetComponentCount = [2]`
```

## 五、★★★ 顺带查出一个**假对象测试**的真相
```
既有测试 `test_sw_assembly_interference.py` 的**假对象**正是照着**错的接口名**写的：
    class Item:      Name = "干涉-1"                 ← 不存在的 `Name`
    class Detection: def GetInterference(self, i)    ← 不存在的**单数**
    class Model:     InterferenceDetection = ...     ← 不存在的入口名（缺 Manager）
⇒ ★★★ **三处全对上** ⇒ 这个测试**一直绿**，而**真机永远是坏的**。
★ 教训（与事实 57/79 同族）：**用假对象测 COM 封装，只能测"逻辑"，测不出"成员名"** ——
  成员名**只有真机**（或对反射做静态比对）能证。
```

## 六、★ 我自己的一次**差点改错**
```
修完三处后那个测试红了（`warn` → `blocked`）⇒ 我一度把**期望值**改成 `blocked`。
⇒ ★★ 但它是**错的**：`status` 的逻辑是 `count == 0 ⇒ pass`，否则 **`warn`**
   （`blocked` 只在**异常**时兜底）。真机证据也是 **`status=warn`, `count=1`, `error=None`**。
⇒ ★ **是那条测试挡住了我去「修」一个正确行为。**（已改为保留 `warn`，并把这个经过写进测试的 docstring。）
```

## 七、判据
| ID | 判据 |
|---|---|
| SC-7401 | ★★ 第一版判据**实测假阳性 ≈100%** ⇒ **弃用**（不接门禁）|
| SC-7402 | ★★★ 第二版判据**有依据**（对象名从包装器第一实参推导）⇒ 323 → 12 |
| SC-7403 | ★★★ 查出并修好 **3 处**成员名（都在 `try:` 里 ⇒ 静默降级）|
| SC-7404 | ★★★ 真机 **6/6**，**体积定量**对上 **16000 mm³** |
| SC-7405 | ★★★ 查出**假对象测试**把错名固化下来 ⇒ 改成官方真名 |
| SC-7406 | ★ 我自己差点改错期望值 ⇒ **测试挡住了**（已留档）|
| SC-7407 | 回归 4 条 + 事实 99；门禁 + 回归不退化（回归 **1240 passed**）|

## ⚠ 明确记下的限度
* ⚠ **第二版判据仍有假阳性**（`QueryInterface` 是 COM 的 IUnknown 方法，不在 SW 接口表里）
  ⇒ **没有**直接接进门禁，只做成探针；
* ⚠ 12 处里还有 9 处**没逐条判**（OCP 对象 / docstring 举例）；
* ⚠ **判据判的是"名字在不在反射里"**，判不出**语义对不对**（事实 74 那一族）；
* ⚠ `GetInterferences()` 的**返回形状**我只是 `list(...)` 兜了一下，**未逐字查证官方说明**。
