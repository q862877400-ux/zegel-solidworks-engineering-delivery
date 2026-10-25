"""★ E7 版本绑定：没声明版本 ⇒ `unknown`，不许静默 `pass`。

## 缺陷（第 36 轮探针确认）

`judge_provenance` 的 ⑤ 逐字是：

```python
if v["evidence_version"] and v["artifact_version"]:
    if v["evidence_version"] != v["artifact_version"]:
        ... fail
```

⇒ **任一为空就整条跳过**，实测三种情形**全部 pass**：

```
产物版本空、证据 rev1  ⇒ pass
证据版本空、产物 rev1  ⇒ pass
两版都空             ⇒ pass
```

⇒ 「**旧版本证据**」（E7 的负例之一）可以靠「不声明产物版本」绕过。

## 修法与它的理由

把义务提到**采集层**的 `complete`：两个版本都必须声明，缺一即「没取到必要输入」。

| 输入 | complete | 判定 |
|---|---|---|
| 两版都有、一致 | True | pass |
| 两版都有、不一致 | True | **fail**（旧版本证据） |
| 任一为空 | **False** | **unknown** |

★ 为什么 `unknown` 而不是 `fail`：我们**没有**证据说它是旧版本 —— 只是无法判。
  判 fail 是编事实。
★ 为什么不算放宽：修之前是**静默 pass**（最糟），现在是明确的 `unknown`。

## 两侧都要钉

只测「为空变 unknown」不够 —— 还要证明**两版一致仍然 pass**（否则加严把判据变钝）、
**两版不一致仍然 fail**（否则这条负例丢了）。
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import pytest  # noqa: E402

from engineering.acceptance.e7_provenance import (  # noqa: E402
    collect_provenance,
    judge_provenance,
)
from engineering.acceptance.result import Status  # noqa: E402

REQ = "R-E"

_CLAIMS = ({"id": "C1", "text": "板厚满足刚度"},)
_CITES = ({"claim_id": "C1", "locator": "GB/T 1804-2000 表1", "resolved": True},)


def _judge(artifact: str, evidence: str, **kw):
    obs = collect_provenance(
        target="板1结论",
        claims=kw.get("claims", _CLAIMS),
        citations=kw.get("citations", _CITES),
        outputs=kw.get("outputs", {"deflection_mm": 0.03}),
        source_kind=kw.get("source_kind", "standard_clause"),
        source_ref=kw.get("source_ref", "GB/T 1804-2000"),
        artifact_version=artifact,
        evidence_version=evidence,
    )
    return obs, judge_provenance(obs, requirement_id=REQ)


# ── 修的那三条（原来全是 pass） ──────────────────────────────────────


@pytest.mark.parametrize(
    ("artifact", "evidence"),
    [("", "rev1"), ("rev1", ""), ("", "")],
)
def test_没声明版本必须unknown(artifact: str, evidence: str) -> None:
    """★★ 修之前这三种情形全部 **pass** —— 「旧版本证据」可绕过。"""
    obs, res = _judge(artifact, evidence)
    assert obs.complete is False, (
        "★ artifact=%r evidence=%r 应标采集不完整" % (artifact, evidence)
    )
    assert res.status is Status.UNKNOWN, (
        "★ 没声明版本应判 unknown，修之前是 pass（实得 %s）" % res.status.value
    )


def test_没声明版本的note说清缺哪件事() -> None:
    obs, _ = _judge("", "rev1")
    assert "版本" in obs.note, "★ note 应指出是版本问题：%r" % obs.note
    assert "旧版本证据" in obs.note, "★ note 应说清无法判哪条负例：%r" % obs.note


# ── 反向：加严不能把判据变钝 ─────────────────────────────────────────


def test_两版一致仍然pass() -> None:
    """★★ 防「一律 unknown」式的假加严。"""
    obs, res = _judge("rev1", "rev1")
    assert obs.complete is True
    assert res.status is Status.PASS, "★ 两版一致应 pass，实得 %s" % res.status.value


def test_两版不一致仍然fail() -> None:
    """★★ 这一条是 E7 的负例之一（旧版本证据），加严不能把它弄丢。"""
    obs, res = _judge("rev2", "rev1")
    assert obs.complete is True
    assert res.status is Status.FAIL, "★ 两版不一致应 fail，实得 %s" % res.status.value
    assert "旧版本" in res.reason


# ── 既有判据不被新判据挤掉 ───────────────────────────────────────────


@pytest.mark.parametrize(
    ("kw", "want"),
    [
        ({"source_kind": "瞎填的来源"}, "来源标签"),
        ({"source_ref": ""}, "来源引用"),
        ({"citations": ()}, "引用"),
        ({"outputs": {}}, "复算依据"),
        ({"claims": _CLAIMS, "citations": (
            {"claim_id": "C1", "locator": "见上", "resolved": True},)}, "locator"),
    ],
)
def test_既有判据仍然生效(kw, want) -> None:
    """★ 顺序问题会让后面的判据永不生效 —— 逐条确认它们仍然拦得住。"""
    obs, res = _judge("rev1", "rev1", **kw)
    assert res.status is Status.FAIL, "★ %r 应被判 fail，实得 %s" % (
        kw,
        res.status.value,
    )
    assert want in res.reason, "★ 理由应含 %r：%s" % (want, res.reason[:120])
