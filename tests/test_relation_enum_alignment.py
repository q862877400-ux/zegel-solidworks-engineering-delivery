"""Check sketch relation names and values against the official swConstraintType_e."""
# Source: this repository, scripts/sw_sketch_relations.py and scripts/sw_part.py.
# Location: specs/222-relation-enum-and-public-contract judging criteria.
# Official reference: C:/swapi/enums/swConstraintType_e.md,
# C:/swapi/types/IModelDoc2/SketchAddConstraints.md,
# SWhelp/swconst/...swConstraintType_e.html and _raw/enum_values_sldworks.txt.
# License: repository MIT; official pages are reference-only, no text copied.
# Coverage: enum alignment, legacy alias direction, undecided registry, public surface.
from __future__ import annotations

import importlib.util
import io
import contextlib
import re
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 枚举（三源逐项比对一致，86/86）
# 文件:   C:/swapi/enums/swConstraintType_e.md
#         AI Solidworks/官方文档/SWhelp/swconst/...swConstraintType_e.html
#         _raw/enum_values_sldworks.txt（## swConstraintType_e 段）
# 定位:   官方 swConstraintType_e 的数值，本文件全部断言的唯一依据。
# 覆盖:   本切片用到的子集（去 swConstraintType_ 前缀 → 数值）。
# ⚠ 三处源逐项一致，故本切片无需走「出厂类型库推翻文档」分支。
# ────────────────────────────────────────────────────────────────────
OFFICIAL_CONSTRAINT_TYPES = {
    "DISTANCE": 1,
    "ANGLE": 2,
    "RADIUS": 3,
    "HORIZONTAL": 4,
    "VERTICAL": 5,
    "TANGENT": 6,
    "PARALLEL": 7,
    "PERPENDICULAR": 8,
    "COINCIDENT": 9,
    "CONCENTRIC": 10,
    "SYMMETRIC": 11,
    "ATMIDDLE": 12,
    "ATINTERSECT": 13,
    "SAMELENGTH": 14,
    "DIAMETER": 15,
    "FIXED": 17,
    "COLINEAR": 27,
    "CORADIAL": 28,
    "ATPIERCE": 40,
}

#: 官方枚举里**不存在**这些名字（真名见 OFFICIAL_CONSTRAINT_TYPES）。
#: 保留它们的唯一理由是把用户已经写下的旧词纠正到官方名上。
LEGACY_ALIASES = {
    "EQUAL": "SAMELENGTH",
    "MIDPOINT": "ATMIDDLE",
}

#: SketchAddConstraints 官方 Remarks 清单里确有的字符串（去 sg 前缀、小写）。
#: 依据 C:/swapi/types/IModelDoc2/SketchAddConstraints.md 的 Remarks 逐项照录。
OFFICIAL_SG_NAMES = {
    "horizontal", "horizpoints", "vertical", "vertpoints",
    "alongzpoints", "alongz", "colinear", "coradial",
    "perpendicular", "parallel", "tangent", "concentric", "coincident",
    "symmetric", "atmiddle", "atintersect", "atpierce", "fixed",
    "angle", "arcang180", "arcang270", "arcang90", "arcangbottom",
    "arcangleft", "arcangright", "arcangtop", "diameter", "distance",
    "samelengh".replace("samelengh", "samelength"),
    "offsetedge", "snapangle", "snapgrid", "snaplength", "useedge",
    "mergepoints", "horizontals2d", "alongx3d", "alongxpoints3d",
}


#: 表内键名 → 官方成员名（**别名**：键名与官方成员名不同但语义相同）。
#: 这些是「已对齐」，不是「未决」。
TABLE_KEY_TO_OFFICIAL = {
    "equal": "SAMELENGTH",
    "midpoint": "ATMIDDLE",
    "fix": "FIXED",
    "pierce": "ATPIERCE",
    "intersect": "ATINTERSECT",
    #: 表内 `collinear`（两个 L）→ 官方 `COLINEAR`（**一个 L**）
    "collinear": "COLINEAR",
}


#: RELATION_TYPES 应有的**完整**键集。★ 完整性判据 —— 防止「删掉大半也能过」的空判据
#: （2026-10-08 由独立复核指出原判据无此约束）。
EXPECTED_RELATION_KEYS = {
    "COINCIDENT", "PARALLEL", "PERPENDICULAR", "TANGENT", "CONCENTRIC",
    "SYMMETRIC", "HORIZONTAL", "VERTICAL", "FIXED", "SAMELENGTH", "ATMIDDLE",
}

#: sw_part._SG_RELATIONS 应有的完整集合。
EXPECTED_SG_RELATIONS = {
    "sgFIXED", "sgHORIZONTAL", "sgVERTICAL", "sgCOLINEAR", "sgPARALLEL",
    "sgPERPENDICULAR", "sgTANGENT", "sgCONCENTRIC", "sgSAMELENGTH",
    "sgSYMMETRIC", "sgATMIDDLE", "sgCOINCIDENT",
}

#: 必须登记为未决、且**不得**出现在 SKETCH_CONSTRAINT_TYPES 里的名字。
EXPECTED_UNDECIDED = {"block", "snappoint"}


def _load_relations():
    spec = importlib.util.spec_from_file_location(
        "relation_enum_under_test", ROOT / "scripts" / "sw_sketch_relations.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_sw_part():
    """Load scripts/sw_part.py with COM imports stubbed out."""
    if str(ROOT / "scripts") not in sys.path:
        sys.path.insert(0, str(ROOT / "scripts"))
    stub = types.ModuleType("sw_connect")

    def _faithful_com(obj, name, *args, **kwargs):
        """复刻真 `get_com_member` 的语义 —— ★ **不许比真函数宽容**。

        ⚠⚠ 这里曾经写成「先 `attr(*args)`，TypeError 就退回 `attr()`」——
           那个兜底**比真函数宽容**，会把「**实参传错**」悄悄吞掉。
           本文件因此放过了一个真 bug：`get_com_member(sk, "A", "B")` 的 `"B"`
           被当成**调用实参**（真函数是 `return member(*args)`），
           导致前置状态门在真机上**恒失败**、工具不可用 —— 而测试全绿。
        ⇒ ★ 现在与真函数一致：**有实参就按实参调，失败就让它失败**。
        """
        if obj is None:
            return None
        attr = getattr(obj, name, None)
        if attr is None:
            return None
        if args:
            return attr(*args, **kwargs)
        if callable(attr):
            try:
                return attr()
            except TypeError:
                #: 与真函数一致：有必填参数 ⇒ 返回成员本身（不静默补零参调用）
                return attr
        return attr

    stub.get_com_member = _faithful_com
    stub.call_com_member = _faithful_com
    stub.set_com_member = lambda obj, name, value: None
    stub.save_document = lambda *a, **k: None
    stub.out_i4 = lambda value=0: ("<out>", int(value))
    stub.create_empty_dispatch_variant = lambda: "<empty>"
    stub.safe_get_com_member = _faithful_com
    #: ★ 必须一并桩掉 sw_preflight —— 缺 COM 依赖时它会**交互式**问
    #:   「是否授权自动安装 [Y/N]」，在无人值守下把测试进程挂死（等同 SIGTERM）。
    #:   本文件只做静态契约断言，不需要任何依赖探测。
    #: ★ 必须一并桩掉 sw_preflight —— 缺 COM 依赖时它会**交互式**问
    #:   「是否授权自动安装 [Y/N]」，在无人值守下把测试进程挂死（等同 SIGTERM）。
    #:   ★ 用**宽松桩**：sw_part 会向它问若干成员，逐个列举很脆。
    class _Permissive(types.ModuleType):
        def __getattr__(self, n):
            if n.startswith("__"):
                raise AttributeError(n)
            return lambda *a, **k: None

    preflight = _Permissive("sw_preflight")
    preflight.import_com_dependencies = lambda *a, **k: (None, None, None)
    preflight.missing_com_dependencies = lambda *a, **k: []
    preflight.ensure_com_dependencies = lambda *a, **k: []
    with patch.dict(sys.modules, {"sw_connect": stub, "sw_preflight": preflight,
                                  "pythoncom": types.ModuleType("pythoncom"),
                                  "win32com": types.ModuleType("win32com"),
                                  "win32com.client": types.ModuleType("win32com.client")}):
        spec = importlib.util.spec_from_file_location(
            "sw_part_enum_under_test", ROOT / "scripts" / "sw_part.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


def _official_types() -> dict:
    """★★ **现读官方枚举页** `swConstraintType_e`（★ 唯一真源 —— 铁律 4）。

    ★★ 判据：**不手抄** —— ★ 手抄的副本会**随时间漂移**，
      ★ 而且「抄漏了几个」看起来像「表里多了几个」。
    ★ 读不到 ⇒ 回 `{}` ⇒ ★ 调用方**跳过**（★ 铁律 5：查不到就说查不到）。
    """
    p = Path("C:/swapi/enums/swConstraintType_e.md")
    if not p.is_file():
        return {}
    rows = re.findall(r"\|\s*swConstraintType_(\w+)\s*\|\s*(\d+)",
                      p.read_text(encoding="utf-8", errors="replace"))
    return {n: int(v) for n, v in rows}


def _load_tool_specs_batch16():
    """Load the ToolSpec batch with a minimal tool_registry stub."""
    registry = types.ModuleType("tool_registry")

    class Param:
        def __init__(self, name, ptype, description="", **kw):
            self.name = name
            self.type = ptype
            self.description = description

    class ToolSpec:
        def __init__(self, name, title="", module="", function="",
                     inject=None, doc="", params=None, **kw):
            self.name = name
            self.title = title
            self.module = module
            self.function = function
            self.inject = inject
            self.doc = doc
            self.params = params or []

    registry.Param = Param
    registry.ToolSpec = ToolSpec
    with patch.dict(sys.modules, {"tool_registry": registry}):
        spec = importlib.util.spec_from_file_location(
            "tool_specs_batch16_under_test", ROOT / "mcp-server" / "tool_specs_batch16.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


# ── US1：映射表与官方枚举对齐 ────────────────────────────────────────

class RelationEnumAlignmentTests(unittest.TestCase):
    def test_relation_types_values_match_official_enum(self):
        """RELATION_TYPES 每个键的数值必须等于官方 swConstraintType_e。

        ★★ 2026-10-12 改（★ 业主定「先做 A」）：**官方枚举现读**，不再钉死子集。
          ⚠ 改前：`OFFICIAL_CONSTRAINT_TYPES` 是**手抄的 19 个**子集 ⇒
            ★ 我把表补到官方全表 **86** 个后 ⇒ ★ 三条断言全红 ✗ ——
            ★ 而「测试红了」看起来像「我把表改错了」，
            ★ 其实是**测试自己只认识一部分**。
          ⇒ ★ 判据：**官方枚举页是唯一真源**（★ 铁律 4）。
        """
        m = _load_relations()
        official = _official_types()
        if not official:
            self.skipTest("★ 本机无官方枚举页 ⇒ 按铁律 5 记「查不到」")
        mismatches = {}
        for key, value in m.RELATION_TYPES.items():
            got = official.get(key.upper())
            if got is None:
                mismatches[key] = "不是官方成员名"
            elif value != got:
                mismatches[key] = "表内 %r，官方 %r" % (value, got)
        self.assertEqual(mismatches, {}, "RELATION_TYPES 与官方枚举不符: %r" % mismatches)

    def test_relation_types_has_no_non_official_name(self):
        """表里不得出现官方枚举里不存在的名字（EQUAL / MIDPOINT 属此类）。"""
        m = _load_relations()
        official = _official_types()
        if not official:
            self.skipTest("★ 本机无官方枚举页")
        illegal = sorted(k for k in m.RELATION_TYPES
                         if k.upper() not in official)
        self.assertEqual(illegal, [], "出现了官方枚举里没有的名字: %r" % illegal)

    def test_relation_types_keys_are_complete(self):
        """★★ 键集必须**覆盖官方全表** —— ★ 否则「少几个」也能过。

        ★★ 2026-10-12 改：从「等于钉死的 11 个」改成「**包含官方全表**」——
          ★ 因为钉死的那个数**本身就不完整**（★ 官方 86 个，它只列 11 个）。
        """
        m = _load_relations()
        official = _official_types()
        if not official:
            self.skipTest("★ 本机无官方枚举页")
        missing = sorted(set(official) - {k.upper() for k in m.RELATION_TYPES})
        self.assertEqual(missing, [],
                         "RELATION_TYPES 缺官方成员: %r" % missing)

    def test_legacy_names_resolve_to_exact_official_members(self):
        """EQUAL→SAMELENGTH、MIDPOINT→ATMIDDLE —— 必须是**这一个**对应，不是「某个官方名」。

        ★ 原判据只断言 `结果 ∈ 官方集合`，则 `EQUAL→PARALLEL` 也会通过（空判据）。
        """
        m = _load_relations()
        self.assertEqual(m._norm_type("EQUAL"), "SAMELENGTH")
        self.assertEqual(m._norm_type("MIDPOINT"), "ATMIDDLE")
        #: 带 sg 前缀与大小写变体也必须归一
        self.assertEqual(m._norm_type("sgEQUAL"), "SAMELENGTH")
        self.assertEqual(m._norm_type("sgequal"), "SAMELENGTH")
        self.assertEqual(m._norm_type("sgMidPoint"), "ATMIDDLE")

    def test_noncallable_returns_none_for_junk(self):
        """空串、裸 sg、乱写必须回 None（不得归一成某个默认关系）。"""
        m = _load_relations()
        for junk in ("", "   ", "sg", "SG", "not_a_relation", None, 123):
            self.assertIsNone(m._norm_type(junk), "%r 不该被归一" % (junk,))

    def test_legacy_name_does_not_leak_into_dispatch_table(self):
        """反别名不得让 EQUAL / MIDPOINT 作为键混进映射表。"""
        m = _load_relations()
        for legacy in LEGACY_ALIASES:
            self.assertNotIn(
                legacy.upper(),
                {k.upper() for k in m.RELATION_TYPES},
                "旧名 %s 仍在映射表里 ⇒ 会被原样派发" % legacy,
            )


# ── US3：冲突未决必须显式登记 ────────────────────────────────────────

def _load_sketch_relations():
    """加载 scripts/sketch_relations.py（stub 掉 sw_connect）。"""
    spec = importlib.util.spec_from_file_location(
        "sketch_relations_under_test", ROOT / "scripts" / "sketch_relations.py"
    )
    rel = importlib.util.module_from_spec(spec)
    stub = types.ModuleType("sw_connect")
    stub.get_com_member = lambda obj, name, *a, **k: None
    stub.set_com_member = lambda obj, name, value: None
    with patch.dict(sys.modules, {"sw_connect": stub}):
        spec.loader.exec_module(rel)
    return rel


class UndecidedRegistryTests(unittest.TestCase):
    def test_every_unaligned_name_is_registered(self):
        """SKETCH_CONSTRAINT_TYPES 的每项要么对齐官方，要么进入未决登记。"""
        rel = _load_sketch_relations()
        registry = getattr(rel, "UNDECIDED_CONSTRAINT_TYPES", None)
        self.assertIsNotNone(
            registry,
            "sketch_relations 缺未决登记 ⇒ 无法区分「对齐」「别名」「未决」三类",
        )
        for key, value in rel.SKETCH_CONSTRAINT_TYPES.items():
            official_name = TABLE_KEY_TO_OFFICIAL.get(key, key.upper())
            official = OFFICIAL_CONSTRAINT_TYPES.get(official_name)
            if official == value:
                continue
            self.assertIn(
                key, registry,
                "%s 既没对齐官方(%s=%r≠%r)又不在未决登记里"
                % (key, official_name, value, official),
            )

    def test_undecided_names_are_not_dispatchable(self):
        """未决名必须①不在可派发表的键里 ②被 `is_undecided_constraint` 认出。

        ★★ 这条让 `EXPECTED_UNDECIDED` 与 `is_undecided_constraint()` **真正被使用** ——
           此前它们一个是**死常量**、一个是**零调用点的死函数**
           （2026-10-08 由独立核对 `w2-34-spec-vs-implementation.md` 抓出，
           即 FR-008 实际未满足）。结构上的保护是「未决名**没有数值**可派发」，
           本判据把这条不变量钉住。
        """
        rel = _load_sketch_relations()
        keys = {k.lower() for k in rel.SKETCH_CONSTRAINT_TYPES}
        for name in EXPECTED_UNDECIDED:
            self.assertIn(name, rel.UNDECIDED_CONSTRAINT_TYPES,
                          "%s 不在未决登记里" % name)
            self.assertNotIn(name, keys,
                             "%s 出现在可派发表的键里 ⇒ 可能被派发" % name)
            self.assertTrue(rel.is_undecided_constraint(name),
                            "is_undecided_constraint(%r) 应为 True" % name)
        #: 反向：正常项不得被判为未决
        self.assertFalse(rel.is_undecided_constraint("coincident"))
        self.assertFalse(rel.is_undecided_constraint("PARALLEL"))

    def test_undecided_entries_carry_candidates_not_numbers(self):
        """未决登记必须写明「候选 + 为什么不能裁决」，且**不携带可派发数值**。"""
        rel = _load_sketch_relations()
        for name, info in rel.UNDECIDED_CONSTRAINT_TYPES.items():
            self.assertIn("why_undecided", info, "%s 缺裁决原因" % name)
            self.assertIn("official_candidates", info, "%s 缺候选清单" % name)
            self.assertTrue(info["official_candidates"],
                            "%s 的候选清单为空" % name)
            self.assertGreaterEqual(
                len(info["official_candidates"]), 2,
                "%s 只有一个候选 ⇒ 那就不叫「无法裁决」，应当直接定值" % name,
            )


# ── US2：公开面与字符串入口 ──────────────────────────────────────────

class PublicSurfaceTests(unittest.TestCase):
    def test_sw_part_whitelist_only_official_names(self):
        """_SG_RELATIONS 去 sg 前缀后必须都在官方 Remarks 清单里。"""
        m = _load_sw_part()
        illegal = []
        for name in m._SG_RELATIONS:
            body = name[2:] if name.lower().startswith("sg") else name
            if body.lower() not in OFFICIAL_SG_NAMES:
                illegal.append(name)
        self.assertEqual(illegal, [], "白名单含官方清单外的名字: %r" % illegal)

    def test_tool_spec_description_lists_only_official_names(self):
        """公开工具**合法值清单**里每个 sg 名都必须在官方 Remarks 清单里。

        ★ 判据取「合法值清单」段（`Legacy` 警告句之前），对该段做**逐个 sg 名**比对。
          只查 EQUAL / MIDPOINT 两个词是空判据 —— 别的非官方名进来照样过。
        """
        m = _load_tool_specs_batch16()
        spec = next(s for s in m.SPECS_BATCH16
                    if s.name == "solidworks_add_sketch_relation")
        text = " ".join([spec.doc] + [p.description for p in spec.params])
        valid_clause = text.split("Legacy")[0]
        found = {n.lower() for n in re.findall(r"\bsg[A-Za-z0-9]+\b", valid_clause)}
        self.assertTrue(found, "合法值清单里没找到任何 sg 名 ⇒ 判据失效")
        for name in sorted(found):
            self.assertIn(name[2:], OFFICIAL_SG_NAMES,
                          "合法值清单里出现非官方名 %s" % name)
        #: 正面要求：官方名必须在清单里
        self.assertIn("sgsamelength", found)
        self.assertIn("sgatmiddle", found)
        #: 警告句必须存在（告诉用户旧名无效）
        self.assertIn("Legacy", text)

    def _stub_sketch(self, status):
        sketch_mod = types.ModuleType("sw_sketch")

        class _Sketch:
            def GetConstrainedStatus(self):
                return status

        sketch_mod.active_sketch = lambda doc: _Sketch()
        return sketch_mod

    def test_string_entry_refuses_when_sketch_not_underconstrained(self):
        """非欠定义状态下，字符串入口必须在修改前拒绝。"""
        m = _load_sw_part()
        calls = []

        class _Model:
            def SketchAddConstraints(self, name):
                calls.append(name)
                return True

        model = _Model()
        with patch.dict(sys.modules, {"sw_sketch": self._stub_sketch(4)}), \
             contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(Exception):
                m.add_sketch_relation(model, "sgPARALLEL")
        self.assertEqual(calls, [], "非欠定义状态仍然改了关系 ⇒ 绕过了状态门")

    def test_string_entry_refuses_without_active_sketch(self):
        """没有活动草图时必须在修改前拒绝，且错误信息点明「没有活动草图」。"""
        m = _load_sw_part()
        calls = []

        class _Model:
            def SketchAddConstraints(self, name):
                calls.append(name)
                return True

        sketch_mod = types.ModuleType("sw_sketch")
        sketch_mod.active_sketch = lambda doc: None
        with patch.dict(sys.modules, {"sw_sketch": sketch_mod}), \
             contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(ValueError) as ctx:
                m.add_sketch_relation(_Model(), "sgPARALLEL")
        self.assertEqual(calls, [], "无活动草图仍然改了关系")
        #: ★ 必须点明是「没有活动草图」这条分支，而不是恰好被状态判据拦下
        self.assertIn("没有活动草图", str(ctx.exception))

    def test_string_entry_dispatches_once_when_underconstrained(self):
        """欠定义状态下恰好一次修改调用，名字原样透传。"""
        m = _load_sw_part()
        calls = []

        class _Model:
            def SketchAddConstraints(self, name):
                calls.append(name)
                return True

        with patch.dict(sys.modules, {"sw_sketch": self._stub_sketch(2)}), \
             contextlib.redirect_stdout(io.StringIO()):
            m.add_sketch_relation(_Model(), "sgPARALLEL")
        self.assertEqual(calls, ["sgPARALLEL"], "欠定义状态应恰好派发一次")

    def test_string_entry_rejects_legacy_name_with_official_hint(self):
        """sgEQUAL / sgMIDPOINT 必须被拒，且拒绝信息里**专门**给出官方名。

        ★★ 本判据必须断言提示的**专有措辞**，不能只断言「官方名出现在消息里」——
           因为合法值清单 `sorted(_SG_RELATIONS)` 本来就含官方名 ⇒ 那样写会在
           「别名提示整个失效」时**照样通过**。
           ⚠ 2026-10-08 实测栽过：别名表的键写成混合大小写而查表用 `.lower()`
             ⇒ **恒不命中、提示恒为空（死代码）**，而当时的弱判据仍绿。
        """
        m = _load_sw_part()
        for legacy, official in (("sgEQUAL", "sgSAMELENGTH"),
                                 ("sgMIDPOINT", "sgATMIDDLE")):
            with self.assertRaises(ValueError) as ctx:
                m.add_sketch_relation(object(), legacy)
            message = str(ctx.exception)
            self.assertIn("官方对应名为", message,
                          "%s 的拒绝信息里没有**专门**的别名提示" % legacy)
            self.assertIn(official, message,
                          "%s 的别名提示里没给官方名 %s" % (legacy, official))

    def test_legacy_alias_table_lookup_is_case_insensitive(self):
        """别名表查表必须大小写无关 —— 键与查询侧大小写不一致会导致恒不命中。

        ★ 这条是上面那个死代码缺陷的**直接判据**（不依赖错误消息文本）。
        """
        m = _load_sw_part()
        for legacy, official in (("sgEQUAL", "sgSAMELENGTH"),
                                 ("sgequal", "sgSAMELENGTH"),
                                 ("SGEQUAL", "sgSAMELENGTH"),
                                 ("sgMIDPOINT", "sgATMIDDLE"),
                                 ("sgmidpoint", "sgATMIDDLE")):
            cand = legacy if legacy.lower().startswith("sg") else "sg" + legacy
            self.assertEqual(
                m._SG_LEGACY_ALIASES.get(cand.lower()), official,
                "%s 查表未命中（键大小写与查询侧不一致？）" % legacy,
            )

    def test_sw_part_whitelist_is_complete(self):
        """白名单必须是完整的官方集合 —— 防止「只留几个也能过」。"""
        m = _load_sw_part()
        self.assertEqual({n.upper() for n in m._SG_RELATIONS},
                         {n.upper() for n in EXPECTED_SG_RELATIONS},
                         "_SG_RELATIONS 集合不完整或多了非预期项")

    def test_sw_part_whitelist_has_no_legacy_name(self):
        """白名单本身不得残留 sgEQUAL / sgMIDPOINT。"""
        m = _load_sw_part()
        body = {n[2:].lower() if n.lower().startswith("sg") else n.lower()
                for n in m._SG_RELATIONS}
        self.assertNotIn("equal", body, "白名单仍含 sgEQUAL")
        self.assertNotIn("midpoint", body, "白名单仍含 sgMIDPOINT")


if __name__ == "__main__":
    unittest.main()
