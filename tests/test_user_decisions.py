"""用户决定索引：**不许漏登记，也不许替业主填答案**。

## 两条钉子

① **不漏**：每个 `owner: user` 的阻塞项 / 复现缺口，都必须在索引里有一条决定。
   漏掉的后果是：它悄悄从报告里消失，看起来像解决了。

② **不替业主填**：`ENGINEERING-PATH.md` 第 85 行逐字 ——
   「尺寸缺失就问；**材料、功能孔型、配合、制造约束、影响承载的工况不得偷偷填默认值**」。
   ⇒ 决定的 `value` 一旦被填，就直接判失败。

★ 这两条都不是「文档整洁」问题：第一条会让待办凭空消失，第二条会让错的模型看起来有依据。
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO))

import check_user_decisions as U  # noqa: E402


def test_索引当前一致() -> None:
    problems = U.check()
    assert problems == [], "★ 用户决定索引有问题：\n" + "\n".join(problems)


def test_S2八项都在() -> None:
    import yaml

    d = yaml.safe_load(
        (REPO / "docs" / "user-decisions.yaml").read_text(encoding="utf-8")
    )
    topics = {x.get("topic") for x in d.get("decisions") or ()}
    for need in (
        "material",
        "load_case",
        "safety_level",
        "process",
        "datums",
        "interface",
        "drawing_scope",
        "delivery_purpose",
    ):
        assert need in topics, "★ S2 的 %s 没进决定索引" % need


def test_每条决定都有回答格式() -> None:
    """★ 问「材料用什么」而不给格式，等于要人猜怎么答。"""
    import yaml

    d = yaml.safe_load(
        (REPO / "docs" / "user-decisions.yaml").read_text(encoding="utf-8")
    )
    for x in d.get("decisions") or ():
        assert str(x.get("format") or "").strip(), (
            "★ 决定 %s 没写回答格式" % x.get("id")
        )


def test_现在没有任何决定被填值() -> None:
    import yaml

    d = yaml.safe_load(
        (REPO / "docs" / "user-decisions.yaml").read_text(encoding="utf-8")
    )
    filled = [x.get("id") for x in d.get("decisions") or () if x.get("value")]
    assert filled == [], "★★ 这些决定被填了值（不许替业主决定）：%s" % filled


def test_填了值会被判失败(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """★★ 阴性对照：证明「填值」这条真有牙齿。

    ★ 只测「当前没填」是不够的 —— 那可能只是因为它压根不检查。
    """
    import yaml

    src = yaml.safe_load(
        (REPO / "docs" / "user-decisions.yaml").read_text(encoding="utf-8")
    )
    src["decisions"][0]["value"] = "Q235B"  #: 故意填一个值
    fake = tmp_path / "user-decisions.yaml"
    fake.write_text(
        yaml.safe_dump(src, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    monkeypatch.setattr(U, "DECISIONS", fake)
    problems = U.check()
    assert any("被填了值" in p for p in problems), (
        "★ 填了 value 却没被判失败 ⇒ 这条判据是摆设"
    )


def test_漏登记会红(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """★ 反向核对有牙齿：把一个 blocks 摘掉，必须报「会漏掉」。"""
    import yaml

    src = yaml.safe_load(
        (REPO / "docs" / "user-decisions.yaml").read_text(encoding="utf-8")
    )
    for x in src["decisions"]:
        if x.get("blocks"):
            x["blocks"] = []
    fake = tmp_path / "user-decisions.yaml"
    fake.write_text(
        yaml.safe_dump(src, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    monkeypatch.setattr(U, "DECISIONS", fake)
    problems = U.check()
    assert any("会漏掉" in p for p in problems), (
        "★ 拿掉 blocks 却没报漏 ⇒ 双向核对没生效"
    )


def test_CLI返回0() -> None:
    r = subprocess.run(
        [sys.executable, "-B", str(REPO / "scripts" / "check_user_decisions.py")],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO), timeout=120,
    )
    assert r.returncode == 0, r.stdout[-700:] + r.stderr[-400:]
    assert "决定" in r.stdout
