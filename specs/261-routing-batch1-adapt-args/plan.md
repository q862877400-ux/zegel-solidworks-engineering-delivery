# Plan — 换路由第 1 批（KFactor / MaterialIdName）

**Feature**: `specs/261-routing-batch1-adapt-args/`
**日期**: 2026-10-10

## 一、三源与冲突裁决顺序

| 序 | 源 | 用途 | 权威度 |
|---|---|---|---|
| 1 | ★★ **官方页签名** `C:/swapi/types/**` | 后继的形参与返回 | ★★★ |
| 2 | **官方索引** | 后继名 | ★★★ |
| 3 | **真树源码** | 原写法 | ★ 事实 |

## 二、口径

| 口径 | 真源 | 怎么用 |
|---|---|---|
| 废弃调用 | ★ **AST 按「名字 + 宿主」** | ★★ 只看名字会误伤（★ 第一版就误伤了） |
| 调用方 | ★ 扫 `set_material(` 的**行**，看有没有格式相关操作 | ★ 核「怎么用」不是「有没有用」 |
| 真机 | `output/_probe261_verify.py` | ★ 走 `sw_guard` · ★ 只用 3.14.7 |

## 三、实现步骤

1. **读 3 个后继的官方签名**（★ `DeleteDisplayStateSpecificRenderMaterial` / `GetCustomBendAllowance` / `GetMaterialPropertyName2`）。
2. **改 2 处**（★ 用脚本改 + grep 复核 + `ast.parse` 查语法）。
3. **真机复验**（★ 可写打开、赋材料、读两代、`QuitDoc` 不保存）。
4. **写判据** → ★ 判据抓出 3 个真问题（★ 宿主误伤 / 调用方 16 处 / 函数名写错）⇒ ★ **修判据与文档，不改数据**。
5. **跑生成器链**（★ 改了 `scripts/`）+ 门禁 + 回写四处。

## 四、改动面

`scripts/sw_sheet_metal.py`（★ 新增 `_read_k_factor`）· `scripts/sw_simulation.py`（★ 新增 `_read_material_id_name` + docstring）·
`tests/test_routing_batch1_adapt_args.py`（新）· `output/_probe261_verify.py` / `.txt`（新）· `specs/261-*/`（新）· 生成器产物 · 四处状态。

## 五、风险与对策

| 风险 | 对策 |
|---|---|
| ★★ 误伤「同名但不同接口」的调用 | ★★ 判据**按宿主**判（★ 第一版误伤，已修） |
| ★★ 语义变化悄悄破坏调用方 | ★★ 判据扫调用方的**用法**；★ 实测 16 处都不依赖格式 |
| ★ 真机把夹具零件改了 | ★ `QuitDoc` **不保存** + ★ 事后核 **mtime** |
| ★ 忘了跑生成器链 | ★ 已跑 7 步 |
