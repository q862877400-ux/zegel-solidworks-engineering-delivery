"""★ 负例：声明坏掉时 `check_specs` 必须**报问题**，不许把门禁自己打崩（2026-11-02 实测事故）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   mcp-server/tool_registry.py 的 `check_specs`
# 定位:   ★ 2026-11-02 逐文件诊断轮的**实测事故**回归：把 `params` 误写成裸 `dict` 列表时，
#         `check_spec` 抛 `AttributeError`（非 `GateError`），而 `check_specs` 只
#         `except GateError` ⇒ 异常穿透 ⇒ `server.py` **导入期崩溃**（499 个工具全拿不到）、
#         并且把 `check_param_binding.py` 与 `probe_all_specs.py` **本身**打崩。
#         ★ 修法：捕获 `Exception` 记成该 spec 的问题并继续。
# 官方依据: AGENTS.md 停止条件「misconfiguration fails loud」——**响亮地报错，而不是让门禁停摆**
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   tool_registry.check_specs 的异常分支（含负例）
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MCP = REPO / "mcp-server"


def _run(code: str) -> tuple[int, str]:
    """在 `mcp-server/` 目录下执行一段 python，返回 (退出码, stdout+stderr)。"""
    proc = subprocess.run(
        [sys.executable, "-B", "-c", code],
        cwd=str(MCP), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


BAD_SPEC = (
    "import sys; sys.path.insert(0, '.')\n"
    "from tool_registry import check_specs, ToolSpec\n"
    "bad = ToolSpec(name='solidworks_bad_tool', title='t', module='sw_x', function='f',\n"
    "               params=[{'name': 'a', 'type': 'string'}])\n"
    "probs = check_specs([bad])\n"
    "print(json.dumps(probs, ensure_ascii=False))\n"
)


def test_malformed_params_is_reported_not_raised():
    """★★ 负例（本事故的正身）：裸 dict 当 params ⇒ 返回问题列表，且**不抛异常**。"""
    code = "import json\n" + BAD_SPEC
    rc, out = _run(code)
    assert rc == 0, f"★ check_specs 抛了异常/崩了 ⇒ 事故复现：\n{out[-800:]}"
    line = [l for l in out.splitlines() if l.strip().startswith("[")]
    assert line, f"★ 没拿到问题列表：\n{out[-800:]}"
    problems = json.loads(line[-1])
    assert problems, "★ 坏声明竟然零问题 ⇒ 门禁放过它了"
    assert any("非 GateError" in p for p in problems), (
        f"★ 问题文案没标明异常类型（日后难诊断）：{problems}")


def test_valid_specs_stay_clean():
    """★ 正向对照：真实工具面必须**零问题**（修完不许把正常声明误判成问题）。"""
    code = (
        "import sys, json; sys.path.insert(0, '.')\n"
        "import register_capabilities as rc\n"
        "from tool_registry import check_specs\n"
        "print(json.dumps(check_specs(rc.all_specs()), ensure_ascii=False))\n"
    )
    rc_, out = _run(code)
    assert rc_ == 0, f"★ 校验真实工具面时崩了：\n{out[-800:]}"
    line = [l for l in out.splitlines() if l.strip().startswith("[")]
    assert line, out[-800:]
    problems = json.loads(line[-1])
    assert problems == [], f"★ 真实工具面有问题（应先修声明，不是改这个测试）：{problems[:3]}"


def test_server_import_still_works():
    """★★ 事故的**外部症状**回归：`import server` 必须成功（工具面 499 条全可发现）。"""
    rc_, out = _run("import server; print('OK', len(server.__dict__) > 0)")
    assert rc_ == 0, f"★ server 导入失败 ⇒ 服务起不来：\n{out[-1200:]}"
    assert "OK" in out
