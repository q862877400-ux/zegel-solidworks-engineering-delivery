# 023 · 从「真缺」里补第一条：螺旋线

**Status**: Implemented（轮 104）

## 背景
前四轮（`020`/`021`/`022`）都在**核样**，收益递减 ⇒ 本轮**换方向**：
从 `010` 的「真缺」档里**挑一条实现出来**。
`helix`（螺旋线）在 `022` 的核样里被确认**确实没有**
（`InsertHelix` 只登记在 API 名表里，没有实现）。

## 做法（铁律 1 + 4：缝合、不发明；签名以官方源为准）
* **来源**：`本项目自建` —— 依据是**官方 API**（合法来源之一：
  「官方 API 文档 → 决定接口选型与参数顺序」）；
* **签名两源互证**：
  * 出厂反射 `iface_sldworks.txt`：`Void InsertHelix(Boolean×4, Int32, Double×5)`（在 **IModelDoc2** 上）
  * `C:\swapi\types\IModelDoc2\InsertHelix.md`：10 个具名参数
  * ⚠ **两源一致** ⇒ 无冲突，不需要类型库裁决；
* **并入规则 2**（单位）：长度 `_mm`、角度 `_deg`，换算只在边界做一次（`mm()` / `deg()`）。

## ★★ 本轮抓到的两个错
### ① 枚举值**凭记忆写反了**
```
我写的（错）                        官方真值（两源一致）
height_and_pitch = 1          ⇒     height_and_pitch = 2
height_and_revolution = 2     ⇒     height_and_revolution = 1
```
**两源**：出厂反射 `enum_values_sldworks.txt` + `C:\swapi\enums\swHelixDefinedBy_e.md`。
★ 这是铁律 4「**不凭记忆写标准值**」的**具体实例** —— 我在**写完之后、跑门禁之前**
停下来查了，才拦住。**契约测试现在把枚举值单独钉住。**

### ② 门禁抓到两处「改了东西没同步」
`union-level-audit.md`（能力 31→32）与 `union-coverage-matrix.md`（独家 68→71）
⇒ 都是正常流程，非缺陷。

## 判据
| ID | 判据 |
|---|---|
| SC-1901 | 10 个参数**顺序与类型**照官方，一个不差 |
| SC-1902 | ★ **枚举值**与官方两源一致（单独一段常量 + 独立测试）|
| SC-1903 | 单位换算在**边界**做一次（100 mm ⇒ 0.1 m；180° ⇒ π rad）|
| SC-1904 | 没建出来时抛**带原因**的 `RuntimeError`（"没选圆"）|
| SC-1905 | 来源块写明等级 **`stitched`** 且**无本机运行证据** |
| SC-1906 | `capabilities.yaml` 新增 `helix_and_spiral`（`stitched`），31 → **32** 条 |
| SC-1907 | 门禁 + 回归不退化（回归 **1054 passed**）|

## ⚠ 明确记下的限度
* **等级是 `stitched`，不是 `verified`** —— 只有静态证据，**本机从未建过螺旋线**；
* **前置条件未查证**（官方示例先选一个圆）；
* `Pitch` 与 `TaperAngle` 的**单位官方没写** ⇒ 本模块按同类推断处理，**已在 limitations 声明**；
* 只做**定距**；变距（`InsertVariablePitchHelix`）未实现。
