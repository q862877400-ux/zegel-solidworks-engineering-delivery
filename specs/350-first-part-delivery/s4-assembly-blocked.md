# S4 前置：装配创建被 `AddComponent5` 阻塞（真机实测）

**日期**: 2026-10-25

**探针**: `tools/probe_s4_assembly_create_and_interference.py` ·
`tools/probe_add_component_diagnose.py`

**起因**: `capabilities.yaml` 里 `assembly_and_mates` 一直是 **`stitched`（从未真机跑过）**，
而 E4（装配自由度闭合）要求「配合约束表达 + 干涉 0 + 关键间隙」——
**连装配都建不出来，E4 的真机验证就无从谈起**。

★ 这一项**不需要** S2 的八项首件要求（材料/载荷/安全等级…）——
  配合与干涉是**几何**判据，与材料载荷无关。所以可以做。

---

## 一、做到哪一步

| # | 步骤 | 结果 |
|---|---|---|
| ① | 新建装配文档 | ✅ **成功**（`title='装配体1'`、`GetType=2`） |
| ② | 加组件（`AddComponent5`） | ❌ **回 `None`**，组件数 0 |
| ③ | 读回组件数 / 配合数 / 干涉数 | ✅ 读取路径本身可用（读到 0、0、0） |
| ④ | 加配合（mate） | ⬜ 未做 —— ② 不通就到不了 |

## 二、`AddComponent5` 回 None：三种前置都排除了

| 假设 | 怎么排掉的（真机读数） |
|---|---|
| 零件路径看不到 | `os.path.exists`=**True**、大小 **78351** 字节 |
| 文档类型不对 | `GetType` = **2**（`swDocASSEMBLY`） |
| 装配不是活动文档 | `ActiveDoc` 的 title 与装配一致 ⇒ `is_active=True` |
| 参数取值非法 | `ConfigOption=0` 已核 = `swAddComponentConfigOptions_CurrentSelectedConfig`（**合法**） |
| 装配未保存 ⇒ 无相对路径基准 | `SaveAs` **成功**、`GetPathName` 有值，**保存后再加仍回 `None`** |

真机原始返回：

```
④ AddComponent5 原始：ok=True type=NoneType repr=None
⑤ 开零件+激活装配后再加：activate=False active='plate_diag__1.SLDPRT' add5=None
⑥ 保存装配：ok=True path=...\asm_diag.SLDASM
⑦ 保存后再加：add5=None
⑧ 组件数=0
```

⇒ 按「**三次失败就停下质疑架构**」的纪律：**停止试变体**，记为阻塞，**不猜原因**。

## 三、★ 另记一条 API 契约问题（差点误读）

`sw_assembly.add_component()` 在失败时**回 `None` 而不抛异常** ⇒
用 `try_call` 包它会得到 `(True, None)` —— **看着像成功**。

第 22 轮第一次跑，我的探针就把 `ok1/ok2` 读成了 `True`。

⇒ 判据必须**回读组件数**，不能看返回值。
  这与事实 560（`save_document` 报 True 却没落盘）、
  事实 561 同族：**返回值和实际结果不一致**。

## 四、E4 的判定器本身是好的（顺带核实）

我一度差点把「空装配上干涉检测回 `status: pass`」当成 E4 通过。核实后：

`judge_assembly_interference` 的第 ② 条是「**必须有真实功能配合（全固定不算）**」——
空装配 `mates=0` ⇒ 判 **fail**，走不到「干涉为 0 ⇒ pass」。

⇒ 判定器没问题；问题是**原始检测报告不是判定结论**。
  把 `sw_assembly.get_interference_detection()` 的 `status` 当结论读，就会误判。

## 五、结论与下一步

| 项 | 状态 |
|---|---|
| 装配文档创建 | ✅ 可用 |
| **加组件** | ❌ **阻塞**（`AddComponent5` 回 None，三种前置已排除） |
| 组件/配合/干涉读取 | ✅ 路径可用（空装配上读数正确） |
| E4 判定器 | ✅ 结构正确（要求 `mates ≥ 1`，空装配不会误绿） |
| `assembly_and_mates` | 仍 **`stitched`** —— 已把上述读数写进 `limitations` |

**E4 的真机验证开不了工**，除非 `AddComponent5` 能通。已记入 `dead-ends.md`（78 条）。

★ 与 S3 的 E2 是同一类阻塞：**卡在工具链，不在设计**。
  两者都不该靠「换个手法再试」解决 —— 已各排除多条路径，再试是浪费。
