# 092 · `mold_evidence` 从**错的接口**读 ⇒ 真机永远全 None；假对象测试全绿

**Status**: Implemented（轮 172）· ⚠ **未修功能**（只更正了文档 + 补了负例）· `mold_tools` 仍 `stitched`

## 一、动机
`mold_tools` 是 **`stitched`** 且 **`evidence` 为空**；它的第 3 条限度说
「本机没有 OCP/cadquery/trimesh ⇒ 涉及 **headless-occt** 的声明无法复现」。
★ 但同一条目的第 1 条说「新增 `scripts/sw_mold.py`（… + `mold_evidence`）」——
★★ **那是我们自己的 COM 侧能力**，**可以真机验** ⇒ 本轮给它取证。

## 二、★★★ 真机结果（`tools/probe_mold_evidence_readers.py`）
```
IFeatureManager.GetPartingLinesCount / GetPartingSurfacesCount /
  GetCavitySurfacesCount / GetCoreSurfacesCount   ⇒ **全 AttributeError: <unknown>.X**
IModelDoc2.PartingType / CoreCavitySplit          ⇒ **同样不存在**
（get_com_member 与 call_com_member **两种**取法结果一致 ⇒ 不是「取法」问题）
```

## 三、★★★ 根因：成员在**别的接口**上（事实 36 那一族）
```
GetPartingLinesCount    ⇒ **IPartingLineFeatureData**（另有 IDraftFeatureData2 同名成员）
GetPartingSurfacesCount ⇒ I*FeatureData（swapi 有独立说明页）
PartingType             ⇒ **IPartingSurfaceFeatureData**
CoreCavitySplit         ⇒ **IPartingLineFeatureData**
```
⇒ 从 `FeatureManager` / `model` 上读**永远是 None** ⇒
★ **「全 None」不是「空件没有分型」，而是「读错了对象」。**
⚠ **要真读到**必须先拿到对应的 `I*FeatureData`（从**已存在的**分型线/分型面特征上取）
⇒ ★ **前提是零件上已经有那些特征**；空零件上**本来就取不到**（**两者表象相同，别混**）。

## 四、★★ 这是「假对象测试看不见真契约」的**第 4 次**
| 次 | 事实 | 假对象看不见的东西 |
|---|---|---|
| 1 | 99 | 干涉检查用了**三个不存在的成员名** |
| 2 | 101 | `sketch_relations` 因为**无 `sw_` 前缀**被整体漏扫 |
| 3 | 106 | `AddIndicator` 的 `TolType` **取值不在官方清单** |
| 4 | **112** | `mold_evidence` 的成员**在错的接口上** ⇒ 假对象恰好**有**它们 |

## 五、处置（三条）
```
① **如实更正** `mold_evidence` 的 docstring：写明它**在真机上只会全 None**、**不假装能读**（铁律 5）
② 补一条**能开火**的负例测试：用**没有那些成员**的假对象 ⇒ 断言**必须是 None、不许变成 0**
③ 修法（从 FeatureData 取）**需要**有分型特征的零件才能验证 ⇒ **未做**，记进限度
```

## 六、判据
| ID | 判据 |
|---|---|
| SC-9201 | ★★ **两种取法都试**（`get_` / `call_`）⇒ 排除「取法不对」|
| SC-9202 | ★★★ **查清归属**：4 个计数 + 2 个属性在 `I*FeatureData` 上，**不在** `IFeatureManager`/`IModelDoc2` |
| SC-9203 | ★★ 分辨「**空件没有**」与「**读错对象**」（两者表象相同）|
| SC-9204 | ★ 如实更正 docstring（**不假装能读**）|
| SC-9205 | ★ 补**能开火**的负例测试（成员缺席 ⇒ 必须 `None`，不许变 0）· 契约 **11 passed** |
| SC-9206 | 门禁 + 回归不退化 |

## ⚠ 明确记下的限度
* ⚠ **功能未修** —— `mold_evidence` **仍从旧位置读** ⇒ 真机上**仍只会全 None**；
* ⚠ 修法（从 `I*FeatureData` 取）需要**有分型线/分型面特征的零件** ⇒ 本轮**没有**那样的件，**未验证**；
* ⚠ 「成员不在 `IFeatureManager` 上」是**真机 + 两种取法**证实的；
  「它们在 `I*FeatureData` 上」来自 **swapi/反射**（**未经真机调用**）；
* ⚠ `mold_tools` **仍为 `stitched`**（本轮**没有**升它 —— 读取侧是空壳，写入侧在未准备件上会弹框）。
