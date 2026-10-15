"""追加第五层（汇总完整性）的契约测试。"""
from __future__ import annotations

import sys
from pathlib import Path

TARGET = Path(r"C:\swprojects\sw-skill-fork\tests\test_gate_negative_cases.py")

BLOCK = '''

# ══ ⑩ 门禁「第五层」：结果必须进返回体（轮 74 加）══════════════════════

def test_gate_aggregation_covers_every_runner():
    """★★ **核心负例**：每个 `_run_*` 的结果都必须在 `_gate_results` 里。

    ⚠ 实测（轮 74）：`release_check` 的返回体此前只汇总了 **4 个**门禁
      （`provenance` / `diff_markers` / `member_names` / `interface_ownership`），
      其余 **9 个的状态根本没被汇总** —— 更关键的是**没有任何地方统计 `skipped`**
      ⇒ **「跳过了」在结果里是隐形的**。
    ★ **一个静默跳过的门禁，与没跑等价**（本项目已记录的第三种面孔）。
    """
    cgw = _load("check_gate_wiring")
    src = (Path(__file__).resolve().parents[1] / "scripts" / "release_check.py").read_text(
        encoding="utf-8")
    agg = cgw.aggregated_vars(src)
    # 真仓库：13 个都要在
    assert len(agg) >= 13, "返回体里只汇总了 %d 个门禁（少于 13）" % len(agg)


def test_gate_aggregation_detects_a_missing_entry():
    """★ 少汇总一个 ⇒ 判据必须能发现（用假源码测）。"""
    cgw = _load("check_gate_wiring")
    src = (
        "def run_release_check():\\n"
        "    a = _run_a_gate()\\n"
        "    b = _run_b_gate()\\n"
        '    _gate_results = {"a": a}\\n'          # ⚠ 漏了 b
        "    return {}\\n"
    )
    agg = cgw.aggregated_vars(src)
    assert "a" in agg and "b" not in agg, agg


def test_gate_skipped_is_exposed_in_the_return_body():
    """★★ 返回体必须**显式**给 `skipped` 列表 —— 不能让人去翻各段。

    ⚠ 「跳过了」如果只体现在各门禁自己的返回值里，读者**看不到**；
      而跳过的门禁**没有在检查** ⇒ 必须一眼可见。
    """
    src = (Path(__file__).resolve().parents[1] / "scripts" / "release_check.py").read_text(
        encoding="utf-8")
    assert '"skipped": skipped' in src, "返回体没有显式的 `skipped` 字段"
    assert '"skipped_count": len(skipped)' in src, "没有 skipped 的计数"
    assert '"gates": gates' in src, "没有把 13 个门禁状态一次列出"
'''

text = TARGET.read_text(encoding="utf-8")
if "test_gate_aggregation_covers_every_runner" in text:
    print("  已追加过")
else:
    TARGET.write_text(text + BLOCK, encoding="utf-8")
    print("  OK 已追加（%d -> %d 行）" % (len(text.splitlines()),
                                        len((text + BLOCK).splitlines())))
sys.stdout.reconfigure(encoding="utf-8")
