"""复现清单：可核项必须可核，缺口必须写清（规格 350 · T030）。

## 这条门禁的边界（写在这里，也写在脚本里）

**判**：Python/包版本、声明 `in_repo` 的输入真在仓库且 sha256 一致、
`steps` 指向的脚本存在、`known_gaps` 三要素齐。

**不判**：SolidWorks 装没装（只能 COM 读）；换台机器产物是否逐字节一致。

## 为什么「有缺口」不算失败

T030 的现状是：输入 STEP **不在仓库里**、SolidWorks **无法从仓库复现**、
模板与材料库随安装包。这三件都**不是代码能修的**，而且都属**用户决定**。

⇒ 把它们写成 `known_gaps`（带 impact/owner/remedy）是**诚实**；
  假装没有、或者说「已复现」，才是错。
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO))

from check_repro_manifest import check  # noqa: E402


def test_可核项全过() -> None:
    problems, _warnings, _gaps = check()
    assert problems == [], "★ 复现清单有可修问题：\n" + "\n".join(problems)


def test_缺口都写了处置三要素() -> None:
    _p, _w, gaps = check()
    assert gaps, "★ 一条缺口都没有 —— T030 现状明明有缺口，全绿是可疑的"
    for g in gaps:
        for k in ("what", "impact", "owner", "remedy"):
            assert str(g.get(k) or "").strip(), (
                "★ 缺口 %s 缺 %s" % (g.get("key"), k)
            )


def test_缺口归属明确() -> None:
    """★ 每条缺口都要有 owner —— 没有归属的缺口永远不会被解决。"""
    _p, _w, gaps = check()
    for g in gaps:
        assert g.get("owner") in ("user", "agent", "toolchain"), (
            "★ 缺口 %s 的 owner=%r 不在已知归属里" % (g.get("key"), g.get("owner"))
        )


def test_输入资产如实标注未入库() -> None:
    """★★ T030 的核心事实：输入 STEP 不在仓库里，必须**如实标** in_repo: false。"""
    import yaml

    d = yaml.safe_load(
        (REPO / "docs" / "repro-manifest.yaml").read_text(encoding="utf-8")
    )
    inputs = d.get("inputs") or ()
    assert inputs, "★ 没有任何输入声明"
    not_in_repo = [i for i in inputs if not i.get("in_repo")]
    assert not_in_repo, "★ 输入全声明 in_repo —— 但 output/stage2 未被 git 跟踪"
    keys = {g.get("key") for g in (d.get("known_gaps") or ())}
    assert "input_step_not_committed" in keys, (
        "★ 未入库的输入没有对应的 known_gap ⇒ 缺口被藏起来了"
    )


def test_步骤指向的脚本都存在() -> None:
    import yaml

    d = yaml.safe_load(
        (REPO / "docs" / "repro-manifest.yaml").read_text(encoding="utf-8")
    )
    for step in d.get("steps") or ():
        for key in ("cmd", "then"):
            cmd = str(step.get(key) or "")
            if not cmd:
                continue
            py = [x for x in cmd.split() if x.endswith(".py")]
            assert py, "★ 步骤 %s 没有 .py 脚本" % step.get("id")
            for rel in py:
                assert (REPO / rel).is_file(), "★ 步骤脚本不存在：%s" % rel


def test_CLI返回0() -> None:
    r = subprocess.run(
        [sys.executable, "-B", str(REPO / "scripts" / "check_repro_manifest.py")],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO), timeout=120,
    )
    assert r.returncode == 0, r.stdout[-800:] + r.stderr[-400:]
    assert "已知缺口" in r.stdout or "known_gaps" in r.stdout or "缺口" in r.stdout
