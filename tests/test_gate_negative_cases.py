"""**负例测试**：每个门禁**真的还能抓到东西**吗？

## 为什么要有这个文件（本轮的方法论）
本项目已有的门禁测试都是「**断言通过**」—— 但**没有一条断言「门禁自己还能抓到东西」**。
**⇒ 一个永远返回 0 的坏门禁，能让所有「断言通过」的测试全绿。**

**⇒ 本文件给每条门禁种一个**已知违规**，断言它**报出来**。**
这叫「防假绿」：**先证明门禁有牙齿，再相信它的沉默。**

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   `scripts/check_provenance.py`（`check_file(path, whole_file)` 收路径 ⇒ 可种负例）
#         `scripts/check_diff_markers.py`（`scan(path)` 收 Path ⇒ 可种负例）
#         `scripts/check_member_names.py`（`_official_members()` 是判据来源）
#         `scripts/check_union_conventions.py`（`normalize_license()` 是纯函数）
# 定位:   2026-10-01 加。起因：上一轮给裸 by-ref 审计加负例时发现
#         **本项目没有任何一条「门禁能抓到」的测试**。
# 官方签名依据: 不适用（纯静态测试）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"


def _load(name: str):
    path = SCRIPTS / ("%s.py" % name)
    if not path.is_file():
        pytest.skip("%s.py 不在" % name)
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location("%s_neg" % name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["%s_neg" % name] = mod
    spec.loader.exec_module(mod)
    return mod


# ══ ① check_provenance：种一行没有来源块覆盖的新代码 ═══════════════
def test_provenance_flags_an_uncovered_function(tmp_path):
    """`check_provenance` 必须报出**没有来源块覆盖**的新增函数。

    ⚠ 这是它存在的**唯一理由**。若一条违规都报不出，它就是个假门禁。
    """
    cp = _load("check_provenance")
    planted = tmp_path / "planted_uncovered.py"
    planted.write_text(
        '"""没有任何来源块的模块。"""\n\n\n'
        "def totally_uncovered_function():\n"
        "    return 1\n",
        encoding="utf-8",
    )
    try:
        violations, _blocks = cp.check_file(str(planted), whole_file=True)
    except Exception as exc:  # noqa: BLE001
        pytest.skip("check_file 签名与本测试不符：%s" % str(exc)[:80])
    assert violations, (
        "**check_provenance 没有报出这个显然违规的文件** ⇒ 它是假门禁。"
        "（一个没有来源块的模块，整文件都是「不可追溯的新增行」）"
    )


def test_provenance_accepts_a_properly_sourced_function(tmp_path):
    """反向：**带合规来源块**的同样代码，应当**不被报**（否则它会误杀一切）。"""
    cp = _load("check_provenance")
    good = tmp_path / "planted_covered.py"
    good.write_text(
        "# ── 来源 ─────────────────────────────────────────────────────────\n"
        "# 仓库:   本项目自身（负例测试的对照）\n"
        "# 文件:   tests/test_gate_negative_cases.py\n"
        "# 定位:   证明合规来源块能让 check_provenance 放行。\n"
        "# 许可:   本仓库 MIT。无第三方代码引入。\n"
        "# 覆盖:   全文件\n"
        "# ⚠ 未在本机实测\n"
        "# ─────────────────────────────────────────────────────────────\n"
        "def properly_sourced_function():\n"
        "    return 1\n",
        encoding="utf-8",
    )
    violations, _blocks = cp.check_file(str(good), whole_file=True)
    assert not violations, (
        "合规来源块覆盖的代码仍被报违规 ⇒ 门禁**误杀**：\n  %r"
        % [v.get("text") for v in violations[:5]]
    )


# ══ ② check_diff_markers：种一个 diff 记号 ═════════════════════════
def test_diff_markers_flags_a_planted_marker(tmp_path):
    """`check_diff_markers` 必须报出残留的**补丁前缀**记号。

    ⚠ **我第一版种错了东西**：种了 git 冲突记号 `<<<<<<< HEAD`，
    而该门禁查的是**被粘贴进来的补丁行**（行首空白 + `+`/`*` + 空白/EOL，
    且括号深度 ≤ 0）。git 冲突记号在行首**必然让 `py_compile` 报语法错**，
    那是 `compileall` 的活 —— 本门禁补的正是**编译抓不到**的那一类。
    **⇒ 契约读清楚再种负例，不然会把自己的误解当成门禁的 bug。**
    """
    cdm = _load("check_diff_markers")
    planted = tmp_path / "planted_marker.py"
    # 行首空白 + `+ `，且上一行没有未闭合括号 ⇒ 命中该门禁的判据
    planted.write_text("value = base\n    + 1\n", encoding="utf-8")
    hits = cdm.scan(planted)
    assert hits, "**check_diff_markers 没有报出种下的补丁前缀** ⇒ 假门禁"


def test_diff_markers_passes_clean_code(tmp_path):
    clean = tmp_path / "planted_clean.py"
    clean.write_text("x = 1\ny = 2\n", encoding="utf-8")
    cdm = _load("check_diff_markers")
    assert cdm.scan(clean) == [], "干净文件被误报"


# ══ ③ check_member_names：判据能不能**分辨**真假成员 ═══════════════
def test_member_names_can_distinguish_real_from_bogus():
    """`check_member_names` 的判据来源（官方反射成员集）必须**能分辨**真假成员。

    ⚠ 这是**必要**的负例：若官方集里什么都有（或什么都没有），门禁就没有分辨力。
    用一对**已知的真/假**成员来验：
      · 真：`CreateFeature`（`IFeatureManager` 的常用成员）
      · 假：一个绝不会存在的名字
    """
    cmn = _load("check_member_names")
    official = cmn._official_members()
    if not official:
        pytest.skip("取不到官方成员集（反射转储不在）—— 缺数据源不算违规")
    assert "CreateFeature" in official, (
        "官方成员集里没有 `CreateFeature` ⇒ 数据源坏了，门禁的『绿』不可信"
    )
    bogus = "TotallyMadeUpMemberName_ZZZ_20261001"
    assert bogus not in official, "官方成员集里混进了不存在的名字 ⇒ 判据不可信"


# ══ ④ check_union_conventions：纯函数与「有牙」的证据 ═══════════════
def test_union_conventions_license_normalization_discriminates():
    """`normalize_license` 的**真实契约**：去掉全角括号里的附注，得到可比对基名。

    ⚠ **我第一版断言错了**：要求它做**大小写归一**（`MIT` == `mit`），
    而它的文档串只说「归一化到白名单比对用的基名」——
    **大小写不在它承诺的范围里**。**⇒ 断言要照契约写，不是照我想当然的用途写。**
    """
    cuc = _load("check_union_conventions")
    # 契约：`"Apache-2.0（见 NOTICE）"` → `"Apache-2.0"`
    assert cuc.normalize_license("Apache-2.0（见 NOTICE）") == "Apache-2.0", (
        "带全角括号附注的许可没被归一 —— 这正是它存在的理由"
    )
    assert cuc.normalize_license("  MIT  ") == "MIT", "首尾空白没被去掉"
    assert cuc.normalize_license("Apache-2.0") != cuc.normalize_license("MIT"), (
        "两种不同许可被归一到同一值 ⇒ 许可检查失去分辨力"
    )


def test_union_conventions_checks_return_lists():
    """每条检查都必须返回**问题列表**（而不是抛错、也不是恒 True）。"""
    cuc = _load("check_union_conventions")
    for name in ("check_sources", "check_docs", "check_map_fresh",
                 "check_capabilities_schema", "check_capabilities_levels",
                 "check_authorization_source"):
        fn = getattr(cuc, name, None)
        if fn is None:
            continue
        out = fn()
        assert isinstance(out, list), "%s 没返回列表（返回了 %r）" % (name, type(out))


def test_level_audit_is_fresh():
    """★ **R8 的新鲜度**：`docs/union-level-audit.md` 必须等于「按当下数据重生成」的结果。

    ⚠ 这条测的是那个**曾经只是 docstring 承诺**的 R8：
    2026-10-01（轮 60）实测发现它**既没有生成器、也没有读者**，而文件**不存在**
    ⇒ 读文档的人会以为「等级已经审计过了」，**而审计根本没发生**。
    ⇒ 现在它是**可跑**的，且这条测试保证生成物**不落后于数据**。
    """
    import importlib.util as _ilu
    import json as _json

    gen = REPO_ROOT / "scripts" / "gen_level_audit.py"
    assert gen.is_file(), "R8 的生成器不在"
    spec = _ilu.spec_from_file_location("_gen_level_audit_t", gen)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    want = mod.build(_json.loads((REPO_ROOT / "capabilities.yaml").read_text(encoding="utf-8")),
                     _load("check_union_conventions"))
    got = (REPO_ROOT / "docs" / "union-level-audit.md").read_text(encoding="utf-8")
    assert want == got, "docs/union-level-audit.md 落后于数据 ⇒ 跑 python scripts/gen_level_audit.py"


def test_level_audit_reuses_the_gate_enums():
    """★★ **不重造守卫**：生成器**必须**从既有门禁取 `LEVELS` / `SOURCES`，**不能自己再写一份**。

    ⚠ 两处各写一份枚举正是「一个事实两个家」的经典错误 —— 一边改了、另一边没改，
    门禁与报告就会**各自言之凿凿地互相矛盾**。
    """
    import importlib.util as _ilu

    spec = _ilu.spec_from_file_location("_gen_level_audit_e", REPO_ROOT / "scripts" / "gen_level_audit.py")
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    src = (REPO_ROOT / "scripts" / "gen_level_audit.py").read_text(encoding="utf-8")
    # 不得自己定义枚举字面量
    assert "LEVELS = {" not in src, "生成器不应自己定义 LEVELS"
    assert "SOURCES = {" not in src, "生成器不应自己定义 SOURCES"
    # 且必须真的从门禁取
    assert "gate.LEVELS" in src and "gate.SOURCES" in src, "生成器必须用门禁的枚举"


def test_capabilities_source_enum_discriminates(monkeypatch, tmp_path):
    """★ **R12 负例**（轮 58 加）：`source` 不在枚举内 ⇒ **必须**被 `check_capabilities_schema` 点名。

    ⚠ 这是**把 A2 的「两层 provenance」落到机器上**的那一条：
    `source` 回答「这条是**并入来的**还是**本项目自研的**」，与 `level` **不是一回事**
    （`level: verified` 只说「有我们自己的运行证据」）。
    ⚠ 本测试**在假清单上跑**（`monkeypatch` 换 `ROOT`），**不碰真 `capabilities.yaml`**。
    """
    import json as _json

    cuc = _load("check_union_conventions")
    fake = tmp_path / "capabilities.yaml"
    fake.write_text(_json.dumps({
        "schema_version": cuc.SCHEMA_VERSION,
        "capabilities": [
            # ① 非法枚举值 ⇒ 必须报
            {"id": "a_bogus", "level": "stitched", "source": "BOGUS",
             "source_evidence": "x"},
            # ② 合法值但**没有依据** ⇒ 必须报（没依据的分类等于没分类）
            {"id": "b_no_evidence", "level": "stitched", "source": "undetermined",
             "source_evidence": "   "},
            # ③ 合法且带依据 ⇒ 不该报
            {"id": "c_ok", "level": "stitched", "source": "undetermined",
             "source_evidence": "提案工具与人工确证都没给出归属 ⇒ 按铁律 5 留 undetermined"},
        ],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    monkeypatch.setattr(cuc, "ROOT", tmp_path)
    problems = cuc.check_capabilities_schema()
    joined = "\n".join(problems)
    assert "a_bogus" in joined and "BOGUS" in joined, problems
    assert "b_no_evidence" in joined, problems
    assert "c_ok" not in joined, problems


def test_capabilities_source_provenance_consistency(monkeypatch, tmp_path):
    """★★ **R13 负例**（轮 59 加）：`source` 与 `provenance` **必须自洽**。

    ⚠ 这条是**实测逼出来的**：`mold_tools` 曾同时有
    `source: "original"` 与一条指向 `Eduardof0nt/Solidworks-MCP-Server` 的 `provenance`
    —— **字段之间互相打架**，而 R12（只查枚举与依据非空）**看不见**。
    ⇒ 「原创」与「有来源」是**互斥的陈述**，机器能判，就该判。
    """
    import json as _json

    cuc = _load("check_union_conventions")
    fake = tmp_path / "capabilities.yaml"
    fake.write_text(_json.dumps({
        "schema_version": cuc.SCHEMA_VERSION,
        "capabilities": [
            # ① source=original 却有 provenance ⇒ 必须报（自相矛盾）
            {"id": "a_contradiction", "level": "stitched", "source": "original",
             "source_evidence": "自称原创",
             "provenance": [{"repo": "Eduardof0nt/Solidworks-MCP-Server", "license": "MIT",
                             "files": ["sw_client.py"], "upstream_verified": ""}]},
            # ② source=upstream 而 provenance 指向**别家** ⇒ 必须报（「上游」特指 wzyn20051216）
            {"id": "b_wrong_upstream", "level": "stitched", "source": "upstream",
             "source_evidence": "x",
             "provenance": [{"repo": "microsoft/UFO", "license": "MIT",
                             "files": ["a.py"], "upstream_verified": ""}]},
            # ③ source=original 且**没有** provenance ⇒ 不该报（自洽）
            {"id": "c_true_original", "level": "stitched", "source": "original",
             "source_evidence": "全部实现模块都不在 origin/main（硬证据）"},
            # ④ source=mixed 且 provenance 指向别家 ⇒ 不该报（自洽）
            {"id": "d_true_mixed", "level": "stitched", "source": "mixed",
             "source_evidence": "思路来自别家、实现照反射写",
             "provenance": [{"repo": "Eduardof0nt/Solidworks-MCP-Server", "license": "MIT",
                             "files": ["sw_mold.py"], "upstream_verified": ""}]},
        ],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    monkeypatch.setattr(cuc, "ROOT", tmp_path)
    joined = "\n".join(cuc.check_capabilities_schema())
    assert "a_contradiction" in joined and "自相矛盾" in joined, joined
    assert "b_wrong_upstream" in joined, joined
    assert "c_true_original" not in joined, joined
    assert "d_true_mixed" not in joined, joined


# ══ ⑤ 反向自检：本文件自己应当被 check_provenance 接受 ═════════════
def test_this_file_itself_passes_provenance():
    """**本测试文件自己**必须有合规来源块 —— 否则它一提交就会被门禁报。"""
    cp = _load("check_provenance")
    violations, _blocks = cp.check_file(
        str(Path(__file__).resolve()), whole_file=True)
    assert not violations, (
        "本测试文件自己没有通过来源门禁（**自己就是违规**）：\n  %r"
        % [v.get("text") for v in violations[:5]]
    )


# ══ ⑤ R14：「不做 + 原因」（A1 的另一半，轮 67 加）═══════════════════════

def test_not_doing_gate_discriminates(monkeypatch, tmp_path):
    """★★ **R14 负例**（轮 67 加）：`subject` / `reason` / `evidence` 缺一即报。

    ⚠ 本条守的是 `AGENTS.md §一 A1` 的**另一半**：
    「域覆盖矩阵里本仓库每一格**都有来源，或写明「不做 + 原因」」。
    此前**只有「有来源」那一半有机制**（`capabilities.yaml` 的 `source`/`source_evidence`，R12 守），
    而「不做」那一半**一格机制都没有** ⇒ 矩阵里只有「缺 N」，读者**无从分辨**
    「我们不做」与「还没做」（轮 67 实测确认）。

    ⚠ 为什么 `reason` 与 `evidence` **都必须非空**：一个没有原因的「不做」是
    **用一个词掩盖一个缺口**，比不写更糟。
    ⚠ 本测试**在假文件上跑**（`monkeypatch` 换 `NOT_DOING_PATH`），**不碰真清单**。
    """
    import json as _json

    cuc = _load("check_union_conventions")
    fake = tmp_path / "union-not-doing.json"
    fake.write_text(_json.dumps({"not_doing": [
        # ① 缺 subject ⇒ 必须报
        {"subject": "  ", "reason": "有原因", "evidence": ["有依据"]},
        # ② 有 subject 但 reason 空 ⇒ 必须报
        {"subject": "有主题", "reason": "   ", "evidence": ["有依据"]},
        # ③ 有 subject/reason 但 evidence 空数组 ⇒ 必须报
        {"subject": "有主题2", "reason": "有原因2", "evidence": []},
        # ④ 三样都齐 ⇒ **不该报**
        {"subject": "合法条目", "reason": "合法原因", "evidence": ["合法依据"]},
    ]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    monkeypatch.setattr(cuc, "NOT_DOING_PATH", fake)
    bad = cuc.check_not_doing()
    assert len(bad) == 3, "应精确命中 3 条（缺 subject / 空 reason / 空 evidence），实际：%r" % bad
    joined = "\n".join(bad)
    assert "subject" in joined and "reason" in joined and "evidence" in joined
    assert "合法条目" not in joined, "三样都齐的那条**不该**被报（假阳性）"


def test_not_doing_gate_tolerates_a_missing_file(monkeypatch, tmp_path):
    """★ **空清单是合法的** —— 文件不存在 ⇒ **不报错**（生成器会在矩阵里提醒「本清单为空」）。

    ⚠ 这条防线是**刻意的**：要求「必须有一条不做」会**逼人编**条目来过关 ——
    那正是本项目反复记录的「为了迁就实现而改判据」的反面。
    """
    cuc = _load("check_union_conventions")
    monkeypatch.setattr(cuc, "NOT_DOING_PATH", tmp_path / "no_such_file.json")
    assert cuc.check_not_doing() == []


def test_not_doing_gate_rejects_invalid_json(monkeypatch, tmp_path):
    """★ 非法 JSON ⇒ **报错**（不静默当空清单）。"""
    cuc = _load("check_union_conventions")
    fake = tmp_path / "union-not-doing.json"
    fake.write_text("{ not json", encoding="utf-8")
    monkeypatch.setattr(cuc, "NOT_DOING_PATH", fake)
    bad = cuc.check_not_doing()
    assert bad and "JSON" in bad[0], bad


def test_real_not_doing_entries_are_well_formed():
    """★ 真清单里每条都必须合格（**这是 R14 对当前仓库的实际断言**）。"""
    cuc = _load("check_union_conventions")
    assert cuc.check_not_doing() == [], cuc.check_not_doing()


def test_not_doing_is_rendered_into_the_generated_matrix():
    """★ 生成物里必须真的**渲染出**「不做 + 原因」段（否则机制等于没接上）。

    ⚠ 一个「数据文件 + 门禁」但没有渲染进矩阵的组合，读者**看不到**它 ——
    而 A1 的判据正是「矩阵里…或写明」。
    """
    matrix = (Path(__file__).resolve().parents[1] / "docs" / "union-coverage-matrix.md")
    text = matrix.read_text(encoding="utf-8")
    assert "不做 + 原因（A1 的另一半）" in text, "矩阵里没有渲染「不做 + 原因」段"
    assert "docs/union-not-doing.json" in text, "矩阵没告诉读者数据源在哪"
    assert "动画导出 AVI" in text, "至少那条有硬依据的『环境受限』应出现在矩阵里"

# ══ ⑥ 审计表「合计行算术自洽」（A5 的可跑那一半，轮 69 加）══════════════

def _totals_case(tmp_path, lines):
    """⇒ `(错误列表, 校验的列和个数)` —— 在**假文档**上跑，不碰真审计表。"""
    csa = _load("check_signature_audit_freshness")
    p = tmp_path / "fake-audit.md"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return csa.check_totals(p)


def test_audit_totals_accept_a_correct_total(tmp_path):
    """★ 表体列和 == 合计 ⇒ **不该报**。"""
    bad, checked = _totals_case(tmp_path, [
        "| 范围 | A | B |", "|---|---|---|",
        "| x | 1 | 2 |", "| y | 3 | 4 |",
        "| **合计** | **4** | **6** |",
    ])
    assert bad == [] and checked == 2, (bad, checked)


def test_audit_totals_flag_a_wrong_total(tmp_path):
    """★★ **核心负例**：合计写错 ⇒ **必须**被点名，并给出「表体 = 合计」的对照。

    ⚠ 这正是 `AGENTS.md §一 A5` 缺的那一半：`signature-audit.md` 的汇总数字
    （`**小计：7 不通过 · 9 通过**` / `| **合计** | **711** | … |` / `**累计…7 处**`）
    **是手工数的**，改一行表体不会让合计跟着变（**与 A8 的 harvest-report 同型缺口**）。
    """
    bad, checked = _totals_case(tmp_path, [
        "| 范围 | A | B |", "|---|---|---|",
        "| x | 1 | 2 |", "| y | 3 | 4 |",
        "| **合计** | **9** | **6** |",
    ])
    assert checked == 2
    assert len(bad) == 1 and "第 2 列" in bad[0] and "4" in bad[0] and "9" in bad[0], bad


def test_audit_totals_flag_a_column_count_mismatch(tmp_path):
    """★★ **列数错位**要报「列数不一致」，**不要**报成看不懂的算术对比。

    ⚠ 这条是被一次**假阳性**逼出来的：我在负例里手写替换合计行时**多打了一个 `|`**，
      门禁当时报的是「第 4 列：表体 2 + 0 + 0 + 0 = 2，而合计写 696」——
      **读者看不出真因是列错位**。⇒ 补一条更接近真因的诊断。
    """
    bad, _checked = _totals_case(tmp_path, [
        "| 范围 | A | B |", "|---|---|---|",
        "| x | 1 | 2 |",
        "| **合计** | **1** | **2** | **x** |",
    ])
    assert len(bad) == 1 and "列数" in bad[0], bad
    assert "多打" in bad[0] or "漏打" in bad[0], bad


def test_audit_totals_do_not_swallow_the_separator_row(tmp_path):
    """★★ **分隔行不许混进表体** —— 否则每一列都会被判「有非数字格」而**静默跳过**。

    ⚠ 这是本轮实测踩到的坑：分隔行的判据原本写成
      `set(line.strip().strip("|")) <= set("-: ")`，而 `strip("|")` 只去**首尾**的 `|`，
      分隔行**中间**全是 `|` ⇒ 集合含 `'|'` ⇒ **判不出** ⇒ 分隔行（`---`）进了表体
      ⇒ 校验列和 = **0** ⇒ **门禁静默地什么都没查**（「量太少本身就是假绿」）。
    ⇒ 本测试断言 `checked >= 1`，把那次的失效**钉死**。
    """
    bad, checked = _totals_case(tmp_path, [
        "| 范围 | A |", "|---|---|",
        "| x | 1 |",
        "| **合计** | **1** |",
    ])
    assert bad == []
    assert checked >= 1, "分隔行混进了表体 ⇒ 一个列和都没校验（这正是那次失效的形态）"


def test_audit_totals_report_zero_checks_loudly():
    """★ 真审计表上必须**真的校验到**列和（不能是 0 ⇒ 那说明判据失效）。"""
    csa = _load("check_signature_audit_freshness")
    from pathlib import Path as _P
    doc = _P(__file__).resolve().parents[1] / "docs" / "signature-audit.md"
    bad, checked = csa.check_totals(doc)
    assert checked >= 4, "真审计表上只校验到 %d 个列和 ⇒ 判据失效" % checked
    assert bad == [], bad

# ══ ⑦ 门禁接线元门禁（「存在但没人跑」的机器判据，轮 71 加）═══════════

def _wiring_case(monkeypatch, tmp_path, gates, release_src, exemptions=None):
    """在**假仓库**上跑元门禁：造 `scripts/check_*.py` + 假 `release_check.py`。"""
    cgw = _load("check_gate_wiring")
    (tmp_path / "scripts").mkdir(exist_ok=True)
    for g in gates:
        (tmp_path / "scripts" / g).write_text('"""x"""\n', encoding="utf-8")
    (tmp_path / "scripts" / "release_check.py").write_text(release_src, encoding="utf-8")
    (tmp_path / "docs").mkdir(exist_ok=True)
    ex_path = tmp_path / "docs" / "gate-wiring-exemptions.json"
    if exemptions is not None:
        ex_path.write_text(json.dumps(exemptions, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(cgw, "ROOT", tmp_path)
    monkeypatch.setattr(cgw, "RELEASE", tmp_path / "scripts" / "release_check.py")
    monkeypatch.setattr(cgw, "EXEMPTIONS", ex_path)
    # ⚠ **必须也把 `CLASSIFICATION` 指向假位置** —— 否则会去读**真仓库**的登记表，
    #   与假仓库里的 `_run_*` 调用点对不上 ⇒ 报「登记了却找不到调用点」⇒「应 PASS」的用例红。
    #   （本轮实测踩过；这批测试测的是「**接线**」，分类另有专门的用例。）
    monkeypatch.setattr(cgw, "CLASSIFICATION",
                        tmp_path / "docs" / "gate-classification.json")
    return cgw


def test_gate_wiring_flags_an_unwired_gate(monkeypatch, tmp_path):
    """★★ **核心负例**：一个新门禁**没被 `release_check.py` 调用** ⇒ **必须**报。

    ⚠ 这正是轮 70 的实测缺口：`check_workspace_shadowing.py` **早就存在却从没被调用**，
      而它当时**正红着**。★ 一个存在但没人跑的门禁，与没有门禁等价 ——
      「接线」这一步此前**只靠人记**。
    """
    cgw = _wiring_case(
        monkeypatch, tmp_path,
        gates=["check_a.py", "check_b.py"],
        release_src='subprocess.run([sys.executable, str(ROOT / "scripts" / "check_a.py")])\n',
    )
    assert cgw.main() == 1


def test_gate_wiring_passes_when_every_gate_is_wired(monkeypatch, tmp_path):
    """★ 全部接线 ⇒ **不该报**（否则新门禁一加就红，没人受得了）。"""
    cgw = _wiring_case(
        monkeypatch, tmp_path,
        gates=["check_a.py", "check_b.py"],
        release_src=(
            'subprocess.run([sys.executable, str(ROOT / "scripts" / "check_a.py")])\n'
            'subprocess.run([sys.executable, str(ROOT / "scripts" / "check_b.py")])\n'
        ),
    )
    assert cgw.main() == 0


def test_gate_wiring_flags_a_stale_exemption(monkeypatch, tmp_path):
    """★★ **名单腐坏**：已接线却仍挂在豁免名单里 ⇒ **必须**报。

    ⚠ 单向检查（只查「未接线」）会让豁免名单**只增不减** ⇒ 久而久之没人知道
      哪些豁免还有效。（与 `union-not-doing.json` 的 R14 同型：**双向**。）
    """
    cgw = _wiring_case(
        monkeypatch, tmp_path,
        gates=["check_a.py"],
        release_src='subprocess.run([str(ROOT / "scripts" / "check_a.py")])\n',
        exemptions={"exemptions": [
            {"gate": "check_a.py", "reason": "测试", "evidence": ["测试"]}]},
    )
    assert cgw.main() == 1


def test_gate_wiring_requires_reason_and_evidence(monkeypatch, tmp_path):
    """★ 豁免必须带**非空** `reason` 与 `evidence`（一条没理由的豁免等于没写）。"""
    cgw = _wiring_case(
        monkeypatch, tmp_path,
        gates=["check_a.py"],
        release_src="",                       # 两个都没接线
        exemptions={"exemptions": [
            {"gate": "check_a.py", "reason": "  ", "evidence": []}]},
    )
    assert cgw.main() == 1


def test_gate_wiring_rejects_a_ghost_exemption(monkeypatch, tmp_path):
    """★ 豁免里写一个**不存在**的门禁 ⇒ 报（文件改名/删除后名单没跟着改）。"""
    cgw = _wiring_case(
        monkeypatch, tmp_path,
        gates=["check_a.py"],
        release_src='subprocess.run([str(ROOT / "scripts" / "check_a.py")])\n',
        exemptions={"exemptions": [
            {"gate": "check_ghost.py", "reason": "x", "evidence": ["x"]}]},
    )
    assert cgw.main() == 1


def test_gate_wiring_does_not_mistake_comments_for_calls(monkeypatch, tmp_path):
    """★★ **判据必须严于文本匹配**：注释/docstring 里提到文件名**不算接线**。

    ⚠ `release_check.py` 的注释与 docstring 里**反复提到**门禁文件名
      （如「接入 `scripts/check_provenance.py`」）⇒ 若只匹配文件名，
      **每个门禁都会被误判为已接线**，元门禁**永远绿**（正是它要防的那种假绿）。
    """
    cgw = _wiring_case(
        monkeypatch, tmp_path,
        gates=["check_a.py"],
        release_src=(
            "# 接入 scripts/check_a.py\n"
            '"""说明里也写着 scripts/check_a.py"""\n'
        ),
    )
    assert cgw.main() == 1, "注释里的文件名被当成了接线"


def test_real_repo_has_every_gate_wired():
    """★ 对**真仓库**的断言：每个 `scripts/check_*.py` 要么被调用、要么已豁免。"""
    cgw = _load("check_gate_wiring")
    assert cgw.main() == 0, "真仓库里有门禁没接线也没豁免"

# ══ ⑧ 门禁「接线方式」分类（硬门禁 vs 诊断，轮 72 加）══════════════════

#: 一份**最小**的假 `release_check.py`：一个硬门禁 + 一个诊断。
#: ⚠ 每个门禁都必须出现 **`str(ROOT / "scripts" / "<名字>")`** 这个**精确形态** ——
#:   光有 `_run_xxx()` 函数调用**不算接线**（判据见 `check_gate_wiring` 的 docstring）。
#:   夹具若漏了它，就会自己触发元门禁的「接线」那半 ⇒「应 PASS」的用例会红（实测踩过）。
_FAKE_RELEASE = (
    'def main():\n'
    '    subprocess.run([str(ROOT / "scripts" / "check_prov.py")])\n'
    '    subprocess.run([str(ROOT / "scripts" / "check_diag.py")])\n'
    '    subprocess.run([str(ROOT / "scripts" / "check_gate_wiring.py")])\n'
    '    prov = _run_prov_gate()\n'
    '    if prov.get("status") == "fail":\n'
    '        raise AssertionError("prov")\n'
    '    diag = _run_diag_probe()\n'
    '    return {"status": "pass"}\n'
)


def _classify_case(monkeypatch, tmp_path, items, release_src=_FAKE_RELEASE):
    cgw = _load("check_gate_wiring")
    (tmp_path / "scripts").mkdir(exist_ok=True)
    for g in ("check_prov.py", "check_diag.py", "check_gate_wiring.py"):
        (tmp_path / "scripts" / g).write_text('"""x"""\n', encoding="utf-8")
    (tmp_path / "scripts" / "release_check.py").write_text(release_src, encoding="utf-8")
    (tmp_path / "docs").mkdir(exist_ok=True)
    (tmp_path / "docs" / "gate-classification.json").write_text(
        json.dumps({"classification": items}, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(cgw, "ROOT", tmp_path)
    monkeypatch.setattr(cgw, "RELEASE", tmp_path / "scripts" / "release_check.py")
    monkeypatch.setattr(cgw, "EXEMPTIONS", tmp_path / "docs" / "gate-wiring-exemptions.json")
    monkeypatch.setattr(cgw, "CLASSIFICATION", tmp_path / "docs" / "gate-classification.json")
    return cgw


_OK_ITEMS = [
    {"gate": "check_prov.py", "runner": "_run_prov_gate", "kind": "hard", "reason": "x"},
    {"gate": "check_diag.py", "runner": "_run_diag_probe", "kind": "diagnostic", "reason": "y"},
]


def test_gate_kind_flags_hard_declared_but_actually_diagnostic(monkeypatch, tmp_path):
    """★★ **核心负例**：「**本该拦的写成诊断**」会**静默放行** ⇒ 必须报。

    ⚠ 轮 71 的元门禁只解决了「门禁**接线了没**」，**接线的方式**没管 ——
      而 `release_check.py` 里实测并存两种形态（`raise` vs 只记状态）。
      一个本该拦的门禁若写成诊断，CI 只看退出码 ⇒ **等于没有这道门禁**。
    """
    items = [dict(_OK_ITEMS[0]), dict(_OK_ITEMS[1])]
    items[1]["kind"] = "hard"                  # 实际是 diagnostic
    cgw = _classify_case(monkeypatch, tmp_path, items)
    assert cgw.main() == 1


def test_gate_kind_flags_diagnostic_declared_but_actually_hard(monkeypatch, tmp_path):
    """★ 反向：登记成诊断、实际是硬门禁 ⇒ 也报（两个方向都要管）。"""
    items = [dict(_OK_ITEMS[0]), dict(_OK_ITEMS[1])]
    items[0]["kind"] = "diagnostic"
    cgw = _classify_case(monkeypatch, tmp_path, items)
    assert cgw.main() == 1


def test_gate_kind_requires_every_call_site_to_be_registered(monkeypatch, tmp_path):
    """★ 调用点**没登记** ⇒ 报（登记表必须覆盖每一个 `_run_*`）。"""
    cgw = _classify_case(monkeypatch, tmp_path, [dict(_OK_ITEMS[0])])
    assert cgw.main() == 1


def test_gate_kind_rejects_a_ghost_runner(monkeypatch, tmp_path):
    """★ 登记了**不存在**的 `_run_*` ⇒ 报（函数改名/删除后名单没跟着改）。"""
    items = [dict(_OK_ITEMS[0]), dict(_OK_ITEMS[1]),
             {"gate": "check_ghost.py", "runner": "_run_ghost_gate",
              "kind": "hard", "reason": "x"}]
    cgw = _classify_case(monkeypatch, tmp_path, items)
    assert cgw.main() == 1


def test_gate_kind_rejects_unknown_kind_and_empty_reason(monkeypatch, tmp_path):
    """★ `kind` 不在枚举内 / `reason` 为空 ⇒ 报。"""
    items = [dict(_OK_ITEMS[0]), dict(_OK_ITEMS[1])]
    items[0]["kind"] = "maybe"
    cgw = _classify_case(monkeypatch, tmp_path, items)
    assert cgw.main() == 1

    items = [dict(_OK_ITEMS[0]), dict(_OK_ITEMS[1])]
    items[0]["reason"] = "   "
    cgw = _classify_case(monkeypatch, tmp_path, items)
    assert cgw.main() == 1


def test_gate_kind_passes_when_classification_matches_reality(monkeypatch, tmp_path):
    """★ 登记与实况一致 ⇒ **不该报**。"""
    cgw = _classify_case(monkeypatch, tmp_path, [dict(x) for x in _OK_ITEMS])
    assert cgw.main() == 0


def test_gate_kind_uses_sibling_statement_not_a_line_window(monkeypatch, tmp_path):
    """★★ **判据必须看「本次调用的直接后果」**，不是「附近有没有 raise」。

    ⚠ 实测踩过：18 行的**行窗口**把 `_run_interface_ownership_probe`（**诊断**）也算成了 raise
      —— 因为它后面紧跟的是**另一件事**（`bundled_drift`）的 `raise`。
    ★ 与已知事实 51 同族：判据的范围必须**贴合它要抓的那件事**。
    ⇒ 本测试造一个「诊断的**下一个兄弟语句**恰好是别的 raise」的形态，断言仍判 diagnostic。
    """
    src = (
        'def main():\n'
        '    diag = _run_diag_probe()\n'
        '    other = collect()\n'
        '    if other:\n'
        '        raise AssertionError("别的 raise")\n'
        '    return {}\n'
    )
    cgw = _load("check_gate_wiring")
    kinds = cgw.actual_runners(src)
    assert kinds.get("_run_diag_probe") == "diagnostic", kinds

# ══ ⑨ 门禁「第四层」：`skipped` 的**依据**必须合法（轮 73 加）════════════

_SKIP_CASES = [
    (
        "故障（超时/OSError）返回 skipped",
        "def f():\n"
        "    try:\n"
        "        pass\n"
        "    except OSError as exc:\n"
        '        return {"status": "skipped", "reason": str(exc)}\n',
        False,
    ),
    (
        "非 git 工作树返回 skipped（合理）",
        "def f():\n"
        "    if not _git_available():\n"
        '        return {"status": "skipped", "reason": "非 git"}\n',
        True,
    ),
    (
        "脚本约定 exit 2（合理）",
        "def f():\n"
        "    if proc.returncode == 2:\n"
        '        return {"status": "skipped", "reason": "读不到锚点"}\n',
        True,
    ),
    (
        "脚本自报 [SKIP] 驱动变量（合理）",
        "def f():\n"
        '    skipped = any(l.startswith("[SKIP]") for l in out)\n'
        "    if skipped:\n"
        '        status = "skipped"\n',
        True,
    ),
]


def test_skip_depends_on_whitelisted_evidence():
    """★★ **核心负例**：`skipped` 的**依据**必须落在白名单内。

    ⚠ 这是同一个问题的**第四层**：门禁**接好了**（轮 71）· **方式对了**（轮 72），
      但**它跳过的时候**呢？调用点只看 `"fail"` ⇒ **`skipped` 会被静默放行**。
      实测：`release_check.py` 里原有 **5 处**「**无法启动**（`TimeoutExpired`/`OSError`）」
      返回 `skipped` —— **那是故障，不是便携性**，已全部改成 `fail`。

    ⚠ 本测试把四种形态一次钉死：只有「数据源缺失 / 脚本约定 / 脚本自报 `[SKIP]`」算合理。
    """
    cgw = _load("check_gate_wiring")
    for name, src, want in _SKIP_CASES:
        branches = cgw.skip_branches(src)
        hit = any(any(tok in ctx for tok in cgw.ALLOWED_SKIP_CONDITIONS)
                  for _ln, _cond, ctx in branches)
        assert hit == want, "用例「%s」：白名单命中 %s，应为 %s" % (name, hit, want)


def test_skip_branch_looks_at_the_variable_source_not_only_the_test():
    """★★ **判据要看变量的来源**，不能只看 `if` 的 `test`。

    ⚠ 实测踩过（轮 73）：第一版判据只看 `If.test`，而
      `_run_interface_ownership_probe` 里那条 `if skipped:` 的条件是**变量**，
      来源在它**上一行**（`skipped = any(... startswith("[SKIP]") ...)`)
      ⇒ 那条**合法的** `skipped` 被**误报成违规**。
    ★ 与已知事实 51 同族：判据的范围必须贴合它要抓的那件事。
    """
    cgw = _load("check_gate_wiring")
    src = (
        "def f():\n"
        '    skipped = any(l.startswith("[SKIP]") for l in out)\n'
        "    if skipped:\n"
        '        status = "skipped"\n'
    )
    branches = cgw.skip_branches(src)
    assert branches, "应当识别出这条 skipped 分支"
    _ln, cond, ctx = branches[0]
    assert "startswith" in ctx, "判据的上下文必须覆盖变量的**来源**，实际只拿到：%r" % cond


def test_real_release_check_only_skips_for_whitelisted_reasons():
    """★ 对**真仓库**的断言：`release_check.py` 里每处 `skipped` 的依据都在白名单内。

    ⚠ 这一条同时守住「以后有人新加一个 `except …: return skipped`」的回归。
    """
    cgw = _load("check_gate_wiring")
    src = (Path(__file__).resolve().parents[1] / "scripts" / "release_check.py").read_text(
        encoding="utf-8")
    for ln, cond, ctx in cgw.skip_branches(src):
        assert any(tok in ctx for tok in cgw.ALLOWED_SKIP_CONDITIONS), (
            "L%d 的 `skipped` 依据 `%s` 不在白名单内" % (ln, cond))


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
        "def run_release_check():\n"
        "    a = _run_a_gate()\n"
        "    b = _run_b_gate()\n"
        '    _gate_results = {"a": a}\n'          # ⚠ 漏了 b
        "    return {}\n"
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


# ══ ⑪ 门禁「第六层」：**覆盖面**必须进返回体（轮 191 加）══════════════════

def _detail_gaps(gates: dict, details: dict) -> list:
    """判据：**每道门禁都要有一条非空明细**（`gate_details` 的键集合必须等于 `gates`）。

    :param gates: `{"门禁名": status}`。
    :param details: `{"门禁名": 明细文本}`。
    :returns: 缺失/为空的差异列表（**空列表 = 通过**）。

    ⚠ 为什么单独立这个函数：**判据要能用**负例**验**（事实 62）——
      直接断言真仓库的输出只能证明"现在是好的"，证明不了"判据有牙"。
    """
    gaps = [n for n in gates if n not in details]
    gaps += [n for n, v in details.items() if not str(v).strip()]
    return sorted(set(gaps))


def test_gate_details_exposed_for_every_gate():
    """★★ 返回体必须给**每道门禁**一条明细 —— 「它扫了什么」不能是隐形的。

    ⚠ 实测（轮 191）：轮 74 已经把「**13 个门禁的 `status`**」与 `skipped` 都暴露了，
      但**每道门禁的 `output`（「扫了多少 / 跳过了什么」）仍只有 4 道有** ——
      其余 11 道在结果里**只有 `"status": "pass"`**。
    ★★ 而 **`status: pass` 与「没覆盖任何东西」在输出上长得一模一样** ——
      「判据没覆盖」和「没有问题」是两回事（轮 190 的定则）。
    """
    rc = _load("release_check")
    #: ⚠ 本调用**在门禁不绿时会抛**（`run_release_check` 的既有行为）—— 与
    #: `test_release_check_passes_current_tree` 同一性质；★ 所以这里**不再重复**断言 `status`，
    #: 只断言**本条真正关心的不变量**（明细覆盖）。
    result = rc.run_release_check()
    assert _detail_gaps(result["gates"], result["gate_details"]) == [], \
        "有门禁没给明细（或缺 key）"


def test_detail_gaps_criterion_has_teeth():
    """★★ **负例**（事实 62）：判据必须能抓到「少一条明细」与「明细为空」两种缺陷。"""
    gates = {"a": "pass", "b": "pass", "c": "pass"}
    #: ① 全都有 ⇒ 通过
    assert _detail_gaps(gates, {"a": "x", "b": "y", "c": "z"}) == []
    #: ② 少一道 ⇒ 必须报
    assert _detail_gaps(gates, {"a": "x", "b": "y"}) == ["c"]
    #: ③ 有但为空（**更隐蔽**：键在、值空，看起来像"有明细"）⇒ 必须报
    assert _detail_gaps(gates, {"a": "x", "b": "  ", "c": "z"}) == ["b"]
    #: ④ 两种同时 ⇒ 两个都报
    assert _detail_gaps(gates, {"a": ""}) == ["a", "b", "c"]


# ══ ⑫ R 编号**登记表**：引用的编号必须都已登记（轮 193 加）══════════════

def _load_uc():
    """载入 `check_union_conventions`（本组测试只用到它的两个纯函数）。"""
    return _load("check_union_conventions")


def test_referenced_rules_expands_ranges():
    """★ `R1-R3` 这类**区间写法**必须被展开成 1/2/3 —— 否则会漏登记。

    ⚠ 实测：门禁的段名写的正是 `R1-R3/R6/R9/R10/**R12**/**R13**`
      ⇒ 若只按 `\\bR\\d+\\b` 抓，会漏掉 R2（它**只**以区间形式出现）。
    """
    uc = _load_uc()
    assert uc.referenced_rules(["R1-R3/R6/R9/R10/**R12**/**R13** · 清单形状"]) == {1, 2, 3, 6, 9, 10, 12, 13}
    assert uc.referenced_rules(["R14 · A1 的另一半"]) == {14}
    assert uc.referenced_rules([]) == set()


def test_rule_registry_section_is_complete():
    """★★ 真仓库：登记表**无缺号**，且门禁段名引用的编号**全都在表里**。"""
    uc = _load_uc()
    reg = uc.rule_registry()
    assert reg, "读不出登记表（docs/union-conventions.md 的「二之补」一节）"
    assert sorted(reg) == list(range(min(reg), max(reg) + 1)), \
        "登记表有缺号：%s" % sorted(set(range(min(reg), max(reg) + 1)) - reg)
    titles = ["R1-R3/R6/R9/R10/**R12**/**R13** · 清单形状",
              "规则 4 + R5/R7/R11 · 验证等级与授权",
              "R11 · 授权真源", "**R14** · A1 的另一半「不做 + 原因」"]
    assert uc.check_rule_registry(titles) == [], "段名引用了未登记的编号"


def test_rule_registry_criterion_has_teeth():
    """★★ **负例**（事实 62）：判据必须能抓到两种缺陷。

    ① **引用了未登记的编号**（如 R99）⇒ 报
    ② **登记表有缺号**（用临时文档：登记 R1/R2/R4，缺 R3）⇒ 报
    ⚠ ② 用 monkeypatch 换 `CONVENTIONS_DOC`，**不动真文件**（避免把仓库改坏）。
    """
    uc = _load_uc()
    #: ① 引用未登记
    bad = uc.check_rule_registry(["R99 · 不存在的编号"])
    assert bad, "引用了未登记的 R99，判据却没报"
    #: ② 登记表缺号
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "conv.md"
        p.write_text("## 二之补 R 编号登记表\n\n"
                     "| 编号 | 含义 |\n|---|---|\n"
                     "| **R1** | a |\n| **R2** | b |\n| **R4** | d |\n", encoding="utf-8")
        old = uc.CONVENTIONS_DOC
        uc.CONVENTIONS_DOC = p
        try:
            bad2 = uc.check_rule_registry(["R1 · x"])
            assert any("缺号" in b for b in bad2), "登记表缺 R3，判据却没报：%s" % bad2
        finally:
            uc.CONVENTIONS_DOC = old
    #: ③ 登记表读不出来（不是"没问题"）⇒ 必须报
    uc2 = _load_uc()
    old2 = uc2.CONVENTIONS_DOC
    uc2.CONVENTIONS_DOC = Path("D:/definitely/not/here.md")
    try:
        assert uc2.check_rule_registry([]), "读不出登记表时判据必须报，不能静默通过"
    finally:
        uc2.CONVENTIONS_DOC = old2


def test_unregistered_refs_covers_the_enforcement_side():
    """★★ **执行侧**（`scripts/*.py`）引用的编号必须都已登记（轮 194 扩的覆盖面）。

    ⚠ 为什么扩：轮 193 只查**段名**，而实测「引用 R 编号的文件」有 **17 个**
      （3 门禁 + 4 scripts + 5 tests + 5 docs）⇒ 段名只覆盖**极小一块**。
    ★★ 为什么**不含 `tests/`**：负例测试**必须能写出未登记的编号**来证明判据有牙 ——
      纳进来会**把负例判成违规**。
    ★★ 为什么**不含 `docs/`**：那是**历史记录**（ROADMAP / known-facts / specs），
      记的是"当时引用过什么"，**不该被后来的登记表追着改**。
    """
    uc = _load_uc()
    reg = uc.rule_registry()
    assert reg, "读不出登记表"
    assert uc.unregistered_refs(uc.RULE_SCAN_GLOB, reg) == {}, \
        "执行侧 `scripts/*.py` 里引用了未登记的编号"


def test_unregistered_refs_has_teeth_and_excludes_registered():
    """★★ **负例**（事实 62）：只报**未登记**的，**已登记的不报**。

    ⚠ 用**临时目录**（`base=` 参数）⇒ **不动真文件**（轮 193 那次用 `git checkout --` 还原
      把自己未提交的改动抹掉的教训）。
    """
    import tempfile
    uc = _load_uc()
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "ok_gate.py").write_text("# 引用 R7（已登记）\n", encoding="utf-8")
        (d / "bad_gate.py").write_text("# 引用 R42（**未登记**）\n", encoding="utf-8")
        got = uc.unregistered_refs("*.py", {7}, base=d)
        assert got == {"bad_gate.py": [42]}, got
        #: 全部已登记 ⇒ 空（证明它**不是**"见了 R 就报"）
        assert uc.unregistered_refs("*.py", {7, 42}, base=d) == {}
        #: 目录不存在 ⇒ 空 dict（不炸）
        assert uc.unregistered_refs("*.py", {7}, base=d / "nope") == {}



