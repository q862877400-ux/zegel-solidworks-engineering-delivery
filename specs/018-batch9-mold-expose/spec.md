# 018 · 模具域补暴露 —— 以及一次**卡住会话的模态框**

**Status**: Implemented（轮 98–99）

## 一、能力侧的发现：一个「真缺口」其实是「已实现但没暴露」
`010` 把 338 个缺口分了四类。回头看**最小域（模具）的唯一"真缺口"** `tooling_split`：
```
官方成员：InsertMoldCoreCavitySolids / CoreCavitySplit
本仓库：scripts/sw_mold.py::insert_core_cavity_solids   ← **已经实现了**
        insert_core_cavity_solids   已暴露=否 · 有测试=是
        insert_parting_surface      已暴露=否 · 有测试=是
        mold_undercut_detect        已暴露=否 · 有测试=是
```
⇒ ★ **那个"真缺口"是 `010` 记的第三类（能力在、未暴露）**，不是要新写的。
⇒ batch9 把这三个接出去。

## 二、⚠⚠ 一次**真实事故**：模态框卡住会话
第一版冒烟在**空零件**上调 `insert_parting_surface` / `insert_core_cavity_solids`
⇒ SolidWorks 弹出**模态框**「**此拔模方向尚未定义。**」⇒ **卡住会话**（用户连续两次截图报错）。

**★ 记下的两条新事实**：
1. **`ISldWorks.CommandInProgress = True` 不能抑制这个模态框** ——
   铁律 2 说它抑制"未抑制的模态对话框"，**这里是反例**；
2. **改「视图/选择状态」的工具会把文档标脏** —— 批次 7 的三个工具在装配体上跑过后，
   主窗口标题变成 `mcp_avi_asm.SLDASM *`（**未保存标记**）。
   ⚠ 轮 96 曾把这记为「未查证」，**轮 99 得到答案：会脏**。

**处置**：
* 冒烟改为**前置条件感知** —— 那 2 个**一个都不调**，只把它们的**前置条件写下来**；
* 批次 7 的 3 条 doc **加警告**（`May mark the document as modified`）；
* 两条事实写进 `known-facts.md`（64/65）；
* **清理**：关掉我造的全部临时件（按标题匹配 `零件N` **且路径为空**，绝不碰有路径的）；
* **未保存任何东西**。

## 三、判据
| ID | 判据 |
|---|---|
| SC-1401 | batch9 声明 3 条、签名一致（契约测试）|
| SC-1402 | ★ 3 条的**前置条件已记录**（防下一个人再踩弹窗）|
| SC-1403 | 冒烟**不调用**那 2 个会弹框的工具 |
| SC-1404 | 批次 7 的 3 条 doc **都带脏标警告**（实测警告出现 **3** 次）|
| SC-1405 | `known-facts.md` 记下 64/65 |
| SC-1406 | 门禁 + 回归不退化（回归 **1039 passed**）|
| SC-1407 | ★ **未验证项如实声明**：`insert_core_cavity_solids` / `insert_parting_surface` 的**真机行为未验** |
