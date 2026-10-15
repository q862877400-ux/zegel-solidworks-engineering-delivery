# 222 · 实施计划

## 技术选择

只改三个既有文件 + 新增一个测试文件，全部离线：

```
scripts/sw_sketch_relations.py        # RELATION_TYPES 数值正名 + 反别名 + 未决登记
scripts/sw_part.py                    # _SG_RELATIONS 去非官方名 + add_sketch_relation 前置门
mcp-server/tool_specs_batch16.py      # solidworks_add_sketch_relation 参数描述正名
tests/test_relation_enum_alignment.py # 新增：枚举对齐 + 公开面 + 前置门负例
```

沿用 221 的测试技术选择：受管 Python 3.13.12、标准库 `unittest`、`importlib` 加载目标模块、假宿主隔离真实 COM。本机无 `pytest` / `pydantic`，不安装、不依赖。

**不做**：不改 `specs/221-*/`（Flow-forward：完成目录不可变）、不改 `capabilities.yaml` 的 `level`、不改注册表计数、不碰 COM、不跑收尾链全量门禁（该链含 `git add` 与关闭 SW 副作用，须另行授权）。

## 官方源与裁决顺序

按宪法 §II（铁律 4：签名三源互证，冲突以出厂类型库为准）列出本特性要查的源：

| 源 | 路径 | 本切片用它裁决什么 | 许可 |
|---|---|---|---|
| 结构化 markdown | `C:\swapi\enums\swConstraintType_e.md`（86 项） | 枚举名与数值 | reference-only |
| CHM 解包 | `D:\AI\SW\AI Solidworks\官方文档\SWhelp\swconst\...swConstraintType_e.html`（86 项） | 交叉确认同一批数值 | reference-only |
| 出厂反射转储 | `D:\AI\SW\_raw\enum_values_sldworks.txt`（`## swConstraintType_e` 段） | 第三源确认；冲突时的裁决者 | reference-only |
| 成员页 | `C:\swapi\types\IModelDoc2\SketchAddConstraints.md` | 合法字符串清单（唯一权威） | reference-only |
| 官方例 | `C:\swapi\examples\Constrain_Sketch_Example_CSharp.md` | 调用序与真实用名 | reference-only |
| 本仓既有模式 | `scripts/sw_sketch_relations.py`、`scripts/sketch_relations.py`、`sw_part.py`、`specs/221-*` | 复用结构、命名、返回契约与状态门 | MIT |

三处枚举源已逐项比对一致（86/86），故本切片无需走「出厂类型库推翻文档」的分支；若后续发现第四处源与这三处冲突，按铁律 4 停在登记、不自行裁决。

## 关键设计决定

**① 正名而不是补丁。** `RELATION_TYPES` 的 11 个键里 10 个数值错、2 个名字官方不存在。不做「只改被怀疑的那几个」——整表按官方重写，并写一个**逐项断言测试**钉住，让下一次改错能被静态抓住（SC-001 的负例就是为此）。

**② 别名方向必须是「错名 → 官方名」。** `EQUAL` 与 `MIDPOINT` 是用户和旧提示词里已经写下的词，直接删掉会让既有调用从「静默无效」变成「突然报错」——方向对，但要在拒绝信息里给出官方对应名（`SAMELENGTH` / `ATMIDDLE`），使纠错成本从「查文档」降到「照抄」。别名解析的**输出**永远是官方成员名。

**③ 未决项显式登记、拒绝派发。** 两份表里原注释自称 `swConstraintType_XXX` 但数值与官方不符的项（如 `tangent: 21` vs 官方 `TANGENT=6`、`equal: 3`）。这类项的正确对应本切片无法从三源唯一确定，因为官方枚举里同族有多个候选（`TANGENT=6` / `TANGENTFACE=63`、`SAMELENGTH=14` / `SAMECURVELENGTH=85` / `SAMESLOTS=75`）。按铁律 5，**登记为未决 + 禁止派发**，不猜数字。

**④ 公开面同步，且前置门不做成第二套。** `solidworks_add_sketch_relation` 是用户唯一入口，其参数描述必须只留官方名。它的前置门与 221 的 `_status(model) == 2` 判断**同源同义**：直接复用同一判据，不复制逻辑、不放松条件。走字符串路径（`SketchAddConstraints`）时同样"改前先验状态、改后至多一次、不重放"。

## 宪法与批准边界

- §I 每个 FR 有来源与许可（见 spec.md 表格）。
- §II 上方源表已列，裁决顺序已写明。
- §III 未决项写成「查不到并登记」，无「应该有」式臆造。
- §IV 全部来源为 reference-only 或本仓 MIT，无第三方代码引入，`THIRD-PARTY-NOTICES.md` 无需变更。
- §V 每个任务带可跑的离线命令。
- Flow-forward：新开 `specs/222-*`，不改 `specs/221-*`；状态写在 `capabilities.yaml` 与 ROADMAP 游标。

**未授权**：COM / 真机 / 部署 / 提交 / 发布 / 关闭用户文档 / 全量门禁链。本切片只到「离线回归绿 + 边界登记完整」。

## 写入/验收

测试**先红后绿**：新增用例在改实现前必须至少失败 1 次（SC-005），否则说明用例没抓到缺陷。收尾核对实际改动与游标，交付简报里逐条列未过门。

## Project Structure

```text
scripts/sw_sketch_relations.py         # 改：RELATION_TYPES 正名、反别名、未决登记
scripts/sw_part.py                     # 改：_SG_RELATIONS 正名、add_sketch_relation 前置门
mcp-server/tool_specs_batch16.py       # 改：参数描述只留官方名
tests/test_relation_enum_alignment.py  # 新增：本切片全部判据
specs/222-relation-enum-and-public-contract/{spec,plan,tasks,acceptance}.md
```

**Structure Decision**：单项目结构，沿用本仓既有落点（铁律 3）—— 能力实现进 `scripts/`，工具声明进 `mcp-server/`，测试进 `tests/`，规格进 `specs/`。不新建顶层目录。
