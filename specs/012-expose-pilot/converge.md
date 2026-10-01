# 012 · Converge

**Converged**: 2026-10-01（轮 90）

## 结果
| 判据 | 结论 |
|---|---|
| SC-801 声明 5 条、全 `solidworks_` 前缀 | ✅ |
| SC-802/803 指向真实函数、参数在签名里 | ✅（契约测试 **18 passed**）|
| SC-804 已接入 `BATCH_MODULES` | ✅（`all_specs()` 20 → **25**）|
| SC-805 暴露面 72 → **77** | ✅ |
| SC-806 缺口 339 → **338** | ✅（**首次下降**）|
| SC-807 门禁 + 回归 | ✅ `release_check` exit 0 · **988 passed / 0 failed** |

## 不符合项 / 实测记录
1. **两处门禁红都是"改了东西没同步"**：`check_union_conventions`（地图未重生成）、
   `check_report_freshness`（数字未同步）—— 都是**正常流程**，非缺陷。
2. **一处测试红是设计意图**：`test_expected_batch_size` 钉死批次数 20 ⇒ 加批次必须改它。
   **已改成 25 并写明"这是它的设计意图：让悄悄多注册工具这件事可见"**。

## 未查证
* **5 个工具的**真机行为**未测**：契约测试只核「声明 vs 签名一致」，**不跑 COM**。
  它们是否真能用，需要真机冒烟（本轮未做）。
* 308 → **303**（本轮接了 5 个）；**剩下的仍有 303 个**，其中大部分需要新解析器或会改几何。

## ✅ 真机冒烟（轮 91 补）—— 上表「未查证」项已解决
`tools/verify_batch5_smoke.py` 真连 SolidWorks（文档 `mcp_avi_shaft.SLDPRT`）：
```
✓ 连接 SolidWorks
✓ list_render_materials          ok · 0 个材质 · 0.02s
✓ collect_appearance_evidence    dict 3 键
✓ current_selection              1 项
✓ clear_selection                ok
✓ set_standard_view              ok · 0.53s
⇒ 7/7 · verdict: pass
```
**⚠ 证据强度不均**：`list_render_materials` 返回 **0 个材质**（**跑通了但没验到"有材质时"的行为**）；
`collect_appearance_evidence` 只回了 3 个键（**未核键的含义对不对**）。
⇒ 这两条**只能说"不报错"，不能说"结果正确"**。

### 冒烟本身踩的两处（都是迟到绑定的老问题）
1. `connect_solidworks()` 返回 **(sw, 元数据)** 元组 —— 直接当对象用 ⇒ `'tuple' object has no attribute 'ActiveDoc'`；
2. `GetTitle` 在 pywin32 下**有时是属性、有时是方法** ⇒ `doc.GetTitle()` 报 `'str' object is not callable`；
   改用仓库自带的 `sw_connect.get_com_member` 兼容两种形态。

### 安全（铁律 2）
`CommandInProgress` 抑制 → 每调用独立计时 → 收尾关掉**本轮自己开的**文档（本轮复用了已有文档，未新建）。

## ✅✅ 强证据（轮 92 补）—— 上节「证据强度不均」已解决
造一个**带外观的新件**再验，把两条弱证据变成硬证据：
```
✓ set_document_appearance 生效
✓ ★ list_render_materials **有材质时**返回 > 0        材质数 = 1（原文档是 0）
✓ ★ appearance_count 与实际材质数一致                 appearance_count=1 · 实际=1
✓ ★ appearances[0].diffuse **不是恒定 0**           diffuse=0.75   ← 证明真读到了材质参数
✓ ★ has_appearance 与材质数一致                      has_appearance=True
⇒ 12/12 · verdict: pass
```
**⚠ 本节自己的两处错（都是当场抽验发现的）**：
1. 我按 `rows` 取行 ⇒ 断言拿到 `None`；**实际键名是 `appearances`**（读实现后确认）；
2. `created.Close(False)` 在迟到绑定下报「**无效的参数数目**」⇒ 改用 `ISldWorks.CloseDoc(标题)`。

**★ 收尾（铁律 2）**：发现**我造的空件残留**（零件6/7/8）⇒ 只关「标题形如 `零件N` **且路径为空**」的，
**绝不碰有路径的文档**；清理后只剩用户原有的两个（`mcp_avi_shaft.SLDPRT` / `mcp_avi_asm.SLDASM`）。
冒烟脚本的收尾也已改成 `CloseDoc`，并在失败时**打印告警而不静默**。
