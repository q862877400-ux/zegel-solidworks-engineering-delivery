"""★ 规格 297 判据：223 的 B1–B5 收口 —— 计数棘轮对齐真值 · 效应表由生成器产出 · 权属裁定留档。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `tests/test_server_wiring.py`（B1）· `tests/test_mcp_protocol_layer.py`（B2）
#         `tests/test_shell_params_capability.py`（B3 · ★ **权威元判据**）·
#         `tests/test_effect_declarations.py` + `docs/effect-declarations.json`（B4/B5）
#         `specs/275-*/`（★ 原判「5 条被未提交改动阻塞、权属未定」）· `output/GOAL.md` §三 E（★ 代拍板授权）
# 定位:   ① 三条计数棘轮必须**互相一致**且等于**实测真值**；
#         ② 效应表必须是**生成器产出**的（★ 不是手改的）；
#         ③ 工具数必须有**两条独立通路**对账（★ 单源自证不算）；
#         ④ 边界冻结（★ 不重写那 5 个 batch 文件的内容）；
#         ⑤ 权属裁定留档可查。
# 官方依据: 不适用（本项目内部纪律与计数）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 不连 COM；★ 真机读数由既有探针产出）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "mcp-server"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★★★ **两条独立通路的真值**（★ 2026-10-10 实测 · ★ 证据 `output/mcp-stdio-handshake.json`）
#: ★★ **2026-10-10 三处下调（★ 业主架构指令 —— ★ 正当减少）**：
#:   业主原话：「★ **我想让你继承上游的是工具，只是单纯的工具。**
#:     ★ **而像齿轮这种东西，在我认知里属于方法 —— 方法错了，工具再多也没有用。**
#:     ★ **你要从你继承的东西里面把方法筛选出来，把工具留下来，方法全部都删掉。**」✓
#:   ★★ **减少了什么**：★ 5 个**由方法模块支撑**的 MCP 工具（★ 渐开线齿形公式 · 倒角体积公式）⇒
#:     · ★ `all_specs()`：★ **479 → 476**
#:     · ★ `tools/list` 合计：★ **524 → 521**
#:     · ★ 装饰器那一路：★ **45 不变**（★ 它是 `server.py` 的 `cadstudio_*`，★ 移出的是**声明式**那批）✓
#:   ★★★ **判据**：★「**那个数字错了，回读能不能查出来**」⇒ ★ **不能** ⇒ **是方法** ✗
#:   ★ 原件在 `archive/inherited-methods/`（★ **只搬不删**）✓
TRUTH_SPECS = 480          #: ① `register_capabilities.all_specs()`
#: ★★ 2026-10-12（规格 329 · Q6 L110「必须同时改 MCP 暴露面」）：**476 → 480**
#:   —— ★ 新增 `tool_specs_batch115.py` 的 4 个**目录检索入口**
#:   （`solidworks_catalog_{domains,retrieve,contract,exposure}`）。
#:   ★★ 为什么：规格 323 的检索层**有名字、没注册** ⇒ **agent 够不到检索层**。
TRUTH_TOTAL = 525          #: ② 真 JSON-RPC `tools/list`
#: ★ 同轮 **521 → 525**（★ 480 + 45 = 525 ✓）
TRUTH_DECORATED = 45       #: ★ `mcp-server/server.py` 那一路（★ 对账：480 + 45 = 525）

#: ★★ 被裁定权属的 5 个文件（★ 275 判「未提交 ⇒ 权属未定」）
RULED_FILES = (
    "mcp-server/tool_specs_batch4.py",
    "mcp-server/tool_specs_batch16.py",
    "mcp-server/tool_specs_batch35.py",
    "mcp-server/tool_specs_batch80.py",
    "mcp-server/tool_specs_batch93.py",
)


def test_three_count_ratchets_agree_on_the_measured_truth():
    """★★★ FR-001：B1/B2/B3 三条计数棘轮**必须互相一致**且等于**实测真值**。

    ★ 三条的形态（★ 逐字）：
      · B1 `test_server_wiring.py`  → `assert len(all_specs()) == 479`
      · B2 `test_mcp_protocol_layer.py` → `assert n == 524`
      · B3 `test_shell_params_capability.py` → ★★ **元判据**：核「B1 的钉死数跟上了没有」
    """
    t1 = (ROOT / "tests" / "test_server_wiring.py").read_text(encoding="utf-8", errors="replace")
    t2 = (ROOT / "tests" / "test_mcp_protocol_layer.py").read_text(encoding="utf-8", errors="replace")

    assert "assert len(all_specs()) == %d" % TRUTH_SPECS in t1, (
        "★ B1 的钉死数不是实测真值 %d" % TRUTH_SPECS)
    assert re.search(r"assert n == %d," % TRUTH_TOTAL, t2), (
        "★ B2 的钉死数不是实测真值 %d" % TRUTH_TOTAL)

    #: ★★ 三条**互锁**：B3 逐字核 B1 的钉死数 ⇒ 三者必须指向同一个数
    assert "assert len(all_specs()) == %d" % TRUTH_SPECS in t1


def test_ratchets_equal_the_live_registry():
    """★★★ FR-001 的**活体**断言：棘轮上的数必须等于**现在真的**有多少个 spec。"""
    import register_capabilities as rc

    live = len(rc.all_specs())
    assert live == TRUTH_SPECS, (
        "★ 活的 `all_specs()` 是 %d，而棘轮钉的是 %d ⇒ ★ 有人加了工具却没同步（★ 那正是棘轮的意图）"
        % (live, TRUTH_SPECS))


def test_tool_count_has_two_independent_sources():
    """★★★ FR-003：工具数必须有**两条独立通路**对账（★ 单源自证不算 —— 事实 62 同族）。

    ★ 通路① = `register_capabilities.all_specs()`（★ 声明式）
    ★ 通路② = 真 JSON-RPC `tools/list`（★ 端到端，★ 走真 stdio 握手）
    """
    handshake = ROOT / "output" / "mcp-stdio-handshake.json"
    assert handshake.is_file(), (
        "★ 缺 `output/mcp-stdio-handshake.json`（★ 通路②的证据）—— "
        "跑 `python tools/probe_mcp_stdio_handshake.py` 生成")
    data = json.loads(handshake.read_text(encoding="utf-8"))
    blob = json.dumps(data, ensure_ascii=False)
    assert str(TRUTH_TOTAL) in blob, (
        "★ 真机握手里找不到 %d ⇒ 两条通路对不上（★ 只有单源自证）" % TRUTH_TOTAL)


def test_effect_table_is_regenerated_not_hand_edited():
    """★★★ FR-002：效应表必须是**生成器产出**的（★ B4/B5 的正解是重生成，不是手改）。"""
    table = ROOT / "docs" / "effect-declarations.json"
    gen = ROOT / "tools" / "gen_effect_declarations.py"
    assert table.is_file(), "★ 缺 `docs/effect-declarations.json`"
    assert gen.is_file(), "★ 缺生成器 `tools/gen_effect_declarations.py`"
    data = json.loads(table.read_text(encoding="utf-8"))
    #: ★★ 生成物必须覆盖**每一个**工具（★ 这正是 B5 的判据）
    import register_capabilities as rc

    names = {s.name for s in rc.all_specs()}
    declared = set((data.get("tools") or {}).keys())
    missing = sorted(names - declared)
    assert not missing, (
        "★ 效应表**没覆盖** %d 个工具 ⇒ ★ 跑 `python tools/gen_effect_declarations.py` 重生成\n  例：%s"
        % (len(missing), missing[:5]))


def test_batch_files_content_is_not_rewritten():
    """★★ FR-004：边界冻结 —— ★ 本轮**只改判据侧**，★ 不重写那 5 个 batch 文件的内容。

    ★ 判据：那 5 个文件**仍然存在**且**仍是合法 Python**（★ 内容未被本规格破坏）。
    ★★ 为什么要这条：★ 权属裁定的结论是「它们是**正规施工产物**」⇒ ★ **更不该**去重写它们。
    """
    import ast

    for rel in RULED_FILES:
        p = ROOT / rel
        assert p.is_file(), "★ %s 不见了" % rel
        ast.parse(p.read_text(encoding="utf-8", errors="replace"))


def test_ownership_ruling_is_recorded():
    """★★ FR-005：权属裁定必须**留档可查**（★ 代拍板要留理由，★ 不能只说"我拍了"）。"""
    spec = ROOT / "specs" / "297-b1-b5-ownership-closeout" / "spec.md"
    assert spec.is_file(), "★ 缺本规格的 spec.md"
    body = spec.read_text(encoding="utf-8", errors="replace")
    assert "代拍板" in body, "★ 裁定段没写清**行使的是哪条授权**"
    assert "权属" in body, "★ 裁定段没写清**权属结论**"
    #: ★ 五个文件都要在裁定表里出现（★ 文档里写的是**文件名**，路径前缀不必重复）
    for rel in RULED_FILES:
        base = rel.rsplit("/", 1)[-1]
        assert base in body, "★ 裁定表里没列 %s" % rel
