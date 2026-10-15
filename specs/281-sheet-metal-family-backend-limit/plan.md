# Plan — 同族的 `AccessSelections` 逐个测

**Feature**: `specs/281-sheet-metal-family-backend-limit/`
**日期**: 2026-10-10
**上游**: `specs/280-edge-flange-backend-limit/`

---

## 一、一句话

★ 280 只验了**一个**常量（37）⇒ ★ 本轮把**同族的其余三个**逐个测 ⇒ ★ **看是不是整族同一个因**。

---

## 二、口径

| 项 | 做法 |
|---|---|
| **测什么** | ★ `CreateDefinition(const)` 拿到的 FeatureData ⇒ `AccessSelections(model, 空 Dispatch)` |
| **为什么只测这一形态** | ★ 280 已证：★ 空 Dispatch 才回 `0x80010105`（★ `None` / `False` 是类型不匹配） |
| **常量从哪来** | ★ 逐字从 `scripts/sw_sheet_metal.py`（35 / 37 / 117 / 118） |
| **「同族」怎么定** | ★★ **按路径**：★ 走 `CreateDefinition` + `CreateFeature` 的才算（★ `create_hem` 走 `Insert*` ⇒ 不算） |
| **「表订正了没」怎么核** | ★★ **回源码核** `SHEET_METAL_RUNTIME_STATUS` 的**那一条**（★ 按 key 取块） |

---

## 三、步骤

| # | 步骤 | 产出 |
|---|---|---|
| S-1 | 对照：常量 37（280 已定案） | ★ `-2147417851` |
| S-2 | 常量 35 / 118 / 117 逐个测 | ★ **全部 `-2147417851`** |
| S-3 | 记 `hasattr(AccessSelections)` | ★ **全 True** ⇒ 方法**在** |
| S-4 | ★ 判据（★ 先红后绿） | `tests/test_sheet_metal_family_backend_limit.py` |
| S-5 | ★ 订正状态表**三条**（★ 旧结论留档） | ★ `scripts/` 改动 |
| S-6 | 生成器链 + 门禁全套 | `output/_gate281.log` |

---

## 四、风险与对策

| 风险 | 对策 |
|---|---|
| ★ 只测一个常量就推广到整族 | ★★ **四个都测**（★ 一次一个） |
| ★ 把 `create_hem` 也算进这一族 | ★★ **按路径分层** —— ★ 它走 `Insert*` ⇒ **不算**（★ 判据里显式断言） |
| ★ 把 `hasattr=True` 误读成「能用」 | ★★ 判据把**两件事**分开：★ 方法**在**（`hasattr`）· ★ 但**调用失败**（hresult） |
| ★ 把 `0x80010105` 的负数写错 | ★★ 判据里**显式断言** `-2147417851 + 2**32 == 0x80010105` |
| ★ 真机探针留残留 | ★ `finally` 里 `CloseDoc(GetTitle)` · ★ 护栏预检「0 个文档」 |
| ★ 判据首跑全绿 = 可疑（★ 铁律 16） | ★ **六组负例** |

---

## 五、不做

- ★ 不改任何 `create_*` 的实现（★ 后端限制）。
- ★ 不验 `create_hem` 的 5 形态（★ 它走另一条路 ⇒ 独立一件工作）。
- ★ 不新增/修改任何 hook（★ 业主明令）。
- ★ 不 `git commit` / `push`（★ 红线）。
