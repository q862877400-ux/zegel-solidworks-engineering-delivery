# Checklist · Feature 133 读文件自定义属性

> 宪法 §I–§V 的可勾项。**勾选前必须真的跑过那条命令。**

## §I 来源
- [x] `spec.md` 每条需求（R1–R7）都写了来源
- [x] 来源分四类之一：官方文档 / 官方示例 / 四家外部 MCP / 本项目既有模式
- [x] ★ 本特性**没有**用四家外部项目代码（只用官方文档 + 官方示例 + 本项目）

## §II 官方源与裁决顺序
- [x] `plan.md` 列了官方源与**冲突裁决顺序**（出厂类型库优先）
- [x] ★ 三处"文档说了但不够用"的地方**逐条列出**并给出实测补齐（`kind: property` 实际是方法 ·
      Obsolete 的 `Get` 反而可用 · out 在 pywin32 下不通）

## §III 查不到就说查不到
- [x] 官方**没说** `CustomPropertyManager` 要不要参数 ⇒ 用实测定（**必须传配置名**）
- [x] 官方**没说** by-ref out 在 pywin32 下的表现 ⇒ 用实测定（**报类型不匹配**）
- [x] `IsCustomPropertyEditable` **实测没读到** ⇒ ★ **如实留 `null`** 并写进 limitations，不假称能读

## §IV 许可
- [x] 每个来源行带 license：全是「官方 API/示例」或「本项目（MIT）」
- [x] 无 AGPL / GPL / 无许可代码进入 ⇒ 本特性**不产生新的 NOTICE 义务**
- [x] ★ **没有**动用 `sw_pdm`（那是另一族，需 PDM 许可证）

## §V 可跑的验收
- [x] `tasks.md` 每条任务都带 `→ 验收:`，且是**能跑出绿的命令**
- [x] 验收①（静态）：`all_specs()` ⇒ 67
- [x] 验收②（★ 真机）：`output/custom-property-evidence.json` 的 `verdict == "pass"`
- [x] ★ 真机证据含**决定性用例**（先写再读回）+ `count_read == count_reported` + **两个负例**

## 纪律
- [x] 完成的特性目录**不可变**（后续需求开新号）
- [x] 本文件**不写**当前进度 / 不重述六条铁律 / 不重述已知事实
- [x] 门禁链八条 exit 0；全量 `pytest` 0 failed
- [x] 无人值守基线**只加一条**（不重生成 ⇒ 不吸收别的漂移）
- [x] 两仓库各自 commit，**未 push**
