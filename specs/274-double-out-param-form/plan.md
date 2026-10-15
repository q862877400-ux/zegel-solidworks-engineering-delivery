# Plan — `Double&` 出参不吃 by-ref VARIANT

**Feature**: `specs/274-double-out-param-form/`
**日期**: 2026-10-10
**上游**: `specs/273-out-params-three-types/`

---

## 一、一句话

★ 用一个**只读真机探针**，把「`Double&` 出参怎么传」量出来，★ 并**把结论钉进判据**。

---

## 二、靶子怎么选的（★ 关键：★ 要「可达 + 同形」）

| 需求 | 靶子 A | 靶子 B（判别器） |
|---|---|---|
| 方法 | `IBody2::GetExtremePoint` | `IModelDocExtension::GetWhatsWrong` |
| 出参 | **3 个 `Double&`** | **3 个 `Object&`** |
| 可达性 | ★ 任何有实体的零件 ⇒ ★ 用夹具 `刀柄_Holder.sldprt` | ★ 任何文档 ⇒ ★ 同一份夹具 |
| 为什么选它 | ★ **3 个 `Double&`** = 与 `GetNodeLocation` **同形** | ★ 253 **已验**它吃 by-ref VARIANT ⇒ ★ 拿来当**对照** |

★ **为什么必须有靶子 B**：★ 只有 A ⇒ ★ 分不清「是 `Double&` 的问题」还是「是 `IBody2` 的问题」；
★ 有了 B（同机、同文档、`Object&`）⇒ ★ 把变量**收敛到「形参类型」**上。

---

## 三、步骤

| # | 步骤 | 产出 |
|---|---|---|
| S-1 | 查本仓 4 个 out 包装器**各自有没有真机证据** | ★ `out_double`/`out_bstr` **只有类推** |
| S-2 | 写只读探针（★ 走 `tools/sw_guard.py`） | `output/_probe274_double_out.py` |
| S-3 | 靶子 A 逐 5 形态实测 | ★ by-ref VARIANT **抛 TypeError**；裸值/省略 **通过** |
| S-4 | 靶子 B 逐 3 形态实测（★ 判别器） | ★ **只有** by-ref VARIANT 通过 |
| S-5 | 把读数钉进判据（★ 先红后绿） | `tests/test_double_out_param_form.py` |
| S-6 | ★ 把结论写回**用它的地方** | `scripts/sw_sensor.py` 的 `out_double` 注释 |
| S-7 | 生成器链（★ 改了 `scripts/`）+ 门禁全套 | `output/_gate274.log` |

---

## 四、风险与对策

| 风险 | 对策 |
|---|---|
| ★ 只测一个接口 ⇒ 结论**过宽** | ★ **加判别器**（同机同文档的 `Object&`）⇒ 变量收敛到**形参类型** |
| ★ 结论**过窄**（只在 `IBody2` 成立） | ★ 判据里**如实标注**「cosworks 上的 `Double&` 仍未见正例」 |
| ★ 凭类推改 `out_double` | ★ **不改行为** —— ★ 只写「未验 + 有同族反例，用前先核」（★ 本仓纪律「不凭类推」） |
| ★ 真机探针留残留 | ★ 只读打开 · `finally` 里 `CloseDoc(GetTitle)`（★ **属性不加括号**）· ★ 护栏预检「0 个文档」 |
| ★ 判据首跑全绿 = 可疑（★ 铁律 16） | ★ **四组负例**（★ 含「把疑点谎报为已验」） |
| ★ 判据比对**手抄常量**（★ 铁律 6） | ★ **回源码核**包装器形态（★ `_helper_variant` 读 `scripts/*.py`） |

---

## 五、不做

- ★ 不改 `out_double` 的**形态**（★ 没直接验 `GetSensorValue` ⇒ ★ 凭类推）。
- ★ 不改 12 条的表（★ 本轮只解决**前置**）。
- ★ 不新增/修改任何 hook（★ 业主明令）。
- ★ 不 `git commit` / `push`（★ 红线）。
