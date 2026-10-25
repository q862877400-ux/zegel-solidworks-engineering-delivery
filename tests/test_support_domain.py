"""支持参数域：声明必须可核、域外必须拒绝（规格 350 · FR-013 / FR-014 · T027 / T028）。

## 为什么这不是「文档工作」

spec 350 的原话：**「不限定范围的『全支持』是虚假承诺」**。
⇒ 「声明支持什么」这件事本身要能被机器查，否则它会退化成一段好话。

三条钉子：
- 每条 `evidence` 指向的**文件必须存在、字段必须真能在 JSON 里找到**
- 域外请求（含不支持的项）**必须被拒绝**，哪怕数值参数都合格
- 「不支持」必须写理由（只写不支持而不说为什么 = 空话）
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO))

from check_support_domain import (  # noqa: E402
    check_evidence,
    classify,
    load_domain,
    self_check,
)


# ── ① 声明本身必须自洽且可核 ─────────────────────────────────────────


def test_声明自洽() -> None:
    problems, checked = self_check()
    assert checked >= 5, "★ 只核到 %d 条 evidence，声明太小或漏核" % checked
    assert problems == [], "★ 支持域声明有问题：\n" + "\n".join(problems)


def test_每条声明都带证据() -> None:
    d = load_domain()
    for item in d.get("part_types") or ():
        assert item.get("evidence"), "★ 零件类型 %s 没写 evidence" % item.get("key")
    for key, spec in (d.get("limits") or {}).items():
        assert (spec or {}).get("evidence"), "★ 参数域 %s 没写 evidence" % key


def test_不支持项必须写理由() -> None:
    d = load_domain()
    assert d.get("unsupported"), "★ 没有任何「不支持」声明 —— 全支持是虚假承诺"
    for item in d["unsupported"]:
        assert str(item.get("reason") or "").strip(), (
            "★ 不支持项 %s 没写理由" % item.get("key")
        )
        assert item.get("match"), "★ 不支持项 %s 没有匹配词" % item.get("key")


# ── ② 证据核验有牙齿 ────────────────────────────────────────────────


def test_不存在的文件被拒() -> None:
    ok, why = check_evidence("output/根本没有这个文件.json#x")
    assert not ok and "不存在" in why


def test_不存在的字段被拒() -> None:
    ok, why = check_evidence("output/s3-acceptance.json#E3.根本没有这个字段")
    assert not ok, "★ 字段不存在却通过了证据核验"
    assert "找不到字段" in why


def test_真字段被接受() -> None:
    ok, why = check_evidence("output/s3-acceptance.json#E3.tally")
    assert ok, why


def test_空证据被拒() -> None:
    ok, _ = check_evidence("")
    assert not ok


# ── ③ 域外必须拒绝（T028 · spec 的验收场景）──────────────────────────


def test_域内请求通过() -> None:
    ok, reasons = classify(
        {"part_type": "plate_rect_holes", "plate_width_mm": 120, "hole_count": 4}
    )
    assert ok, "★ 域内请求被误拒：%s" % reasons


def test_超界数值被拒() -> None:
    ok, reasons = classify({"part_type": "plate_rect_holes", "plate_width_mm": 999})
    assert not ok
    assert any("高于上界" in r for r in reasons)


def test_未知零件类型被拒() -> None:
    ok, reasons = classify({"part_type": "五轴叶轮"})
    assert not ok
    assert any("不在支持列表" in r for r in reasons)


def test_要求图样必须被拒() -> None:
    """★★ 核心场景：数值都合格，但要图样 ⇒ 必须拒绝，不许「尽力生成」。"""
    ok, reasons = classify(
        {
            "part_type": "plate_rect_holes",
            "plate_width_mm": 120,
            "hole_count": 4,
            "asks": ["出一张工程图并标注"],
        }
    )
    assert not ok, "★ 要图样的请求没被拒 —— 这正是 spec 里禁止的「勉强生成」"
    assert any("drawing" in r for r in reasons)


def test_要求工艺必须被拒() -> None:
    ok, reasons = classify({"part_type": "plate_rect_holes", "asks": ["给工序卡"]})
    assert not ok
    assert any("process_plan" in r for r in reasons)


def test_要求自由度闭合必须被拒() -> None:
    ok, reasons = classify({"part_type": "plate_rect_holes", "asks": ["证明自由度闭合"]})
    assert not ok
    assert any("dof_closure" in r for r in reasons)


# ── ④ CLI 行为（门禁与拒绝器同一个判据源）────────────────────────────


def test_CLI自检返回0() -> None:
    r = subprocess.run(
        [sys.executable, "-B", str(REPO / "scripts" / "check_support_domain.py")],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO), timeout=120,
    )
    assert r.returncode == 0, r.stdout[-600:] + r.stderr[-600:]


def test_CLI域外请求返回非0(tmp_path: Path) -> None:
    req = tmp_path / "req.json"
    req.write_text(
        json.dumps({"part_type": "plate_rect_holes", "asks": ["出图"]}, ensure_ascii=False),
        encoding="utf-8",
    )
    r = subprocess.run(
        [
            sys.executable, "-B",
            str(REPO / "scripts" / "check_support_domain.py"),
            "--request", str(req),
        ],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO), timeout=120,
    )
    assert r.returncode == 1, "★ 域外请求的 CLI 没回非 0"
    assert "in_domain" in r.stdout
