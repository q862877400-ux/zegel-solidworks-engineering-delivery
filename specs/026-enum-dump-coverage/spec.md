# 026 · 补齐枚举门禁的**转储覆盖**：75 条「查不到」→ **0**

**Status**: Implemented（轮 107）

## 背景
`025` 建的门禁（第 16 道）实跑时报 **75 条「查不到」**（多为 Simulation 的 `sws*` 枚举），
当时记为「未查证」。本轮把它查清。

## 查到的事实
```
`swsAnalysisStudyTypeBuckling` 落在 **SolidWorks.Interop.cosworks.dll**
  ⇒ 那是**另一个程序集**（Simulation / COSMOSWorks），不是 sldworks
而 `_raw\reflect\enum_cosworks.txt` **已有对应转储**（363 个枚举节，格式完全相同）
```
★ ⇒ **不是"官方没有"，是我只读了一份转储。**

## 做法
把门禁从「读一份转储」改成「**读多份并合并**」：
* `_raw\enum_values_sldworks.txt`（sldworks 程序集）
* `_raw\reflect\enum_cosworks.txt`（cosworks 程序集）
* 合并顺序即优先级（`sw*` 与 `sws*` 前缀不重叠，实测无冲突）；
* 记下**每个成员来自哪份转储**；
* `DSH_ENUM_DUMP` 支持多份（`;` 分隔）。

## 结果
```
                 轮 106        轮 107
转储份数            1             2
合并成员         8,216         **10,588**
有据可查的值       15             **90**（全部一致）
查不到             75             **0**
两源冲突            1             1（仍是 024 那个）
```

## 判据
| ID | 判据 |
|---|---|
| SC-2201 | 门禁读**≥2 份**转储并合并 |
| SC-2202 | ★ **`sws*` 能查到**：`swsAnalysisStudyTypeBuckling == 2`，且记下来自 cosworks |
| SC-2203 | 合并时**先出现的赢**（冲突时行为确定）|
| SC-2204 | 实跑 **0 条查不到**，且仍报得出 024 那处冲突 |
| SC-2205 | 全拿不到转储时 **SKIP exit 0**（便携性）|
| SC-2206 | 门禁 + 回归不退化（回归 **1074 passed**）|

## ⚠ 本轮自己踩的坑
改 `gate-classification.json` 时把 Windows 路径写进 JSON 字符串
⇒ **非法转义 `\e`** ⇒ JSON 解析失败 ⇒ `gate_wiring` / `release_check` 连着红。
⇒ 改用正斜杠。★ 教训：**往 JSON 里塞 Windows 路径要先想转义**。
