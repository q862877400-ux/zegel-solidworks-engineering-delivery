"""★ 批次 86 的契约测试：**第四坡（解锁 C 类）产出的 30 个** —— 本批证明"加解析器换工具"走得通。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch86.py`（生成物）· `output/bunny4-filtered-report.json`（真新行）·
#         `mcp-server/register_capabilities.py` 的 `RESOLVERS`（本批靠它才挂得上）
# 定位:   规格 `specs/205-tool-ramp/` 的 SC-002/SC-004；★ 本批三条特有契约：
#         ① ★ **30 个都要能解析到真实函数**（生成物必须逐条可调）
#         ② ★★ **注入键必须既在 `RESOLVERS` 里、又逐字等于目标函数首参名**（事实 502）——
#            本批全靠 `view`/`results`/`mesh`/`options` 四个新键 ⇒ 这条是本批的**命门**
#         ③ ★ **没有裸坐标**（规则 3）；★ 视图族里有"缩放/平移"这类**容易被写成收坐标**的工具 ⇒ 专门守
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as rc                            # noqa: E402
import tool_specs_batch86 as b86                              # noqa: E402

NEW_KEYS = ("view", "results", "mesh", "options")


def test_batch86_registered():
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch86"' in t


def test_thirty_specs_declared():
    assert len(b86.SPECS_BATCH86) == 30, len(b86.SPECS_BATCH86)


def test_every_spec_resolves_to_a_real_function():
    """★ 生成物的核心风险：`module`/`function` 拼错看着像工具、跑起来才炸 ⇒ 逐条解析 ✓"""
    for s in b86.SPECS_BATCH86:
        m = importlib.import_module("scripts.%s" % s.module)
        assert callable(getattr(m, s.function, None)), "%s → %s.%s" % (s.name, s.module, s.function)


def test_inject_key_is_registered_and_equals_first_param():
    """★★ 本批的**命门**：四个新键必须既在 `RESOLVERS` 里、又与目标函数首参同名（事实 502）。"""
    for s in b86.SPECS_BATCH86:
        inj = getattr(s, "inject", "")
        assert inj in rc.RESOLVERS, (s.name, inj, sorted(rc.RESOLVERS))
        assert inj in NEW_KEYS, (s.name, inj)
        m = importlib.import_module("scripts.%s" % s.module)
        first = next(iter(inspect.signature(getattr(m, s.function)).parameters), "")
        assert first == inj, (s.name, first, inj)


def test_no_bare_coordinates():
    """★ 视图族有"缩放/平移/旋转"这类**容易被写成收坐标**的工具 ⇒ 规则 3 专门守一条 ✓"""
    for s in b86.SPECS_BATCH86:
        for p in (getattr(s, "params", None) or []):
            assert p.name.lower() not in ("x", "y", "z", "point", "coord", "center", "origin"), \
                (s.name, p.name)


def test_all_specs_count_matches_registry():
    """★ 注册表与批次文件必须一致（★ 防"文件写了但没进 BATCH_MODULES"）。"""
    names = {getattr(x, "name", "") for x in rc.all_specs()}
    for s in b86.SPECS_BATCH86:
        assert s.name in names, "★ 没进注册表: %s" % s.name
