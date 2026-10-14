"""★ 契约测试：`mech-design` 的 3 个设计规则 YAML（★ 含 YAML 语法错的处理）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_design_rules.py
# 定位:   规格 `specs/335-design-rules-lib` 的契约测试。
#           ★★ 触发它的是 2026-10-14 全自动挖掘：`mech-design/知识库/` 的
#             **3 个 YAML**（设计规则 225 行 · 材料库 · 公差配合）。
# 官方依据: `~/.agents/skills/mech-design/知识库/*.yaml`（★ 只读）
# 许可:   本仓库 MIT。★ 外部数据只读；★ 测试**不复制数据**。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"),
                str(ROOT / "mcp-server"), str(ROOT / "tools")]

from scripts.engineering import design_rules as D                      # noqa: E402


def test_three_yaml_files_exist() -> None:
    """★ **三个 YAML 都在**（★ 业主早装好的）。"""
    r = D.report()
    for k in ("rules", "materials", "fits"):
        assert r[k]["exists"], "★ %s 不在" % k


#: ══ ★★ 材料库（★ 含 SolidWorks 牌号映射）═════════════════════════════

def test_material_count() -> None:
    """★ 材料库有 **14** 种。"""
    assert len(D.materials()) == 14


def test_45_steel_maps_to_sw_material() -> None:
    """★★★ **45钢 → `AISI 1020`** —— ★ 这是「设计选材 ↔ 建模填牌号」的桥。

    ★★ 判据：★ 中文名与 SolidWorks 牌号**不是同一个** ⇒
      ★ 建模时要填**牌号**，★ 而设计时说的是**中文名**。
    """
    assert D.sw_material_of("45钢") == "AISI 1020"


def test_45_steel_properties() -> None:
    """★ 45钢：屈服 **355** MPa · 密度 **7.85** g/cm³。"""
    m = D.material("45钢")
    assert m["yield_strength"] == 355
    assert m["density"] == 7.85


def test_40cr_is_stronger_than_45() -> None:
    """★★ **40Cr 屈服（785）> 45钢（355）** —— ★ 与 YAML 里的注一致。"""
    assert D.material("40Cr")["yield_strength"] > D.material("45钢")["yield_strength"]


def test_unknown_material_raises() -> None:
    """★ 材料不在库 ⇒ 报错（★ 不猜）。"""
    with pytest.raises(D.RuleError) as ei:
        D.material("不存在的钢")
    assert ei.value.code == "unknown-material"


#: ══ ★★ 公差配合 ══════════════════════════════════════════════════════

def test_fits_is_honest_about_unreadable() -> None:
    """★★★ **读不全就如实报**（★ 不假装读到）。

    ⚠⚠ 实测（2026-10-14）：`fits_iso286.yaml` **有多处 YAML 语法错** ——
      我**连着修了 3 类**（裸标量 / `:{` 缺空格 / `:"` 缺空格），
      ★ 到**第 4 类**（两个键挤在一行）时**按事实 53 停手**。
    ★★ 判据：★ **不继续加正则**（★ 那是「同一个启发式连续修补」）⇒
      ★ 而是**如实报「读不全」**。
    """
    d = D.fits_raw()
    #: ★ 要么读到了（★ 有真键），★ 要么**如实报读不全** —— ★ 两者都可接受
    ok = ("_yaml_unreadable" in d) or bool(
        [k for k in d if not k.startswith("_")])
    assert ok, "★ 既没读到、也没报读不全 ⇒ 那是静默失败"


def test_fits_unreadable_message_is_actionable() -> None:
    """★ 「读不全」的消息要**写清修了哪几类、剩哪类**（★ 可行动）。"""
    d = D.fits_raw()
    if "_yaml_unreadable" not in d:
        pytest.skip("★ 本机该文件已可读")
    msg = d["_yaml_unreadable"]
    for k in ("事实 53", "第 4 类", "①②③"):
        assert k in msg, "★ 消息缺 `%s`" % k


#: ══ ★★ 规则库（★ 读不全就如实报）════════════════════════════════════

def test_rules_is_honest() -> None:
    """★★ `design_rules.yaml` 同样**读不全就如实报**。

    ⚠ 实测：它**也有**第 4 类语法错（`design_rules.yaml` L222 的裸标量
      **加上**别处）⇒ ★ 按事实 53 **不继续修**。
    """
    d = D._load("rules")
    ok = ("_yaml_unreadable" in d) or bool(
        [k for k in d if not k.startswith("_")])
    assert ok


def test_rule_raises_when_unreadable() -> None:
    """★ 读不全时查规则 ⇒ **响亮报错**（★ 不假装查到）。"""
    d = D._load("rules")
    if "_yaml_unreadable" not in d:
        pytest.skip("★ 本机该文件已可读")
    with pytest.raises(D.RuleError) as ei:
        D.rule("general.bolt.min_spacing")
    assert ei.value.code == "no-lib"
    assert "不假装查到" in ei.value.detail


#: ══ ★★★ 三类 YAML 修复（★ 逐类验）══════════════════════════════════

def test_repair_adds_dash_to_bare_scalar() -> None:
    """★ **① 类**：块下**裸标量** ⇒ 补 `-`（★ 只在内存里）。"""
    bad = 'sealing:\n  "金属垫片"\n  "软垫片"\n'
    fixed = D._repair_bare_scalars(bad)
    assert '- "金属垫片"' in fixed
    assert '- "软垫片"' in fixed


def test_repair_adds_space_before_brace() -> None:
    """★ **② 类**：`key:{` 的 `:` 后**缺空格** ⇒ 补一个。"""
    bad = '  "0_3":{H6: [6, 0]}\n'
    assert D._repair_bare_scalars(bad).strip() == '"0_3": {H6: [6, 0]}'


def test_repair_adds_space_before_quote() -> None:
    """★ **③ 类**：`key:"v"` 的 `:` 后**缺空格** ⇒ 补一个。"""
    bad = 'H11/c11:"间隙 非常松"\n'
    out = D._repair_bare_scalars(bad).strip()
    assert out == 'H11/c11: "间隙 非常松"'


def test_repair_is_idempotent() -> None:
    """★ 修复**幂等**（★ 修两次结果一样 —— ★ 三类互不干扰）。"""
    bad = 'a:\n  "x"\n  "0_3":{H6: [6, 0]}\n  H11/c11:"v"\n'
    once = D._repair_bare_scalars(bad)
    assert D._repair_bare_scalars(once) == once


def test_repair_does_not_touch_good_yaml() -> None:
    """★ **好 YAML 不被改**（★ 不误伤）。"""
    good = 'a: 1\nb:\n  - "x"\n  - "y"\nc: "v"\n'
    assert D._repair_bare_scalars(good) == good


#: ══ ★★ 不静默改用户文件 ══════════════════════════════════════════════

def test_repair_never_writes_the_source_file() -> None:
    """★★★ **修复只在内存里** —— ★ **原文件一个字节都不动**。

    ★★ 判据：★ 那是**用户的资产**（★ `mech-design` skill 的一部分）⇒
      ★ 本模块**只读**。
    """
    before = {}
    for f in D.FILES.values():
        p = D.KB / f
        if p.is_file():
            before[f] = p.read_bytes()
    #: ★ 触发一次读（★ 会走修复路径）
    D._load("rules")
    D._load("fits")
    for f, b in before.items():
        assert (D.KB / f).read_bytes() == b, "★★ %s 被改了！" % f


def test_report_shape() -> None:
    """★ 总览含三块 + 材料数 + 规则组。"""
    r = D.report()
    for k in ("source", "rules", "materials", "fits", "material_count"):
        assert k in r
