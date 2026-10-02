# Tasks · Feature 143 仿真载荷族广度（24h 段 2.1）

> 每条都带 `→ 验收:`（宪法 §V）。★ 本特性的真机验收 **FAIL** ⇒ 按硬约束③标 `stitched`。

## 静态一半（★ 全绿）

- [x] T1 读 `sw_simulation_loads` 四个 `add_*` 的签名与返回形状
      → 验收: `inspect.signature` 显示首参是 `manager`，且 `_check(...)` 直回 COM 对象
- [x] T2 给 `sw_simulation_loads` 加四个**回读报告**包装（`apply_*_report`）
      → 验收: `python -c "import sw_simulation_loads as L; print(all(callable(getattr(L,n,None)) for n in ('apply_pressure_report','apply_torque_report','apply_gravity_report','apply_centrifugal_force_report')))"` 输出 `True`
- [x] T3 给 `RESOLVERS` 加 `"manager"` 键（★ 注入名只能是表的键）
      → 验收: `python -c "import register_capabilities as rc; print('manager' in rc.RESOLVERS)"` 输出 `True`
- [x] T4 写 `mcp-server/tool_specs_batch29.py`（4 个工具）
      → 验收: `python -c "import register_capabilities as rc; print(len(rc.all_specs()))"` 输出 `94`
- [x] T5 把 batch29 注册进 `BATCH_MODULES`
      → 验收: 同 T4，且 `python -m pytest tests/test_server_wiring.py -q` 0 failed
- [x] T6 参数绑定门禁（★ 为"漏绑/写错绑定"而建的那道）
      → 验收: `python scripts/check_param_binding.py; echo $LASTEXITCODE` 为 `0` 且输出 `[PASS] 0 处`
- [x] T7 更新两个"钉死数量"的守卫
      → 验收: `python -m pytest tests/test_server_wiring.py tests/test_mcp_protocol_layer.py -q` 0 failed

## ★ 真机一半（**FAIL** —— 如实记录）

- [x] T8 写真机证据脚本（★ 判据**沿用** `tools/capture_simulation_loads_evidence.py` 那条）
      → 验收: `python tools/capture_loadfamily_evidence.py` 能跑完并落 `output/loadfamily-evidence.json`
- [x] T9 **第 1 轮真机**（原样）
      → 验收: 输出显示四类报错形态（`类型不匹配@arg3` / `非选择性的参数`）—— ★ **已达成**（记录在案）
- [x] T10 **第 2 轮真机**（只改一个变量：`reg_geom` 用空 Dispatch）
      → 验收: ★ **`类型不匹配` 消失**（证明那条修复生效）—— ★ **已达成**
- [ ] **T11 第 3 轮真机（`verdict: pass`）** —— ⚠ **未完成，且按事实 53 主动停手**
      → 验收: `output/loadfamily-evidence.json` 的 `verdict == "pass"` ⇒ ⚠ **仍是 `fail`**
      → ★ 停手理由: 在「实参形状」上已改 2 次（arity 修正 + `reg_geom`）⇒ **事实 53**；
        正路是**先读类型库的重载表**，而不是继续试包装形态

## 收尾（★ 每批必做）

- [x] T12 能力条目：`simulation_load_family_breadth`，等级 **`stitched`** + `limitations` 写清未验证
      → 验收: `python -c "import json;from pathlib import Path;d=json.loads(Path('capabilities.yaml').read_text(encoding='utf-8'));print([c['level'] for c in d['capabilities'] if c['id']=='simulation_load_family_breadth'])"` 输出 `['stitched']`
- [x] T13 门禁链 18 道全 exit 0 + 全量 pytest 0 failed
      → 验收: `python scripts/release_check.py; echo $LASTEXITCODE` 为 `0`；`python -m pytest tests -q` 报 `0 failed`
- [x] T14 Spec Kit 五件套 + ROADMAP §一 游标 + known-facts 一条
      → 验收: `specs/143-simulation-load-family/` 下五件齐；`docs/ROADMAP.md` 含「24h 计划 段 2.1」；`docs/known-facts.md` 含新条目号
- [x] T15 两仓库各自 commit（**不 push**）
      → 验收: `git -C . status --porcelain` 与 `git -C D:\AI\SW status --porcelain` **均为空**
