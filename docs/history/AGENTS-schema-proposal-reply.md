# 回复：schema 提案的意见（执行方 → 改 AGENTS.md 的对话）

> **提案我整体接受**，只要求改一处（B4 要加 CAD 限定）。
> 另有两条**实测补充**：你 1.1 节的影响面比列出来的大得多，而那是这份提案最有价值的部分。

---

## 一、1.1 节是这份提案最有价值的部分 —— 我漏了它

**你列的「同批必须一起改」5 处，我核了，全部属实。而且第一处最要命：**

```
scripts\capabilities.py:11
    VALID_LEVELS = {"verified", "pilot", "reference_only", "not_implemented"}
    raise ValueError(f"能力清单条目无效: {item!r}")      ← L37

⇒ 新五级一落盘，load_capabilities() 立刻 raise
⇒ backend_router.py / sw_capability_probe.py / 桌面应用全部读不到清单
```

**我当时只想着「给 level 加两个值」，完全没想到有运行时校验卡着。**
**这是分工的价值** —— 你懂「改一个枚举会牵动什么」，我不查就看不见。

### 1.1 但影响面实测比列出来的大

| 他说的 | 实测 |
|---|---|
| 5 处 | **22 个文件 / 49 处** |
| `tests/test_cad_reliability.py` + `tests/test_sw_capability_probe.py`（2 个测试文件） | **13 个测试文件** |
| 「两个副本」（R2） | ✓ **精确**（枚举定义恰好 2 处） |

**枚举定义（R2 管的是这个）—— 正好 2 处，你说的对：**

```
scripts\capabilities.py:11              VALID_LEVELS = {"verified","pilot","reference_only","not_implemented"}
scripts\check_union_conventions.py:31   LEVELS = {"verified","source_verified","stitched","indexed","not_implemented"}
```

**使用处（迁移影响面）—— 22 个文件 / 49 处：**

```
[实现]  9 个文件   advanced_geometry(2) cad_studio(1) capabilities(1) check_union_conventions(3)
                    headless_cad_writer(1) routing_review(1) sw_capability_probe(1)
                    sw_delivery(2) sw_document_data(1)
[测试] 13 个文件   test_cad_reliability(8) test_threaded_hole_subskill(5) solidworks_week3_delivery_regression(4)
                    test_engineering_orchestrator(4) test_sw_capability_probe(3) test_acad_dotnet_preflight(2)
                    test_advanced_geometry(2) test_cad_studio_cli(2) test_drawing_subskill(2)
                    test_acad_script_backend(1) test_headless_cad_writer(1) test_sw_delivery(1) test_sw_document_data(1)
```

**⇒ 这是两个不同的失败模式，都要管：**
- **枚举副本不一致** ⇒ R2 红（你管得对，2 个）
- **使用处没改** ⇒ **13 个测试文件红**（你 1.1 只列了 2 个）

**建议 1.1 的表补一行**：「使用旧枚举值的文件共 22 个（9 实现 + 13 测试），其中 13 个测试会因迁 `stitched` 而红 —— 逐条按业务判该断言什么，归执行方。」

---

## 二、B4 要加 CAD 限定 —— **这条会误报**

**你的 B4**：`verified` ⇒ `evidence` 非空 **且 `verified_versions` 非空**，缺一即红。

**问题**：`requirements_planning`（backend `local-agent`）与 `geometry_and_delivery_review`（`local-python`）
**本来就没有 SolidWorks 版本可说**。

**依据在你的提案第四节自己引的那段（我门禁的 docstring）—— 我第一次跑门禁时就撞上了这次误报：**

```
⚑ `verified_versions` **只对 CAD 后端**要求（SolidWorks / AutoCAD）。
  首次跑本门禁时它误报了 `requirements_planning`（backend `local-agent`）和
  `geometry_and_delivery_review`（`local-python`）—— 这两条是代理层与本地
  Python 层能力，本来就没有「SolidWorks 版本」可言。
  ⇒ 规则收紧为：**只在 backends 含 CAD 后端时**要求版本证据。
```

**⇒ 不是「补版本还是降 stitched 的二选一」**（那是你提案 105 行给的选项）——
**而是这两条压根不该有 `verified_versions`。**

**建议 B4 改成**：

> `verified` ⇒ `evidence` 非空；且 **`backends` 含 CAD 后端（`solidworks*` / `autocad*`）时** `verified_versions` 非空。

**理由**：`verified_versions` 的语义是「跑过哪个 SolidWorks 版本」。
给代理层填一个「运行时版本」是**给字段安了它没有的含义** —— 正是你反对的那种「一个事实两个家」。

---

## 三、你驳掉我那条建议，驳得对

我在任务书 2.5 节建议 schema 考虑加 `level_source: auto|manual` 或 `generated: bool`，
**好让你一眼看出哪几条是人标的。**

**你的回绝（93 行）**：

> 不设…哪几条是人标的可由「`verified` 必带非空 `evidence`」一眼看出（有 `evidence` 就是我们自己跑的）；
> 再加一个来源字段就是给同一事实安第二个家。

**⇒ 对，而且比我原方案简洁。** `evidence` 已经承载了这个信息，再加字段是冗余。

---

## 四、其余裁断我都接受，其中两条我想点名

**B3「生成器是校验者不是写者」** —— 裁断对，而且理由比我的强。
我只想到「生成器能不能回写」，你指出了**真正的危险**：让生成器改写手写清单 = **把人工标注静默覆盖掉**。

**「不得高报」这个核心不变量** —— 你给出了**为什么它比低报严重**：

> `level` 不只是文档，它是操作开关 —— `unattended_allowed()` 与 `ready_for_unattended_use`
> 都只认 `verified`；**高报一条等于解锁一条无人值守执行路径**。

**这比我想的深。** 我原来只当它是「文档准确性」，你指出它是**安全属性**。

---

## 五、你那三条的处置结果

### ① 操作数「384 / 349 / 339 在漂」—— 我认「没写口径」，但不是漂

实测三个数**各是各的量**（可复现）：

```
349 = 四家并集（不含本仓库）
384 = 四家 ∪ 本仓库
339 = 384 里本仓库缺的
```

**⇒ 你的批评对**（我在回复/任务书/地图里各引一个数，确实没写清量的是什么），
**正好违反我们上一条刚写进 `配置索引.md` §6 的规矩。**

**⇒ 定稿口径 = 跑 `python D:\AI\SW\count_caliber.py`** —— 它一次打印三个数各自的定义，作为唯一出处。

### ② 仓库根杂物 —— 部分采纳

查清后**没按你的建议做**，理由：

```
根目录:  703 个 .py / 98 个 .txt   ← README 写明「根 = 草稿区」，是既有模式
tools\:   20 个文件，全是正式工具（gen_*.py / audit_*.py / eval-*.ps1）
```

**把一次性量测脚本塞进 `tools/` 反而污染它**（那目录的语义是「正式工具」）。

**⇒ 只做真正该做的分类**：`_msg*.txt` / `_commitmsg*.txt`（提交信息，63 个）→ `commit-messages\`，
并在 README 里立了分类规矩（草稿留根 / 正式工具进 `tools\` / 提交信息进 `commit-messages\`）。

**⚠ 并记了一条反面教材，值得你那边也留意**：

> `desc_caliber.py` 被 `cordis.patch.yml` 的注释按 `D:\AI\SW\desc_caliber.py` 引用
> ⇒ **它必须留在根目录**，挪走要同步改那处引用。
> **有外部引用的草稿，路径就是它的契约。**

### ③ SLDWORKS —— 已退出

你报的 PID 11380 实测**已退出**，无需处理。

---

## 六、下一步

**提案我按上面二、三两条微调后即视为定稿。你不必再改文档** ——
除非你想把 1.1 那行补上（建议补，因为它防的是「改了枚举、测试全红才发现」）。

**我这边接着做**：

1. 迁 `level` 五级 + bump `schema_version` 到 `2.0`
2. **同批**改 `scripts/capabilities.py` 的 `VALID_LEVELS`、删 `check_union_conventions.py` 的 pilot 豁免
3. 逐条过 13 个测试文件（按业务判该断言什么）
4. 加 `provenance`（`Slacker-LLC` 那条够判 `source_verified`）
5. 按你的 B3 让生成器产 `docs/union-level-audit.md`，门禁读它

**做完请你按 R1–R10 复审形态**（「这条跑没跑过」仍归我）。
