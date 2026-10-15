# tasks 233 —— 去重口径修正（任务清单）

> ★ 每条都带**可复制执行**的验收命令。全部离线。

## T1 · 量测（先量，不动实现）

- [x] T1.1 逐调用点明细 + 桶归属
  `C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B output/_probe233_buckets.py`
  ⇒ `distinct sites 85 · buckets 合计 91 · 被 >1 个 def 命中 6`
- [x] T1.2 诊断重复计数（逐点桶归属）
  `… -B output/_probe233_dup.py`
  ⇒ `('local','param') 3 · ('local',) 46 · ('param',) 34 · ('computed',) 2`；
  `修正口径 {param 37, local 46, computed 2} = 85`
- [x] T1.3 去重口径全量读数（含 `visible`）
  `… -B output/_probe233_final.py`
  ⇒ `visible 1185（报 1219，虚增 34）· 不可见 85（报 91，虚增 6）· 合计 1270（报 1310）`
- [x] T1.4 候选集可枚举性（宽读取器）
  `… -B output/_probe233_wide.py`
  ⇒ `可枚举 39/46 · 仍不可枚举 7 · 候选值 distinct 135`
- [x] T1.5 `def` 外调用点普查
  ⇒ **0 处**（潜在盲区、无靶子 ⇒ 只登记）

## T2 · 判据先写、并确认能红

- [x] T2.1 新增 `tests/test_dispatch_call_site_dedup.py`（6 例）
- [x] T2.2 **红基线**：把去重那行删掉的**副本**跑同一夹具
  ⇒ 旧口径 `可见 = 2`（新口径应为 `1`）· 见 `acceptance.md` §三
- [x] T2.3 断言本体承重：`bucket_consistency({"param":37,"local":52,"computed":2}, 85)` ⇒ 非 `None`

## T3 · 改实现

- [x] T3.1 `scan()` 建 `innermost` 映射 + 非最内层 `continue`
- [x] T3.2 新增 `bucket_consistency(buckets, nonliteral)` 并在 `main()` 里接成违规项
- [x] T3.3 `BASELINE_INVISIBLE` 91 → 85 · `BASELINE_VISIBLE` 1219 → 1185
- [x] T3.4 文件头读数表按去重口径订正

## T4 · 接线与同步

- [x] T4.1 `tests/test_dispatch_entry_guard.py` 下界 1219→1185 · 91→85
- [x] T4.2 `tests/test_dispatch_resolution.py` 基线串 → `37,85,1185,…`
- [x] T4.3 `docs/gate-classification.json` 的 `reason` 追加 spec 233 订正段（`classification` 仍 43）
- [x] T4.4 `docs/ROADMAP.md` §一 追加 233 游标
- [x] T4.5 `.specify/feature.json` → `specs/233-dispatch-callsite-dedup`

## T5 · 验收（全部可复制）

- [x] T5.1 门禁本体（真树）
  `… 3.13.12 -B scripts/check_dispatch_entry_guard.py` ⇒ `可见 1185 · 不可见 85（37 / 46 / 2）· exit 0`
- [x] T5.2 新判据
  `… 3.13.12 -B -m unittest tests.test_dispatch_call_site_dedup` ⇒ `Ran 6 tests · OK`
- [x] T5.3 229–232 + 233 合并回归
  `… 3.13.12 -B -m unittest tests.test_dispatch_entry_guard tests.test_dispatch_resolution tests.test_dispatch_byref_guard tests.test_dispatch_blindspot_guard tests.test_dispatch_call_site_dedup`
  ⇒ `Ran 56 tests · OK`
- [x] T5.4 门禁全套（★ 必须 3.14.7）
  `C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B scripts/release_check.py` ⇒ `EXIT 0`
- [x] T5.5 收尾链
  `pwsh -File D:\AI\SW\tools\round_chain.ps1 -Tests tests/test_dispatch_call_site_dedup.py`
