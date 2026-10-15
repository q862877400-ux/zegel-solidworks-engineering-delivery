# Plan — 给「`CreateFeature` 回 `None`」找到能报错的入口

**Feature**: `specs/276-createfeature-error-entry/`
**日期**: 2026-10-10
**上游**: `specs/263-base-flange-failure-layers/`

---

## 一、一句话

★ 263 自己留了下一步（★「先找能报错的入口」），★ **三轮没人做** ⇒ ★ 本轮做，★ 并**一次读到底**。

---

## 二、口径（★ 铁律 46：口径要么 `import` 要么逐字抄）

| 项 | 做法 |
|---|---|
| **入口怎么选** | ★★ **先读官方页**（★ `C:/swapi/types/<接口>/<成员>.md`）⇒ ★ 按 **Remarks** 判适用性（★ 不猜） |
| **复现 setup 怎么来** | ★ 逐字照 `tests/solidworks_sheet_metal_regression.py`（★ 新零件 + Front Plane + 3 条线 + `create_base_flange`） |
| **读栈时机** | ★★ **先清一次栈**（★ 官方：读完即清）⇒ ★ 再触发失败 ⇒ ★ **立刻**读 ⇒ ★ 读数才干净 |
| **官方序列对照** | ★ 逐字读 `Create_Base_Flange_Feature_Example_VBNET.md` |

---

## 三、步骤

| # | 步骤 | 产出 |
|---|---|---|
| S-1 | 搜「报错入口」候选（★ 反射 + 官方页） | ★ 3 个候选 |
| S-2 | ★ 逐条读**官方 Remarks** 判适用性 | ★ 只剩 `GetErrorMessages` |
| S-3 | 写只读探针（★ 走 `tools/sw_guard.py`） | `output/_probe276_error_entry.py` |
| S-4 | ★ 清栈 → 触发失败 → **立刻**读栈 | ★ **真因可读** |
| S-5 | 顺带实测另两个入口（★ 留证） | ★ 一个报类型不匹配 · 一个空 |
| S-6 | 读官方示例，逐字对比 | ★ **两条关键差异** |
| S-7 | 判据（★ 先红后绿） | `tests/test_createfeature_error_entry.py` |
| S-8 | 门禁全套（★ 只改 `tests/` ⇒ **不跑生成器链**） | `output/_gate276.log` |

---

## 四、风险与对策

| 风险 | 对策 |
|---|---|
| ★ 拿一个**只对特定特征有效**的入口当通用入口 | ★★ **先读官方 Remarks** ⇒ ★ `GetCreateFeatureErrors` 只对 **Mate Controller** ⇒ **排除**（★ 并把理由逐字记进判据） |
| ★ 读到**上一次**失败的消息（★ 栈里有历史） | ★ **先清一次栈**（★ 官方：读完即清）⇒ ★ 后面的读数才是本次的 |
| ★ 消息里带**会变的**文档序号（`零件11`） | ★ 判据只钉**稳定子串**（`所选的草图对此操作无效`） |
| ★ 真机探针留残留 | ★ `finally` 里 `CloseDoc(GetTitle)`（★ **属性不加括号**）· ★ 护栏预检「0 个文档」 |
| ★ 判据首跑全绿 = 可疑（★ 铁律 16） | ★ **五组负例** |

---

## 五、不做

- ★ 不改 `scripts/`（★ 所以**不跑生成器链**）。
- ★ 不修 `create_base_flange`（★ 修法 = 按官方序列对齐 ⇒ ★ **另开切片** + 真机验）。
- ★ 不新增/修改任何 hook（★ 业主明令）。
- ★ 不 `git commit` / `push`（★ 红线）。
