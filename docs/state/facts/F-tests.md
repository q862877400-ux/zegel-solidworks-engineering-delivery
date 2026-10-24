# F 维度 · `tests/` 测试层现状

> 观测时间 **2026-10-24** · 观测方式：AST 统计 + `pytest --collect-only -q`（**只收集、不执行任何用例**）
> 复现总命令：
> ```powershell
> python docs\state\probes\probe_tests.py --json docs/state/inventory-f.json
> ```

---

### F-01 `tests/` 有 496 个 `.py`，其中 `test_*.py` **478** 个

- **读数**：`tests/*.py` **496** · `test_*.py` **478** · 其余（`conftest.py`、辅助模块等）**18**
- **未确认**：那 18 个非 `test_` 文件各自的用途——未逐个读

### F-02 `def test_` 共 **3,977** 个；收集期展开为 **4,111** 项

- **读数**：AST 统计 `test_` 前缀函数 **3,977** 个（无一个文件是 0 个测试）
- **读数**：`pytest --collect-only -q` 报告 **4,111** 项被收集
- **记录员注（陈述）**：两者差 **134**，与 `@pytest.mark.parametrize` 展开一致的可能（本次未逐文件核对 parametrize 数量）
- **未确认**：差值 134 的确切来源

### F-03 收集期 **exit=2**，**5 个文件收集失败**，异常类型全部是 `tool_registry.GateError`

- **读数**：`pytest tests --collect-only -q` ⇒ `exit=2` · `collected=4111` · `ERROR` **5** 条
- **错误类型分布**：`tool_registry.GateError` **5/5**
- **5 个文件（逐字）**：
  - `tests/test_mcp_backend_router.py`
  - `tests/test_mcp_configuration_tools.py`
  - `tests/test_mcp_drawing_tools.py`
  - `tests/test_mcp_headless_open_format.py`
  - `tests/test_spec212_unit_guard.py`
- **该异常的内容**：见 `docs/state/facts/B-tools.md` B-11（`check_specs` 返回 5 条问题，`register()` 整体拒绝）
- **未确认**：这 5 个文件里被阻断的用例**条数**——收集失败时 pytest 未给出该文件的用例数
- **未确认**：除这 5 个之外是否还有**执行期**失败——本次**未执行**任何用例

### F-04 无 `pytest.mark.asyncio`；`pytest.mark.skip` 出现 4 次

- **读数**：含 `pytest.mark.asyncio` 的文件 **0** · `pytest.mark.skip` 出现 **4** 次
- **交叉核对**：本轮早前观察到 `tests/test_ipc_protocol.py` 曾因**缺 `pytest-asyncio`** 报 38 error（见调查记录；
  该文件不在 F-03 的 5 个里 ⇒ 那条依赖缺失属另一条路径，需另行观测）
- **未确认**：`pytest-asyncio` 是否在本机环境内——未查 `pip list`

### F-05 收集期能收到 4,111 项 ⇒ 多数测试文件的**导入期**是通的

- **读数**：478 个 `test_*.py` 中，**5** 个在导入期被阻断；其余 **473** 个进入收集
- **记录员注（陈述）**：本读数只说明「能被收集」，**不说明**用例会通过
- **未确认**：用例通过率——需执行，本次范围外

---

## 与其它维度的交点（只列读数，不做关联推断）

| 交点 | 读数 | 来源 |
|---|---|---|
| 有测试钉死 `len(all_specs()) == 480` | 实测 501 | `docs/state/facts/B-tools.md` B-12 |
| 该断言所在文件是否被阻断 | 是（`test_server_wiring.py` 在收集期报 8 errors） | 本轮早前实测，见 B-13 |
| 测试文件的修改历史 | 未查 | — |

---

## 本节未覆盖（留给后续补充）

- 用例**执行**结果（通过/失败/跳过分类）——需真跑，且 `sw_connect` 相关用例可能要 SolidWorks
- 哪 5 个被阻断文件里各有多少用例
- `conftest.py` 提供了哪些 fixture、是否有自动 skip 逻辑
- 测试与 `capabilities.yaml` 里 100 条 `verified` 的对应关系
