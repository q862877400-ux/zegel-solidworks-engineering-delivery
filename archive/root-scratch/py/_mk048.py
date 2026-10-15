import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\048-mcp-protocol-layer-verified")
S.mkdir(parents=True, exist_ok=True)

spec = """# 048 · 补上 `047` 留下的那条边界：**MCP 协议层**

**Status**: Implemented（轮 129）

## 一、要证什么
`047`（轮 128）只证到「**声明 → RESOLVERS → 调用**」，**协议层未证**。
本轮把 server **真的起起来**，用 JSON-RPC 问它「你有哪些工具」。

## 二、⚠⚠ 安全设计：**一次工具都不调**
已知事实 **24**：运行时只能有一个 SolidWorks MCP —— 多个进程抢同一 COM 连接会**死锁**。
⇒ 本探针**只发 `initialize` 与 `tools/list`**，**一次工具都不调** ⇒ **完全不碰 COM**。
★ 这正好也是本轮要证的那一层：**"工具被正确地登记与描述出来了"**。

## 三、★ 结果 **7/7**
```
✓ 起 server（stdio，一次工具都不调）          pid=…
✓ ★ `tools/list` 拿到响应                    **86 个工具**
✓ ★★ batch10 的 4 条都在协议层可见             4/4
✓ ★ schema 参数逐条对上（顺 $ref 走进去）      4/4
```
★ **顺带补上了 `047` 说「没有重新统计」的那个数**：协议层 **86 个工具**。

## 四、★★ 本轮抓到的东西：**不是缺陷，是我查错了地方**（两层）
```
第 1 层：我去**顶层** `properties` 找**展平**的参数名
        ⇒ 报「协议里只有一个 `params`」⇒ 看起来像个真缺陷
        ⇒ 查 schema 原文才发现那是**设计**：每个工具统一收一个 `params` 对象
          （与 server.py 原生工具一致），参数在 `params.$ref → $defs.<Model>.properties` 里
第 2 层：修完第 1 层后，又在 `inner["response_format"]` 找 `enum`
        ⇒ 它**也是个 `$ref`**（枚举在 `$defs.ResponseFormat`）
```
⇒ ★ 两次都是**判据爬错层**，不是系统有问题。
⚠ 而这也说明：**"测试红了"不等于"代码坏了"** —— 得先问「我量的是不是那个东西」。

## 五、★ 一个正面发现：框架会**统一补**一个参数
```
声明里没有 `response_format`，但协议层**每个工具都有**（枚举 json / markdown）
⇒ ★ 这是框架级的统一约定 ⇒ **声明时不要自己再加一个**
```

## 六、判据
| ID | 判据 |
|---|---|
| SC-4401 | ★★ **起 server 但一次工具都不调**（不碰 COM，符合事实 24）|
| SC-4402 | ★★ batch10 的 4 条**在协议层可见** |
| SC-4403 | ★ schema 参数**逐条**对上（顺 `$ref` 走进去）|
| SC-4404 | ★ 记下「框架统一补 `response_format`」这件事 |
| SC-4405 | ★★ **如实承认判据爬错两层**（不是缺陷）|
| SC-4406 | ★ 补上 `047` 没统计的**总暴露数**（86）|
| SC-4407 | 固化成测试（**4 条**，同样不碰 COM）|
| SC-4408 | 门禁 + 回归不退化（回归 **1153 passed**）|

## ⚠ 明确记下的限度
* **只证「工具被正确登记与描述」** —— **没有真调过一次工具** ⇒
  **不证调用路径**（那需要 COM，而这台机器上不允许第二个 COM 连接）；
* 86 个工具这个数**只在此刻成立**（加批次会变）；
* 协议版本用的是客户端声明的 `2025-06-18`；**其它版本未试**。
"""

plan = """# 049 · Plan

## 步骤
1. 确认**不能**起第二个连 COM 的进程（事实 24）⇒ 只发 `initialize` + `tools/list`
2. ★ 查 `mcp` 包在不在、server 的入口形态 ⇒ 都在
3. 写探针：起 stdio server、发两条 JSON-RPC、读回响应
4. 跑 ⇒ 86 个工具、batch10 **4/4 可见**
5. ★ schema 判据**红了** ⇒ **不急着改代码**，先 `_dump_tool_schema.py` 打原文
6. ⇒ 发现是**判据爬错层**（参数嵌在 `params` 里）⇒ 修判据
7. ⇒ 再红一次（`response_format` 也是个 `$ref`）⇒ 再修判据
8. 固化成测试（4 条）+ 已知事实 72 + 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 起第二个连 COM 的进程 ⇒ 死锁 | ★ **只发 list，不调工具** |
| schema 判据红了就改代码 | ★ **先打原文**看真实形状 ⇒ 才知是判据错还是代码错 |
| 忘记 `encoding`（事实 58）| ★ `subprocess` 一律给 `encoding="utf-8"` |
| 说"协议层通了"就完事 | ★ 限度里**明写**"没有真调过一次工具" |
"""

tasks = """# 049 · Tasks（全部完成，轮 129）

- [x] T-4401 确认安全边界（不调工具 ⇒ 不碰 COM）
- [x] T-4402 写 `tools/verify_mcp_protocol_layer.py`
  `→ 验收:` `python tools/verify_mcp_protocol_layer.py`（**7/7**）
- [x] T-4403 ★ 打 schema 原文（`_dump_tool_schema.py`）⇒ 发现是**判据爬错层**
- [x] T-4404 修两层判据（`params.$ref` → `$defs.<Model>`；`response_format` 也是 `$ref`）
- [x] T-4405 固化成测试 `tests/test_mcp_protocol_layer.py`（**4 passed**）
- [x] T-4406 已知事实 72 入库（含 86 这个数）
- [x] T-4407 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 049 · Converge

**Converged**: 2026-10-01（轮 129）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-4401 起 server 不调工具 | ✅ 不碰 COM |
| SC-4402 4 条协议层可见 | ✅ 4/4 |
| SC-4403 schema 逐条对上 | ✅ 顺 `$ref` |
| SC-4404 记下框架补的 `response_format` | ✅ |
| SC-4405 承认判据爬错两层 | ✅ 已写进测试与事实 72 |
| SC-4406 补上总暴露数 | ✅ **86** |
| SC-4407 固化成测试 | ✅ 4 passed |
| SC-4408 门禁 + 回归 | ✅ `release_check` exit 0 · **1153 passed** |

## 二、★★ 本轮的形状：**红了先别改代码，先打原文**
```
判据红 ⇒ 报「协议里只有一个 params」（看着像个真缺陷：调用方拿不到参数）
⇒ ★ 没有立刻去改 tool_specs 或 registry，而是先 _dump_tool_schema.py **打原文**
⇒ 原文显示：参数**在里面**（`$defs.<Model>.properties`），**这是设计**
⇒ 于是修的是**判据**，不是代码
```
⚠ **若我先去"修"代码**，就会把一个**本来对的设计**改坏 ——
而改完测试还会变绿（因为判据也错了）。★ **那才是最难发现的坏结局。**

## 三、★ 两次爬错层，说明一件事
```
第 1 层：顶层 properties 找展平参数名
第 2 层：inner["response_format"] 找 enum（它是个 $ref）
⇒ 这个 schema 是**多层 $ref 嵌套**的
```
★ 与事实 51（「一个抓不到目标类别的检查，往往是**分析范围**与代码的**组织单元**不匹配」）
**同族**：这次是**判据的"层"与数据的"层"不匹配**。

## 四、★ 顺带补上一个欠账
```
047 的限度里写着：「总暴露数（"工具 83 个"一类）本轮没有重新统计」
⇒ 本轮协议层一跑就拿到了：**86**
```

## 五、未查证
* **没有真调过一次工具** ⇒ **不证调用路径**；
* 86 只在此刻成立；
* 协议版本只用了客户端声明的 `2025-06-18`，**其它版本未试**。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
