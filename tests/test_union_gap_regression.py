"""★ **S0 缺口判定的回归测试**（2026-10-01 · 轮 312）。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_union_gap_regression.py
# 定位:   S0 缺口判定的回归 —— ★ 6 条已知答案（名字取自并集）必须全判「已有等价物」。
# 官方签名依据: 不适用（本测试只读 union-sources.json / capabilities.yaml / union-coverage-matrix.md）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

★★ 判据（★ 一条能跑出绿的命令）：★ `compute_union_gap_v3` 的**已知答案回归必须全过** ——
```
★ 6 条已知答案（★ 名字**取自 `tools/union-sources.json` 的并集**）
   `bbox` · `shell` · `export_step` · `pack_and_go_assembly` · `measure` · `measure_distance`
   ⇒ ★★ **全部应被判成「①已有等价物」**（★ 因为它们**我们都已经有了**）。
★ ⚠ 而 v1 会把其中一部分误判为"缺"（★ 假阳性率约 5/6）——
   ★ 本测试**就是那个改进的证明**（★ 事实 62：一个门禁"写了"不等于"有效"，负例是唯一的证明）。
```

★ 为什么它需要真机之外的东西：★ **不需要 SolidWorks** —— 它只读 `union-sources.json` ·
  `capabilities.yaml` · `union-coverage-matrix.md` ⇒ ★ **干净机器上必过**。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])
R = Path(r"" + _ROOT_S + r"")
SCRIPT = Path(Path(__file__).resolve().parents[1] / "compute_union_gap_v3.py")

#: ★ 已知答案：★ **6 条全部应判「已有」**（★ 名字取自并集，★ 不是记忆里的常见名）
KNOWN_ALREADY_HAVE = (
    "bbox", "shell", "export_step", "pack_and_go_assembly", "measure", "measure_distance",
)


def _load():
    """★ 动态载入那个独立脚本（★ 它不在包内 —— 它是工作区的分析工具）。"""
    if not SCRIPT.exists():
        pytest.skip("compute_union_gap_v3.py 不在（★ 它是工作区分析工具，★ 缺了就跳过）")
    spec = importlib.util.spec_from_file_location("union_gap_v3", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["union_gap_v3"] = mod
    spec.loader.exec_module(mod)
    return mod


def _rows(mod):
    import register_capabilities as rc                                     # noqa: PLC0415
    ours = [{"tool": s.name,
             "words": mod._expand(mod._words(s.name.replace("solidworks_", "")) | mod._words(s.function))}
            for s in rc.all_specs()]
    import json                                                            # noqa: PLC0415
    ops = json.loads((R / "tools" / "union-sources.json").read_text(encoding="utf-8"))["union_operations"]
    out = {}
    for op in ops:
        ow = mod._expand(mod._words(op))
        best = 0.0
        for o in ours:
            inter = ow & o["words"]
            if inter:
                best = max(best, len(inter) / max(1, len(ow)))
        out[op] = best
    return out


def test_regression_known_answers_all_covered():
    """★ **判据**：★ 6 条已知答案的 `best_cov` 都 ≥ 0.5（★ 即都判成「已有等价物」）。"""
    mod = _load()
    cov = _rows(mod)
    bad = [(n, cov.get(n)) for n in KNOWN_ALREADY_HAVE if cov.get(n, 0.0) < 0.5]
    assert not bad, "★ 这些已知「我们已有」的却被判成缺口：%s" % bad


def test_regression_samples_really_exist_in_the_union():
    """★ **负例自证**：★ 回归样本必须**真的在并集里** ——
    ★ 否则测试会因为"样本写错名字"而假绿（★ 本会话踩过：`export_to_step` 的真名是 `export_step`）。"""
    import json                                                            # noqa: PLC0415
    ops = set(json.loads((R / "tools" / "union-sources.json").read_text(encoding="utf-8"))["union_operations"])
    missing = [n for n in KNOWN_ALREADY_HAVE if n not in ops]
    assert not missing, "★ 回归样本不在并集里（★ 名字写错了）：%s" % missing


def test_strong_candidates_are_reported_with_a_domain():
    """★ 强候选必须**带域**（★ 那才是"域约束"的产出，★ 便于按域分批）。"""
    mod = _load()
    import json                                                            # noqa: PLC0415
    p = Path(Path(__file__).resolve().parents[1] / "output" / "union-gap-v3.json")
    if not p.exists():
        pytest.skip("先跑一次 compute_union_gap_v3.py 生成 output/union-gap-v3.json")
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["strong"], "★ 强候选不应为空（★ 若真为空也要显式记录）"
    nodom = [s for s in d["strong"] if not s.get("domain")]
    assert not nodom, "★ 这些强候选没带域：%s" % nodom[:5]
