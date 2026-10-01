# 026 · Converge

**Converged**: 2026-10-01（轮 107）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-2201 读 ≥2 份转储并合并 | ✅ 合并 **10,588** 个成员 |
| SC-2202 `sws*` 能查到 | ✅ `swsAnalysisStudyTypeBuckling == 2`，来源记为 cosworks |
| SC-2203 合并优先级确定 | ✅ 先出现的赢（测试钉住）|
| SC-2204 实跑 0 条查不到 + 仍报 024 冲突 | ✅ **90 条全部一致** · 1 处冲突 |
| SC-2205 拿不到转储则 SKIP | ✅ |
| SC-2206 门禁 + 回归 | ✅ `release_check` exit 0 · **1074 passed** |

## 二、★ 这一轮把「未查证」兑现成了「查清」
`025` 结束时写的是：
> **75 条"查不到"未逐条核** —— 多半来自 `swsimulation` 程序集（不在本转储里），
> **未验证**是否有对应的反射源可查。

本轮查清：**有** —— 它们在 **cosworks.dll**，而对应的转储**早就存在**。
★ **⇒ 那句"未查证"里藏着一个错误前提**：我当时猜是 `swsimulation`（其实没有这个程序集名），
真正的程序集是 **cosworks**（Simulation 的前身叫 COSMOSWorks）。
**猜测写进"未查证"里，读起来像事实。**

## 三、门禁现在的覆盖（可复算）
```
2 份转储 · 10,588 个成员 · 代码里 90 条「值 + 官方成员名」
  ├─ 90 条与出厂反射一致
  ├─  0 条查不到
  └─  1 处两源冲突（swSketchChamfer_DistanceDistance：反射 1 · md −1）
```
⇒ **代码里每一个写了官方成员名的枚举值，现在都有据可查、且都对。**

## 四、⚠ 本轮自己踩的坑
改 `gate-classification.json` 时把 Windows 路径 `reflect\enum_cosworks.txt` 写进 JSON 字符串
⇒ **非法转义 `\e`** ⇒ JSON 解析失败 ⇒ `gate_wiring` 与 `release_check` **连着红两次**。
⇒ 改用正斜杠。★ **往 JSON 里塞 Windows 路径要先想转义。**

## 五、未查证
* 门禁**不判**「成员名挂的是不是对的枚举」，也**不判**值的语义；
* **还有没有别的程序集**的枚举被我们用到了（本轮只解决了 sldworks + cosworks 两个）；
  其余 interop 程序集（`swmotionstudy` / `swdocumentmgr` / `swdimxpert` / `dsgnchk` /
  `fworks` / `sldcostingapi` / `SWRoutingLib` …）**未逐一检查是否有对应转储**。
