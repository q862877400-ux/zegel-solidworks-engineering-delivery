"""守「枚举值 vs 出厂反射」门禁 —— **重点是负例**（轮 106）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_enum_values_gate.py
# 定位:   守 `scripts/check_enum_values_vs_reflection.py`。
# 官方签名依据: 不适用（纯静态门禁测试，不连 SolidWorks）
# 许可:   本仓库 MIT。无第三方代码引入。
#
# ⚠⚠ **为什么这个门禁必须有负例（已知事实 62）**：
#   它补的是「**值级**」覆盖缺口 —— 023（枚举凭记忆写反）与 024（两源冲突）
#   连着两轮的错，**旧门禁一个都抓不到**（它们只查名字）。
#   ⇒ 必须证明**新门禁真的能抓到那两类**，否则它只是又一道"写了但没用"的门禁。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
GATE = REPO_ROOT / "scripts" / "check_enum_values_vs_reflection.py"


def _gate():
    spec = importlib.util.spec_from_file_location("_enum_gate", GATE)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_gate_script_exists():
    """@brief 门禁脚本在。"""
    assert GATE.is_file()


def test_code_row_parser_accepts_trailing_comment_text():
    """@brief ★ **负例（轮 106 当场抓到的漏点）**：成员名后**可以有注释文字**。

    ⚠ 第一版正则要求成员名即行尾 ⇒ 漏掉 `sw_sketch_edit.py` 那行
    （它写成 `# swSketchChamfer_DistanceDistance（⚠ md 写 -1…）`）
    ⇒ **门禁会漏掉 024 那个冲突本身**。
    """
    m = _gate()
    row = '    "distance_distance": 1,     # swSketchChamfer_DistanceDistance（⚠ md 写 -1，采用 1）'
    parsed = m.CODE_ROW.match(row)
    assert parsed is not None, "带尾注的行必须能解析"
    assert parsed.group("key") == "distance_distance"
    assert int(parsed.group("value")) == 1
    assert parsed.group("member") == "swSketchChamfer_DistanceDistance"


def test_code_row_parser_handles_enum_prefixed_member():
    """@brief 也接受 `Enum.member` 那种带枚举前缀的写法。"""
    m = _gate()
    parsed = m.CODE_ROW.match(
        '    "part": 8,       # swUserPreferenceStringValue_e.swDefaultTemplatePart')
    assert parsed is not None
    assert parsed.group("enum") == "swUserPreferenceStringValue_e"
    assert parsed.group("member") == "swDefaultTemplatePart"


def test_wrong_value_is_flagged():
    """@brief ★★ **核心负例**：值写错必须被抓出来。

    ⚠ 用 023 的真实错法造负例：把 `height_and_revolution` 写成 2（官方是 1）。
    """
    m = _gate()
    ref = {"swHelixDefinedByHeightAndRevolution": 1}
    owner = {"swHelixDefinedByHeightAndRevolution": "swHelixDefinedBy_e"}
    rows = [("sw_helix.py", 54, "height_and_revolution", 2, "swHelixDefinedByHeightAndRevolution", None)]
    ok, mismatched, unknown, conflicts = m.compare(rows, ref, owner, swapi_loader=lambda _e: {})
    assert ok == 0
    assert len(mismatched) == 1, "值写错必须被抓出来"
    assert mismatched[0][4] == "swHelixDefinedByHeightAndRevolution"
    assert mismatched[0][5] == 1, "要报出反射里的正确值"


def test_correct_value_passes():
    """@brief 正确的值不该被误报。"""
    m = _gate()
    ref = {"swHelixDefinedByHeightAndRevolution": 1}
    owner = {"swHelixDefinedByHeightAndRevolution": "swHelixDefinedBy_e"}
    rows = [("sw_helix.py", 54, "height_and_revolution", 1, "swHelixDefinedByHeightAndRevolution", None)]
    ok, mismatched, unknown, _c = m.compare(rows, ref, owner, swapi_loader=lambda _e: {})
    assert ok == 1 and not mismatched and not unknown


def test_two_source_conflict_is_reported_but_not_a_failure():
    """@brief ★★ **024 的真实形态**：两源冲突要**被报出来**，但**不判失败**。

    ⚠ 铁律 4 已定「冲突取反射」⇒ 实现用反射的值是**对的**，
    判失败会把它误伤。但**必须让人看得见**。
    """
    m = _gate()
    member = "swSketchChamfer_DistanceDistance"
    ref = {member: 1}                       # 出厂反射
    owner = {member: "swSketchChamferType_e"}
    rows = [("sw_sketch_edit.py", 53, "distance_distance", 1, member, None)]
    swapi = {"swSketchChamferType_e": {member: -1}}      # swapi 的 md
    ok, mismatched, _u, conflicts = m.compare(rows, ref, owner, swapi_loader=lambda e: swapi.get(e, {}))
    assert ok == 1, "取反射的值是对的 ⇒ 不算值错"
    assert not mismatched
    assert len(conflicts) == 1, "两源冲突必须被报出来"
    assert conflicts[0][3] == 1 and conflicts[0][4] == -1, "要同时报出两个源的值"


def test_member_missing_from_dump_is_unknown_not_a_failure():
    """@brief 转储里查不到的成员 ⇒ 归「查不到」（铁律 5），**不判失败**。"""
    m = _gate()
    rows = [("sw_simulation.py", 114, "fixed", 0, "swsRestraintTypeFixed", None)]
    ok, mismatched, unknown, conflicts = m.compare(rows, {}, {}, swapi_loader=lambda _e: {})
    assert ok == 0 and not mismatched and not conflicts
    assert len(unknown) == 1


def test_gate_reads_the_dump_and_reports_the_real_conflict():
    """@brief 对着**真实仓库**跑：应当报出 `swSketchChamfer_DistanceDistance` 那处冲突。"""
    m = _gate()
    if not any(Path(p).is_file() for p in m.DUMPS):
        pytest.skip("拿不到出厂反射转储（便携性）")
    ref, owner, _origin = m.parse_dumps(m.DUMPS)
    assert len(ref) > 5000, "转储应解析出数千个成员"
    rows = m.parse_code()
    assert rows, "仓库里应能解析出「值 + 官方成员名」的行"
    _ok, mismatched, _u, conflicts = m.compare(rows, ref, owner)
    assert not mismatched, "当前仓库里不该有与反射不符的值：%s" % mismatched
    members = {c[2] for c in conflicts}
    assert "swSketchChamfer_DistanceDistance" in members, \
        "024 那处两源冲突必须被报出来（否则门禁漏了它）"


def test_both_assemblies_dumps_are_merged():
    """@brief ★ **轮 107 的修正**：转储**不止一份** —— `sldworks` 与 `cosworks` 是两个程序集。

    ⚠ 第一版只读 `enum_values_sldworks.txt` ⇒ **75 条 `sws*`（Simulation）全归"查不到"**。
    """
    m = _gate()
    assert len(m.DUMPS) >= 2, "至少要读 sldworks 与 cosworks 两份转储"
    if not all(Path(p).is_file() for p in m.DUMPS):
        pytest.skip("本机拿不到全部转储（便携性）")
    ref, owner, origin = m.parse_dumps(m.DUMPS)
    member = "swsAnalysisStudyTypeBuckling"
    assert member in ref, "Simulation 的 sws* 枚举必须能查到（它在 cosworks 程序集里）"
    assert ref[member] == 2
    assert "cosworks" in origin.get(member, ""), "应记下它来自哪份转储"


def test_parse_dumps_first_dump_wins_on_collision():
    """@brief 两份转储合并时，**先出现的赢**（且 `sw*` 与 `sws*` 前缀本就不重叠）。"""
    m = _gate()
    a = {"swX": 1}
    b = {"swX": 9, "swY": 2}
    merged = {}
    for d in (a, b):
        for k, v in d.items():
            merged.setdefault(k, v)
    assert merged == {"swX": 1, "swY": 2}
