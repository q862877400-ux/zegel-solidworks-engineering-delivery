"""MCP **协议层**契约测试：起 server、发 `tools/list`、核对 schema。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_mcp_protocol_layer.py
# 定位:   钉住 `047`（轮 128）留下的那条边界：**协议层**。
#         ⚠ **本测试会起一个 server 子进程，但一次工具都不调** ⇒ **不碰 COM**
#         （已知事实 24：多个进程抢同一 COM 连接会死锁）。
# 官方依据: MCP 协议由 `mcp` 包实现；本文件只断言我们自己的观测。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SERVER = REPO_ROOT / "mcp-server" / "server.py"

BATCH10 = (
    "solidworks_part_bounding_box",
    "solidworks_hole_standards",
    "solidworks_fastener_types",
    "solidworks_fastener_table_types",
)


def _list_tools(timeout: float = 40.0):
    """起 server、`initialize` + `tools/list`、终止。

    ⚠ **不调任何工具** —— 那才会连 COM。
    ⚠ 事实 58：一定要给 `encoding`，否则中文 Windows 上父进程用 GBK 解 UTF-8 会炸。
    """
    if not SERVER.is_file():
        pytest.skip("server.py 不在")
    proc = subprocess.Popen(
        [sys.executable, str(SERVER)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO_ROOT / "mcp-server"))
    try:
        def send(method, params, i):
            proc.stdin.write(json.dumps({"jsonrpc": "2.0", "id": i,
                                         "method": method, "params": params}) + "\n")
            proc.stdin.flush()

        send("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                            "clientInfo": {"name": "pytest", "version": "1"}}, 1)
        proc.stdin.write(json.dumps(
            {"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        proc.stdin.flush()
        send("tools/list", {}, 2)

        deadline = time.time() + timeout
        while time.time() < deadline:
            line = proc.stdout.readline()
            if not line:
                break
            try:
                msg = json.loads(line)
            except Exception:      # noqa: BLE001
                continue
            if msg.get("id") == 2 and "result" in msg:
                return msg["result"].get("tools") or []
        return None
    finally:
        try:
            proc.stdin.close()
        except Exception:      # noqa: BLE001
            pass
        try:
            proc.terminate()
            proc.wait(timeout=10)
        except Exception:      # noqa: BLE001
            try:
                proc.kill()
            except Exception:      # noqa: BLE001
                pass


@pytest.fixture(scope="module")
def tools():
    got = _list_tools()
    if got is None:
        pytest.skip("server 没在超时内回 `tools/list`（环境问题，不是契约问题）")
    return got


def test_batch10_tools_are_visible_over_the_protocol(tools):
    """@brief ★★ batch10 的 4 条**在协议层可见**（不只是"声明里有"）。"""
    names = {t["name"] for t in tools}
    missing = [n for n in BATCH10 if n not in names]
    assert not missing, "协议层缺: %s" % missing


def test_param_schema_is_nested_under_params(tools):
    """@brief ★★ **schema 形状**：参数嵌在 `properties.params.$ref → $defs.<Model>.properties`。

    ⚠⚠ **第一版爬错地方了（轮 129 当场发现）**：我去**顶层** `properties` 找**展平**的参数名，
    报「协议里只有一个 `params`」—— 但那**是设计**：每个工具统一收一个 `params`
    对象（与 `server.py` 原生工具一致）。
    ⇒ 本测试把**正确的位置**钉住，免得下一个人又爬错。
    """
    by = {t["name"]: t for t in tools}
    t = by["solidworks_hole_standards"]
    schema = t["inputSchema"]
    assert set(schema.get("properties") or {}) == {"params"}, "顶层应当只有 params"
    ref = schema["properties"]["params"].get("$ref")
    assert ref, "params 应当是一个 $ref"
    model = ref.rsplit("/", 1)[-1]
    inner = (schema["$defs"][model].get("properties") or {})
    assert "hole_type_id" in inner, "声明的参数应当在内层"


def test_every_tool_gets_a_framework_supplied_response_format(tools):
    """@brief ⚑ 框架**统一补**一个 `response_format`（`json`/`markdown`）—— 声明里没有它。"""
    by = {t["name"]: t for t in tools}
    t = by["solidworks_part_bounding_box"]
    schema = t["inputSchema"]
    model = schema["properties"]["params"]["$ref"].rsplit("/", 1)[-1]
    inner = schema["$defs"][model]["properties"]
    assert "response_format" in inner, "框架应当补 response_format"
    # ⚠ 它也是**一个 `$ref`**（指向 `$defs.ResponseFormat`），枚举在那边 ——
    #   不在 `inner["response_format"]` 里（**第一版又爬错了一层**）。
    rf_ref = inner["response_format"].get("$ref")
    assert rf_ref, "response_format 应当是一个 $ref"
    rf = schema["$defs"][rf_ref.rsplit("/", 1)[-1]]
    assert set(rf.get("enum") or []) == {"json", "markdown"}


def test_declared_params_all_appear_in_the_inner_schema(tools):
    """@brief ★ 声明里的**每个**参数都要在协议层内层出现（逐条）。"""
    sys.path.insert(0, str(REPO_ROOT / "mcp-server"))
    import importlib
    mod = importlib.import_module("tool_specs_batch10")
    by = {t["name"]: t for t in tools}
    for spec in mod.SPECS_BATCH10:
        t = by.get(spec.name)
        assert t is not None, spec.name
        schema = t["inputSchema"]
        model = schema["properties"]["params"]["$ref"].rsplit("/", 1)[-1]
        inner = set(schema["$defs"][model]["properties"])
        want = {p.name for p in spec.params}
        assert want <= inner, "%s 缺 %s" % (spec.name, want - inner)

# ── 轮 138：**两条注册路径**之间的一致性（此前无人检查）────────────────
#
# `server.py` 与 `batch` 模块是**两条**注册路径：
#   `server.py`     `@mcp.tool(name="solidworks_…")` 直接声明（当前 **45** 条）
#   batch 模块      `register_capabilities` 注册 `all_specs()`（当前 **41** 条）
# ⇒ 45 + 41 = **86**（与协议层实测一致）
#
# ⚠⚠ **本轮查出一件事**：`tool_registry.check_specs` 只查 **batch 路径内部**的重名；
#   **两条路径之间的重名没有任何检查** ⇒ 若有人把同一个名字加到两处，**没人会拦**
#   （而那时"哪一个赢"是不确定的）。本节的第 ② 条就是补这个。

SERVER_SRC = REPO_ROOT / "mcp-server" / "server.py"
NAME_LITERAL = re.compile(r'name\s*=\s*"((?:solidworks|cadstudio)_[a-z0-9_]+)"')


def _declared_in_server() -> list:
    return NAME_LITERAL.findall(SERVER_SRC.read_text(encoding="utf-8"))


def _declared_in_batches() -> list:
    sys.path.insert(0, str(REPO_ROOT / "mcp-server"))
    import importlib
    rc = importlib.import_module("register_capabilities")
    return [s.name for s in rc.all_specs()]


def test_two_paths_together_equal_the_protocol_tool_set(tools):
    """@brief ★★ `server.py` ∪ `batch` 必须**恰好等于**协议层给出的工具集合。"""
    live = {t["name"] for t in tools}
    both = set(_declared_in_server()) | set(_declared_in_batches())
    assert both == live, (
        "两边对不上：只在声明里 %s · 只在协议层 %s"
        % (sorted(both - live), sorted(live - both)))


def test_no_tool_is_declared_in_both_paths():
    """@brief ★★ **两条路径不许重名** —— 此前**没有任何检查**（轮 138 补上）。

    ⚠ 若重名，`tools/list` 只会出现一次（集合去重）⇒ 从协议层**看不出来**；
    而"哪一个赢"取决于注册顺序 ⇒ **不确定**。⇒ 必须在**声明层**拦。

    ⚠⚠ **本测试刻意不收 `tools` fixture**（轮 138 的故障注入抓出来的）：
    重名会让**注册失败 ⇒ server 起不来** ⇒ `tools` fixture 拿不到响应就 **`skip`**
    ⇒ ★ **判据会"恰好在被测故障发生时静默跳过"** —— 那是**最坏**的失效方式。
    ⇒ 所以本测试**只看两个声明来源**（源码 + `all_specs()`），**不碰协议层**。
    """
    overlap = sorted(set(_declared_in_server()) & set(_declared_in_batches()))
    assert not overlap, "这些工具名在 server.py 与 batch 里**都声明了**: %s" % overlap


def test_no_duplicate_declarations_within_each_path():
    """@brief ★ 每条路径**内部**也不许重名。"""
    from collections import Counter
    for label, names in (("server.py", _declared_in_server()),
                         ("batch 模块", _declared_in_batches())):
        dup = {k: v for k, v in Counter(names).items() if v > 1}
        assert not dup, "%s 内部重名: %s" % (label, dup)


def test_protocol_tool_count_matches_the_two_paths_sum():
    """@brief ★ 数量关系：`len(server) + len(batch) == len(协议层)`。

    ⚠ 硬编码的那个数是**钉死数量**的守卫：**加了工具就要同时改这里**。
    ★ 历史：曾为 **86**；轮 204（Spec Kit `123`）新增 `tool_specs_batch11.py` 的 4 个
      拓扑「目标 / 约束 / 控制」入口 ⇒ **90**；轮 222（Spec Kit `131`，砌墙 W1）新增
      `tool_specs_batch18.py` 的 4 个草图只读查询 ⇒ **103 → 107**；
      轮 224（砌墙 W2）新增 `tool_specs_batch19.py` 的 3 个工程图轻量读数 ⇒ **107 → 110**；
      轮 227（砌墙 W3）新增 `tool_specs_batch20.py` 的 2 个自定义属性读取 ⇒ **110 → 112**；
      轮 229（砌墙 W4）新增 `tool_specs_batch21.py` 的 5 个建草图/画几何 ⇒ **112 → 117**；
      轮 230（砌墙 W4 续）新增 `tool_specs_batch22.py` 的 3 个拉伸 ⇒ **117 → 120**；
      轮 231（砌墙 W4 续）新增 `tool_specs_batch23.py` 的 2 个倒角/圆角 ⇒ **120 → 122**；
      轮 234（砌墙 W5）新增 `tool_specs_batch24.py` 的 1 个质量属性读数 ⇒ **122 → 123**；
      轮 237（砌墙 W6）新增 `tool_specs_batch25.py` 的 3 个装配只读 ⇒ **123 → 126**；
      轮 238（砌墙 W7）新增 `tool_specs_batch26.py` 的 2 个仿真载荷 ⇒ **126 → 128**；
      轮 239（24h 段 1.1）新增 `tool_specs_batch27.py` 的 3 个仿真研究 ⇒ **128 → 131**；
      轮 240（24h 段 1.2）新增 `tool_specs_batch28.py` 的 4 个网格/求解/读数 ⇒ **131 → 135**；
      轮 246（24h 段 2.1）新增 `tool_specs_batch29.py` 的 4 个载荷族 ⇒ **135 → 139**。
    ★★ 2026-10-03（轮 470）：**234 → 281**。★ 按本测试的设计意图（"加了就要同时改这里"）。
    ★★ 2026-10-03（轮 474）：**286 → 291**（B6-a 的 5 条）。
    ★★ 2026-10-03（轮 476）：**291 → 292**（B6-b 的 1 条：放样曲面）。
    ★★ 2026-10-03（轮 479-480）：**292 → 297**（B8 的 5 条）。
    ★★ 2026-10-03（轮 481）：**297 → 298**（B7 的 1 条）。
      ⚠ **本轮之前还有多次工具增量我没逐个回溯**（★ 不编造来源）——
        可指认的两次是 `tool_specs_batch65.py` **9 条**（B1 草图图元，★ 9/9 真机建成）
        与 `tool_specs_batch66.py` **6 条**（B3 草图编辑，★ 6/7 真机建成）。
    ★★ 2026-10-03（轮 472）：**281 → 286**。★ 加的是 **B4** 的 5 条
      （`tool_specs_batch67.py`：移动 / 旋转 / 缩放 / 伸展 / 镜像草图实体，★ **真机 5/5**）。
      ★ 按本测试的设计意图（"加了就要同时改这里"）。
    ★★ 2026-10-04（24h 任务 · 阶段 3 · 轮 95–109）：**322 → 333**（★ 按本测试自己的设计意图
      ——「**加了就要同时改这里**」）✓
      ★ **这 11 条里有 8 条是本会话的**（★ 详见 `tests/test_server_wiring.py` 同轮的记录）：
        ★ **`tool_specs_batch77.py` 8 条** —— **阶段 3 的「读特征参数」族**，
          ★ 每条都走了「查官方签名 → 建能力 → **挂 ToolSpec** → 真机验证 → 提交」五步 ✓
      ★★ **另 3 条是**本会话之前**就有的**（★ **不逐个回溯、★ 不编造来源**）✓
    """
    n = len(_declared_in_server()) + len(_declared_in_batches())
    assert n == 339, (
        "两条路径合计 %d 条，而本测试上次实测 **339** 条 ⇒ 数字变了就说明有人加了东西"
        "（**本测试是「钉死数量」的守卫，加了就要同时改这里**）" % n)
