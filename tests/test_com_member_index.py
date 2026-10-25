"""COM 反查索引：**先查我们封过没，再决定要不要手写**。

## 为什么（业主 2026-10-26 质问）

> 你怎么又开始查官方 API 了？…我们自己不是有草图阵列的这个 MCP 工具吗？…

我手写了 `AddDimension2` / `EditDelete`，而本仓早就有：
```
IModelDoc2.AddDimension2          → sw_part.add_dimension_report
IModelDoc2.AddVerticalDimension2  → sw_sketch_dimensions.add_vertical_dimension
IModelDoc2.EditDelete             → sw_part.feature_delete
```
⇒ 有了反查表，这类「忘了自己有工具」才不会再发生。

## 钉什么

① 索引**新鲜**（重新扫描 == 落盘内容），否则表会过期骗人
② 关键成员**能反查到**（拿本轮实证的 3 个当样本）
③ 查不到时**如实说没有**（不能静默回空）
④ 生成物里**不许出现**「N 处」这类无出处量化断言（事实出处门禁会红）
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO))

import gen_com_member_index as _gen  # noqa: E402

INDEX_JSON = REPO / "docs" / "com-member-index.json"
INDEX_MD = REPO / "docs" / "com-member-index.md"


def test_index_file_exists() -> None:
    assert INDEX_JSON.is_file(), "★ 缺 docs/com-member-index.json"
    assert INDEX_MD.is_file(), "★ 缺 docs/com-member-index.md"


def test_index_is_fresh() -> None:
    """★ 落盘内容必须等于**现在重新扫描**的结果，否则读表的人会被过期数据骗。"""
    on_disk = json.loads(INDEX_JSON.read_text(encoding="utf-8"))
    fresh = _gen.scan()
    only_disk = set(on_disk) - set(fresh)
    only_fresh = set(fresh) - set(on_disk)
    assert not only_fresh, "★ 索引漏了新封装的成员：%s" % sorted(only_fresh)[:8]
    assert not only_disk, "★ 索引里有已不存在的成员：%s" % sorted(only_disk)[:8]


def test_known_members_resolvable() -> None:
    """★★ 本轮实证的 3 个：我手写过、而本仓早有封装。"""
    idx = json.loads(INDEX_JSON.read_text(encoding="utf-8"))
    expect = {
        "AddDimension2": "sw_part.py",
        "AddVerticalDimension2": "sw_sketch_dimensions.py",
        "EditDelete": "sw_part.py",
    }
    for member, module in expect.items():
        hits = idx.get(member) or []
        assert hits, "★ %s 没有封装记录（本仓明明有）" % member
        assert any(module in h["module"] for h in hits), (
            "★ %s 的记录里没有 %s：%s" % (member, module, hits)
        )


def test_real_gaps_are_empty() -> None:
    """★ 没有封装就要如实为空 —— 这样我才会自己去写并记缺口。"""
    idx = json.loads(INDEX_JSON.read_text(encoding="utf-8"))
    for member in ("CreateLinearSketchStepAndRepeat", "CreatePoint"):
        assert member not in idx or not idx[member], (
            "★ %s 现在有封装了 ⇒ 请更新本测试的「真缺口」清单" % member
        )


def test_cli_hit_returns_zero() -> None:
    r = subprocess.run(
        [
            sys.executable, "-B",
            str(REPO / "tools" / "find_com_wrapper.py"),
            "EditDelete",
        ],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO), timeout=120,
    )
    assert r.returncode == 0, r.stdout[-400:] + r.stderr[-300:]
    assert "feature_delete" in r.stdout


def test_cli_miss_returns_one() -> None:
    r = subprocess.run(
        [
            sys.executable, "-B",
            str(REPO / "tools" / "find_com_wrapper.py"),
            "NoSuchMemberXyz",
        ],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO), timeout=120,
    )
    assert r.returncode == 1, "★ 查不到应回 1（不能静默成功）"
    assert "没有" in r.stdout


def test_generated_md_has_no_bare_counts() -> None:
    """★ 表格里不许写「等 N 处」—— 事实出处门禁会要求给出处。"""
    md = INDEX_MD.read_text(encoding="utf-8")
    assert " 等 " not in md or "处" not in md
    for ln in md.splitlines():
        if ln.startswith("| `"):
            assert " 处" not in ln, "★ 表格行里有裸计数：%s" % ln[:80]


def test_index_scale_is_useful() -> None:
    idx = json.loads(INDEX_JSON.read_text(encoding="utf-8"))
    assert len(idx) >= 100, "★ 只索引到 %d 个成员，太小了，多半扫描面不对" % len(idx)
