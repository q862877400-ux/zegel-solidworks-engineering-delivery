r"""★ 判据：sw_pattern 的两张枚举表必须与官方枚举**逐项相等**（spec 223 / US1）。

背景（F1）：`scripts/sw_pattern.py` 的 `SWS_PATTERN_ELEMENT_SELECTION`（7 项）与
`SWS_FEATURES_TO_PATTERN`（8 项）**来源块自称"照录官方页"**，而官方页只有 **3 项 / 2 项**
⇒ 键与值全部对不上，属「**自造抽象冒官方名**」。

本文件锁四件事：
  1. **项数**：两张表的项数 == 官方枚举项数（3 / 2）。
  2. **成员名**：每行行末 `# swXxx` 注释的成员名 ∈ 官方成员集，且其值与官方**相等**。
  3. **来源块自陈项数正确**：三个枚举的官方项数必须在源码里如实写出（可核对）。
  4. **`_SG_RELATIONS` 是官方 45 项的真子集**（非伪造；spec 223 §五 的裁决）。
另附**反射交叉核对**：出厂反射转储（铁律 4 的裁决基准）里这 5 个成员的值须与官方页一致。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_pattern_enum_alignment.py —— 本文件自身
# 定位:   spec 223 US1 的判据；被测对象 scripts/sw_pattern.py 的两张枚举表。
# 官方依据: C:\swapi\enums\swPatternElementSelection_e.md（3 项）
#           C:\swapi\enums\swFeaturesToPatternType_e.md（2 项）
#           C:\swapi\enums\swPatternEndCondition_e.md（2 项）
#           C:\swapi\types\IModelDoc2\SketchAddConstraints.md（Remarks 77 行 / 45 名）
#           出厂反射 D:\AI\SW\_raw\enum_values_sldworks.txt
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚠ 本文件为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ast
import importlib.util
import io
import re
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "sw_pattern.py"
SW_PART_PATH = REPO_ROOT / "scripts" / "sw_part.py"
SWAPI_ENUMS = Path(r"C:\swapi\enums")
SKETCH_ADD_CONSTRAINTS = Path(r"C:\swapi\types\IModelDoc2\SketchAddConstraints.md")
REFLECTION = Path(r"D:\AI\SW\_raw\enum_values_sldworks.txt")

#: ── 官方枚举基线（逐字抄自 S2，见上方"官方依据"）────────────────────────
#: 键 = 官方成员名，值 = 官方值。**不得**由被测模块推导。
OFFICIAL_PATTERN_ELEMENT_SELECTION = {
    "swErrorInPatternElementSelection": 0,
    "swFeatureFaces": 1,
    "swBodiesToPattern": 2,
}
OFFICIAL_FEATURES_TO_PATTERN = {
    "swFeaturesToPatternSelectedFeatures": 0,
    "swFeaturesToPatternCreateSeedCut": 1,
}
OFFICIAL_PATTERN_END_CONDITIONS = {
    "swPatternEndCondition_SpacingAndInstances": 0,
    "swPatternEndCondition_UpToReference": 1,
}

#: ── US4：同类候选（门禁双盲的错值表）的官方基线 ──────────────────────
#: `swRefPlaneReferenceConstraints_e`：★ md 那一页**自身矛盾**（写 `1028 or 0x400`、
#:   `2056 or 0x800`，而 `0x400=1024`、`0x800=2048`）⇒ 取**十六进制列 = 出厂反射**的值。
OFFICIAL_REF_PLANE_CONSTRAINTS = {
    "swRefPlaneReferenceConstraint_Parallel": 1,
    "swRefPlaneReferenceConstraint_Coincident": 4,
    "swRefPlaneReferenceConstraint_Distance": 8,
    "swRefPlaneReferenceConstraint_Angle": 16,
    "swRefPlaneReferenceConstraint_MidPlane": 128,
    "swRefPlaneReferenceConstraint_OptionFlip": 256,
    "swRefPlaneReferenceConstraint_OptionOriginOnCurve": 512,
    "swRefPlaneReferenceConstraint_OptionProjectToNearestLocation": 1024,
    "swRefPlaneReferenceConstraint_OptionProjectAlongSketchNormal": 2048,
    "swRefPlaneReferenceConstraint_OptionReferenceFlip": 8192,
}
#: ★ **订正前的错值** —— 永久负例（它们必须**不通过**上面的判据）
REF_PLANE_OLD_WRONG = {
    "swRefPlaneReferenceConstraint_OptionProjectToNearestLocation": 1028,
    "swRefPlaneReferenceConstraint_OptionProjectAlongSketchNormal": 2056,
}
#: `swHemPositionTypes_e`：**真两源冲突**（md 1/2 · 反射 0/1）⇒ 铁律 4 取反射。
OFFICIAL_HEM_POSITIONS = {
    "swHemPositionTypeInside": 0,
    "swHemPositionTypeOutside": 1,
}

TABLE_SPECS = (
    ("SWS_PATTERN_ELEMENT_SELECTION", "swPatternElementSelection_e",
     OFFICIAL_PATTERN_ELEMENT_SELECTION),
    ("SWS_FEATURES_TO_PATTERN", "swFeaturesToPatternType_e",
     OFFICIAL_FEATURES_TO_PATTERN),
    ("SWS_PATTERN_END_CONDITIONS", "swPatternEndCondition_e",
     OFFICIAL_PATTERN_END_CONDITIONS),
)


# ── 解析工具 ─────────────────────────────────────────────────────────

def _module_source() -> str:
    return MODULE_PATH.read_text(encoding="utf-8")


def _module_ast() -> ast.Module:
    return ast.parse(_module_source())


def _find_assign(tree: ast.Module, name: str) -> ast.Assign:
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == name:
                    return node
    raise AssertionError("模块里找不到顶层赋值 %r" % name)


def _dict_from_assign(node: ast.Assign) -> dict:
    """把 `NAME = {"k": <int>, ...}` 读成 `{key: int}`。"""
    assert isinstance(node.value, ast.Dict), "表不是字典字面量：%r" % ast.dump(node.value)[:80]
    out: dict = {}
    for k, v in zip(node.value.keys, node.value.values):
        assert isinstance(k, ast.Constant) and isinstance(k.value, str), "键非字符串"
        assert isinstance(v, ast.Constant) and isinstance(v.value, int), "值非整数"
        out[k.value] = v.value
    return out


def _line_member_comments(source: str) -> dict:
    """从**源码文本**里取每个 `"key": <int>,  # swMember` 的成员名 ⇒ `{key: member}`。

    ★ 键**大小写不限**（与门禁的 `CODE_ROW` 一致 —— 驼峰键原先匹配不到，那是一处静默边界）。
    """
    out: dict = {}
    row = re.compile(
        r'^\s*"(?P<key>[A-Za-z0-9_]+)"\s*:\s*(?P<value>-?\d+)\s*,\s*#\s*'
        r'(?P<member>sw\w+)\b')
    for line in source.splitlines():
        m = row.match(line)
        if m:
            out[m.group("key")] = m.group("member")
    return out


def _official_from_swapi(enum_name: str) -> dict:
    """从 `C:\\swapi\\enums\\<enum>.md` 的表格取 `{成员名: 值}`（拿不到回空）。"""
    p = SWAPI_ENUMS / ("%s.md" % enum_name)
    if not p.is_file():
        return {}
    out: dict = {}
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\|\s*(sw\w+)\s*\|\s*(-?\d+)\s*\|", line)
        if m:
            out[m.group(1)] = int(m.group(2))
    return out


def _reflection_values(names) -> dict:
    """从出厂反射转储取 `{成员名: 值}`（只取要的那几个；拿不到回空）。"""
    if not REFLECTION.is_file():
        return {}
    want = set(names)
    out: dict = {}
    row = re.compile(r"^\s{2,}(?P<member>sw\w+)\s*=\s*(?P<value>-?\d+)\s*$")
    for line in REFLECTION.read_text(encoding="utf-8", errors="replace").splitlines():
        m = row.match(line)
        if m and m.group("member") in want:
            out.setdefault(m.group("member"), int(m.group("value")))
    return out


def _official_sg_names() -> set:
    """从官方 `SketchAddConstraints.md` 的 Remarks 取全部不重复 `sg*` 名。"""
    if not SKETCH_ADD_CONSTRAINTS.is_file():
        return set()
    text = SKETCH_ADD_CONSTRAINTS.read_text(encoding="utf-8", errors="replace")
    return set(re.findall(r"\bsg[A-Za-z0-9_]+", text))


def _load_module():
    """加载 sw_pattern（桩掉 sw_connect + sw_preflight，避免缺 COM 依赖时交互式提问）。"""
    connect = types.ModuleType("sw_connect")
    connect.__getattr__ = lambda name: (lambda *a, **k: None)
    connect.get_com_member = lambda *a, **k: None
    connect.set_com_member = lambda *a, **k: None
    connect.call_com_member = lambda *a, **k: None
    connect.mm = lambda v: v
    sys.modules.setdefault("sw_connect", connect)

    preflight = types.ModuleType("sw_preflight")
    preflight.__getattr__ = lambda name: (lambda *a, **k: None)
    #: ★ 环境坑：缺 COM 依赖时它会**交互式**问「是否授权自动安装 [Y/N]」⇒ 必须返回三元组
    preflight.import_com_dependencies = lambda *a, **k: (None, None, None)
    sys.modules.setdefault("sw_preflight", preflight)

    spec = importlib.util.spec_from_file_location("sw_pattern", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["sw_pattern"] = module
    spec.loader.exec_module(module)
    return module


# ── US1 判据 ─────────────────────────────────────────────────────────

def test_pattern_element_selection_matches_official():
    """官方 swPatternElementSelection_e 只有 3 项；表必须逐项相等。"""
    src = _module_source()
    table = _dict_from_assign(_find_assign(_module_ast(), "SWS_PATTERN_ELEMENT_SELECTION"))
    assert len(table) == len(OFFICIAL_PATTERN_ELEMENT_SELECTION), (
        "SWS_PATTERN_ELEMENT_SELECTION 项数 %d ≠ 官方 %d（官方 %s）"
        % (len(table), len(OFFICIAL_PATTERN_ELEMENT_SELECTION),
           sorted(OFFICIAL_PATTERN_ELEMENT_SELECTION)))
    comments = _line_member_comments(src)
    for key, value in table.items():
        member = comments.get(key)
        assert member, "第 %r 行缺 `# swXxx` 官方成员名注释" % key
        assert member in OFFICIAL_PATTERN_ELEMENT_SELECTION, (
            "键 %r 标注的 %r 不在官方枚举里" % (key, member))
        assert value == OFFICIAL_PATTERN_ELEMENT_SELECTION[member], (
            "%r = %d，而官方 %s = %d"
            % (key, value, member, OFFICIAL_PATTERN_ELEMENT_SELECTION[member]))


def test_features_to_pattern_matches_official():
    """官方 swFeaturesToPatternType_e 只有 2 项；表必须逐项相等。"""
    src = _module_source()
    table = _dict_from_assign(_find_assign(_module_ast(), "SWS_FEATURES_TO_PATTERN"))
    assert len(table) == len(OFFICIAL_FEATURES_TO_PATTERN), (
        "SWS_FEATURES_TO_PATTERN 项数 %d ≠ 官方 %d（官方 %s）"
        % (len(table), len(OFFICIAL_FEATURES_TO_PATTERN),
           sorted(OFFICIAL_FEATURES_TO_PATTERN)))
    comments = _line_member_comments(src)
    for key, value in table.items():
        member = comments.get(key)
        assert member, "第 %r 行缺 `# swXxx` 官方成员名注释" % key
        assert member in OFFICIAL_FEATURES_TO_PATTERN, (
            "键 %r 标注的 %r 不在官方枚举里" % (key, member))
        assert value == OFFICIAL_FEATURES_TO_PATTERN[member], (
            "%r = %d，而官方 %s = %d"
            % (key, value, member, OFFICIAL_FEATURES_TO_PATTERN[member]))


def test_end_condition_table_unchanged():
    """既有正确的表不得被本轮改动带坏。"""
    src = _module_source()
    table = _dict_from_assign(_find_assign(_module_ast(), "SWS_PATTERN_END_CONDITIONS"))
    assert len(table) == 2
    comments = _line_member_comments(src)
    for key, value in table.items():
        member = comments.get(key)
        assert member in OFFICIAL_PATTERN_END_CONDITIONS
        assert value == OFFICIAL_PATTERN_END_CONDITIONS[member]


def test_source_block_states_official_page():
    r"""来源块必须**引用官方页路径**，且**如实写出官方项数**（FR-003）。

    ★ 判据写成「**同一行**同时出现官方枚举名与「官方…N 项」」——
      否则相邻枚举的计数会被误读成这一条（本轮实测踩过：元素表的窗口里
      读到了上一张表的「官方只有 2 项」）。
    """
    src = _module_source()
    for table_name, enum_name, official in TABLE_SPECS:
        assert enum_name + ".md" in src, (
            "%s 的来源块没引用官方页 %s.md" % (table_name, enum_name))
        same_line = re.compile(
            re.escape(enum_name) + r"\b[^\n]*?官方[^\n]*?(\d+)\s*项")
        found = [int(m.group(1)) for m in
                 (same_line.search(line) for line in src.splitlines()) if m]
        assert found, (
            "%s 的来源块没有**同一行**写出「%s … 官方 N 项」" % (table_name, enum_name))
        assert len(set(found)) == 1, (
            "%s 的来源块对 %s 给出了矛盾的项数：%s" % (table_name, enum_name, found))
        assert found[0] == len(official), (
            "%s 的来源块写「官方 %d 项」，而官方实为 %d 项"
            % (table_name, found[0], len(official)))


def test_tables_are_exported():
    """`__all__` 必须仍导出两张表（公开面不缩）。"""
    module = _load_module()
    for name in ("SWS_PATTERN_ELEMENT_SELECTION", "SWS_FEATURES_TO_PATTERN",
                 "SWS_PATTERN_END_CONDITIONS"):
        assert name in module.__all__, "%s 不在 __all__ 里" % name


# ── 反射交叉核对（铁律 4）────────────────────────────────────────────

def test_official_pages_agree_with_reflection_dump():
    """官方页与出厂反射转储必须一致（不一致要显式暴露，不静默）。"""
    names = list(OFFICIAL_PATTERN_ELEMENT_SELECTION) + list(OFFICIAL_FEATURES_TO_PATTERN)
    ref = _reflection_values(names)
    if not ref:
        return  # 便携性：转储不在则跳过
    for member, value in {**OFFICIAL_PATTERN_ELEMENT_SELECTION,
                          **OFFICIAL_FEATURES_TO_PATTERN}.items():
        assert member in ref, "反射转储里没有 %s" % member
        assert ref[member] == value, (
            "两源冲突：%s 官方页 %d · 反射 %d" % (member, value, ref[member]))


def test_official_baseline_matches_swapi_files():
    """本文件抄的官方基线必须与 C:\\swapi 的页一致（防止抄错）。"""
    for enum_name, official in (
        ("swPatternElementSelection_e", OFFICIAL_PATTERN_ELEMENT_SELECTION),
        ("swFeaturesToPatternType_e", OFFICIAL_FEATURES_TO_PATTERN),
        ("swPatternEndCondition_e", OFFICIAL_PATTERN_END_CONDITIONS),
    ):
        parsed = _official_from_swapi(enum_name)
        if not parsed:
            continue  # 便携性：swapi 不在则跳过
        assert parsed == official, (
            "%s 官方页 %r ≠ 本文件基线 %r" % (enum_name, parsed, official))


# ── _SG_RELATIONS 裁决（45/77 口径）──────────────────────────────────

def test_sg_relations_is_subset_of_official():
    """`sw_part._SG_RELATIONS` 必须是官方 `SketchAddConstraints` 清单的**真子集**（非伪造）。"""
    official = _official_sg_names()
    if not official:
        return  # 便携性
    node = _find_assign(ast.parse(SW_PART_PATH.read_text(encoding="utf-8")), "_SG_RELATIONS")
    call = node.value
    assert isinstance(call, ast.Call), "_SG_RELATIONS 不是 frozenset((...)) 形式"
    names = {e.value for e in call.args[0].elts}  # type: ignore[attr-defined]
    assert names, "没解析出 _SG_RELATIONS 的成员"
    illegal = sorted(names - official)
    assert not illegal, (
        "白名单里有官方清单里不存在的名字：%s（官方共 %d 名）" % (illegal, len(official)))
    assert len(names) < len(official), (
        "_SG_RELATIONS 应是**真子集**；现在 %d vs 官方 %d" % (len(names), len(official)))


# ── US4：同类候选（门禁双盲的错值表）────────────────────────────────

def _table_in(path: Path, name: str):
    src = path.read_text(encoding="utf-8")
    return _dict_from_assign(_find_assign(ast.parse(src), name)), _line_member_comments(src)


def test_ref_plane_constraints_values_match_reflection():
    """`sw_ref_geometry.REF_PLANE_CONSTRAINTS` 必须与**出厂反射**一致（铁律 4）。"""
    table, comments = _table_in(REPO_ROOT / "scripts" / "sw_ref_geometry.py",
                                "REF_PLANE_CONSTRAINTS")
    ref = _reflection_values(OFFICIAL_REF_PLANE_CONSTRAINTS)
    assert table, "REF_PLANE_CONSTRAINTS 没解析出来"
    for key, value in table.items():
        member = comments.get(key)
        assert member, "REF_PLANE_CONSTRAINTS 的 %r 行缺 `# swXxx` 注释" % key
        assert member in OFFICIAL_REF_PLANE_CONSTRAINTS, "%r 不在本文件基线里" % member
        assert value == OFFICIAL_REF_PLANE_CONSTRAINTS[member], (
            "%s = %d，基线 %d" % (member, value, OFFICIAL_REF_PLANE_CONSTRAINTS[member]))
        if ref:
            assert ref.get(member) == value, (
                "%s 与出厂反射不符：代码 %d · 反射 %s" % (member, value, ref.get(member)))


def test_ref_plane_negative_case_old_values_fail():
    """★ 永久负例：订正前的 **1028 / 2056** 必须**不通过** ⇒ 证明判据有牙。"""
    ref = _reflection_values(REF_PLANE_OLD_WRONG)
    if not ref:
        return
    for member, old in REF_PLANE_OLD_WRONG.items():
        assert member in ref, "反射里应有 %s" % member
        assert old != ref[member], "负例失效：%s 的旧值 %d 竟等于反射值" % (member, old)
        assert old != OFFICIAL_REF_PLANE_CONSTRAINTS[member]


def test_hem_positions_matches_reflection():
    """`sw_sheet_metal.HEM_POSITIONS` 必须与**出厂反射**一致（铁律 4 裁决两源冲突）。"""
    table, comments = _table_in(REPO_ROOT / "scripts" / "sw_sheet_metal.py", "HEM_POSITIONS")
    ref = _reflection_values(OFFICIAL_HEM_POSITIONS)
    for key, value in table.items():
        member = comments.get(key)
        assert member, "HEM_POSITIONS 的 %r 行缺 `# swXxx` 注释" % key
        assert member in OFFICIAL_HEM_POSITIONS, "%r 不在本文件基线里" % member
        assert value == OFFICIAL_HEM_POSITIONS[member], (
            "%s = %d，基线 %d" % (member, value, OFFICIAL_HEM_POSITIONS[member]))
        if ref:
            assert ref.get(member) == value, (
                "%s 与出厂反射不符：代码 %d · 反射 %s" % (member, value, ref.get(member)))


def test_hem_positions_negative_case_md_values_fail():
    """★ 永久负例：官方 **md** 写的 1/2 必须**不通过**（那是两源冲突的另一侧）。"""
    ref = _reflection_values(OFFICIAL_HEM_POSITIONS)
    if not ref:
        return
    md = _official_from_swapi("swHemPositionTypes_e")
    if not md:
        return  # 便携性
    assert md, "md 应能解析出成员"
    for member, mdval in md.items():
        assert member in ref, "反射里应有 %s" % member
        assert mdval != ref[member], (
            "负例失效：%s 的 md 值 %d 竟等于反射值" % (member, mdval))


# ── 直接运行 ─────────────────────────────────────────────────────────

def _main():
    failures = []
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        try:
            test()
            print(f"  PASS  {test.__name__}")
        except Exception as exc:  # noqa: BLE001
            failures.append((test.__name__, exc))
            print(f"  FAIL  {test.__name__}: {exc}")
    print(f"\n{len(tests) - len(failures)}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    raise SystemExit(_main())
