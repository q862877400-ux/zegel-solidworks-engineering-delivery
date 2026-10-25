"""FR-014：规则/方法升级必须让**旧证据失效**（T029）。

## 义务原文

> 规则/方法升级必须能**识别受影响交付**并使**旧证据失效**。

## 为什么这条要机器保证

本仓的验收证据是「某一时刻 · 某一版产物 · 某一版判定器」跑出来的。
三者任一变了，旧证据就不再代表现在 —— 但没有指纹时**这三件事全都看不出来**，
报告会一直显示旧的 pass。

## 指纹三元（都可复算）

```
判定器版本（5 个 CHECKER_VERSION）
支持域版本（support-domain.yaml 的 declared_at）
交付件 sha256
```

★ **时间戳不进指纹**：时间变了不代表证据失效，用它会让指纹天天变，那就没人看了。
  这条也钉在测试里。
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO))

from check_evidence_freshness import compare, compute_fingerprint  # noqa: E402


def test_指纹含三项且不含时间() -> None:
    fp = compute_fingerprint()
    assert set(fp) == {"checkers", "domain_declared_at", "deliverable_sha256"}
    #: ★ 不得含任何时间字段 —— 时间变了不代表证据失效
    joined = " ".join(fp.keys()).lower()
    for bad in ("time", "at_", "date", "mtime", "finished"):
        assert bad not in joined, "★ 指纹里出现了时间类字段 %r" % bad
    assert len(fp["checkers"]) >= 5, "★ 判定器没数全"
    assert len(fp["deliverable_sha256"]) == 64, "★ 交付件指纹不是 sha256"


def test_同一指纹自比无差异() -> None:
    fp = compute_fingerprint()
    assert compare(fp, fp) == []


def test_判定器升级即失效() -> None:
    """★★ FR-014 的核心：判定器版本变了 ⇒ 旧结论按旧判据得出。"""
    cur = compute_fingerprint()
    rec = dict(cur)
    rec["checkers"] = dict(cur["checkers"])
    rec["checkers"]["e4_assembly"] = "s1-0"
    diffs = compare(rec, cur)
    assert len(diffs) == 1
    assert "e4_assembly" in diffs[0]
    assert "重跑" in diffs[0]


def test_支持域变更即失效() -> None:
    cur = compute_fingerprint()
    rec = dict(cur)
    rec["domain_declared_at"] = "1999-01-01"
    diffs = compare(rec, cur)
    assert any("支持域版本" in d for d in diffs)


def test_交付件变更即失效() -> None:
    cur = compute_fingerprint()
    rec = dict(cur)
    rec["deliverable_sha256"] = "0" * 64
    diffs = compare(rec, cur)
    assert any("交付件内容变了" in d for d in diffs)


def test_三处同时变会全部列出() -> None:
    """★ 一次改动不该只报第一条 —— 人要看到**全部**受影响的依据。"""
    cur = compute_fingerprint()
    rec = {
        "checkers": {k: "old" for k in cur["checkers"]},
        "domain_declared_at": "old",
        "deliverable_sha256": "old",
    }
    diffs = compare(rec, cur)
    assert len(diffs) >= 3
