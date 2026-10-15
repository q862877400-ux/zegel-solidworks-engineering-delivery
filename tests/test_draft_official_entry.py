"""★ spec 239 判据：拔模特征的创建**必须走官方入口** `IFeatureManager::InsertMultiFaceDraft`。"""

# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tests/test_draft_official_entry.py
# 定位:   钉住 `scripts/sw_sheet_metal.py::create_draft` 的**创建路径**：
#         ① **不得**再出现 `CreateDefinition` 调用（`swFmDraft` 不在任何官方
#            `CreateDefinition` 宿主页的 `Type` 清单里 —— spec 238 已证）；
#         ② **必须**调用 `InsertMultiFaceDraft`，且实参个数 == **6**（官方签名）；
#         ③ 官方该页**不得**带 `Obsolete`（否则「官方入口」这个说法本身不成立）；
#         ④ 官方**前代**两页必须指向它（`Obsolete. Superseded by …`）—— 这是「取代方向」的证据；
#         ⑤ 反射转储的签名参数个数必须与官方页一致（**三源一致**）；
#         ⑥ `SHEET_METAL_RUNTIME_STATUS["create_draft"]` 必须是 `None`（**未测**）—— 不是 `True`
#            （★ 本规格是离线切片，**没跑 COM** ⇒ 不许把「照官方页改写」说成「真机可用」）；
#         ⑦ `swFmDraft` **不得**作为任何 `CreateDefinition` 调用的实参出现在 `scripts/` 里
#            （★ 这条是**内容断言**：它接住「有人把创建路径写回去」——
#              而 237/238 的 `sites` 棘轮本轮**已正当下调** 10 → 9，计数不再能接住它）。
# 官方依据: ① C:\swapi\types\IFeatureManager\InsertMultiFaceDraft.md
#           ② C:\swapi\types\IModelDoc2\InsertMfDraft{,2}.md（`Obsolete. Superseded by …`）
#           ③ D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt（反射转储）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts" / "sw_sheet_metal.py"
SWAPI = Path("C:/swapi/types")
DUMPS = ROOT / "_raw" / "reflect_sldworks" / "iface_sldworks.txt"

#: 官方入口名（三源一致的那个拼写；官方 `IModelDoc2` 页的 See-also 写作 `InsertMultifaceDraft`，
#: ★ 那是**链接文本**，真实成员名以 `types/IFeatureManager/InsertMultiFaceDraft.md` 与反射转储为准）。
ENTRY = "InsertMultiFaceDraft"


def _func(tree: ast.Module, name: str):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _calls(node: ast.AST) -> list:
    """⇒ `(成员名, 实参个数)` 列表。

    ★ 同时认**两种**调用形状（本仓两种都在用）：
      ① `obj.Member(a, b)` —— 点式；
      ② `get_com_member(obj, "Member", a, b)` / `call_com_member(...)` —— 本仓的 pywin32 兼容包装
         （★ 成员名是**字符串实参**，不是属性 ⇒ 只认点式会**读成 0 个调用**）。
      ★ 并把**裸名调用**（`Name`，如 `_create_from_definition(...)`）也记进来 —— 否则
        「不再走 `CreateDefinition` 那条路」这条判据会**漏掉经由共用骨架的间接路径**
        （★ 本规格实测：HEAD 版 `create_draft` 的 `CreateDefinition` 调用**藏在**
          `_create_from_definition` 里 ⇒ 只看点式会**读成 0** ⇒ 判据空转）。
    """
    out: list = []
    for sub in ast.walk(node):
        if not isinstance(sub, ast.Call):
            continue
        f = sub.func
        if isinstance(f, ast.Attribute):
            out.append((f.attr, len(sub.args)))
        elif isinstance(f, ast.Name):
            out.append((f.id, len(sub.args)))
        if (isinstance(f, ast.Name) and f.id in ("get_com_member", "call_com_member")
                and len(sub.args) >= 2 and isinstance(sub.args[1], ast.Constant)
                and isinstance(sub.args[1].value, str)):
            out.append((sub.args[1].value, len(sub.args) - 2))
    return out


def _import_sheet_metal():
    """★ 导入 `scripts.sw_sheet_metal` —— **必须桩掉 `sw_preflight`**。

    ⚠ 本规格实测：不桩 ⇒ 本机（受管 3.13.12）打印
    「检测到当前 Python 环境缺少 comtypes / win32com 库，是否授权 AI 自动为您配置本地环境？[Y/N]」
    并**卡住等人按键** ⇒ 无人值守下等同 SIGTERM。★ 用**宽松桩**（`sw_part` 会向它问若干成员，
    逐个列举很脆）。
    """
    import importlib
    import sys
    import types as _types

    class _Permissive(_types.ModuleType):
        def __getattr__(self, n):
            if n.startswith("__"):
                raise AttributeError(n)
            return lambda *a, **k: None

    pre = _Permissive("sw_preflight")
    pre.import_com_dependencies = lambda *a, **k: (None, None, None)
    pre.missing_com_dependencies = lambda *a, **k: []
    pre.ensure_com_dependencies = lambda *a, **k: []
    keys = ("sw_preflight", "scripts.sw_preflight")
    saved = {k: sys.modules.get(k) for k in keys}
    for k in keys:
        sys.modules[k] = pre
    try:
        for d in (ROOT, ROOT / "scripts"):
            if str(d) not in sys.path:
                sys.path.insert(0, str(d))
        return importlib.import_module("scripts.sw_sheet_metal")
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


class DraftOfficialEntryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = MODULE.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.src)

    # ── ①② 实现侧 ──────────────────────────────────────────────────
    def test_create_draft_no_longer_takes_the_create_definition_route(self):
        """★★ 创建路径**不再**走 `CreateDefinition` —— 包括**经由共用骨架**的间接路径。

        ★ 本规格实测（红基线）：HEAD 版 `create_draft` 里**没有**点式 `CreateDefinition`
          （它藏在 `_create_from_definition` 里）⇒ **只看点式会读成 0 ⇒ 判据空转**。
          所以这里把 `_create_from_definition` 也列为禁止项。
        """
        fn = _func(self.tree, "create_draft")
        self.assertIsNotNone(fn, "找不到 create_draft")
        names = {n for n, _ in _calls(fn)}
        self.assertNotIn("CreateDefinition", names)
        self.assertNotIn("_create_from_definition", names,
                         "★ 又走回 `CreateDefinition` 的共用骨架了（`swFmDraft` 官方不支持那条路）")

    def test_create_draft_calls_the_official_entry_with_six_args(self):
        """★ 必须调用 `InsertMultiFaceDraft`，实参 **6** 个（官方签名 / 反射转储一致）。"""
        fn = _func(self.tree, "create_draft")
        hits = [(n, k) for n, k in _calls(fn) if n == ENTRY]
        self.assertEqual(len(hits), 1, "应**恰好**一处 %s 调用，实际 %r" % (ENTRY, hits))
        self.assertEqual(hits[0][1], 6, "官方签名是 6 个形参，实际传了 %d 个" % hits[0][1])

    def test_create_draft_does_not_pass_the_forbidden_constant(self):
        """★ `SW_FM_DRAFT`（`swFmDraft`）**不得**再出现在 `create_draft` 里。"""
        fn = _func(self.tree, "create_draft")
        used = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)}
        used |= {n.attr for n in ast.walk(fn) if isinstance(n, ast.Attribute)}
        self.assertNotIn("SW_FM_DRAFT", used)

    def test_angle_is_converted_from_degrees_to_radians(self):
        """★ 官方 `Angle` 是**弧度**、本仓 spec 层是**度** ⇒ 边界处必须转换。"""
        fn = _func(self.tree, "create_draft")
        src = ast.get_source_segment(self.src, fn) or ""
        self.assertIn("radians", src, "官方 Angle 是弧度 ⇒ 必须显式转换（不能把度直接传进去）")

    # ── ③④⑤ 官方侧（便携：源不在 ⇒ 跳过）──────────────────────────
    def test_official_entry_page_carries_no_obsolete_mark(self):
        """★★ 「官方入口」这个说法**必须自证**：该页**不得**带 `Obsolete` 标注。"""
        p = SWAPI / "IFeatureManager" / ("%s.md" % ENTRY)
        if not p.is_file():
            self.skipTest("官方文档树不在：%s" % p)
        self.assertNotIn("Obsolete", p.read_text(encoding="utf-8", errors="replace"))

    def test_official_predecessors_point_at_the_entry(self):
        """★★ 官方**前代**两页写着 `Obsolete. Superseded by …InsertMultifaceDraft` —— 取代方向的证据。"""
        for name in ("InsertMfDraft", "InsertMfDraft2"):
            p = SWAPI / "IModelDoc2" / ("%s.md" % name)
            if not p.is_file():
                self.skipTest("官方文档树不在：%s" % p)
            text = p.read_text(encoding="utf-8", errors="replace")
            self.assertIn("Obsolete", text, "%s 应带 Obsolete 标注" % name)
            self.assertIn("InsertMultifaceDraft", text,
                          "%s 的取代目标应为 IFeatureManager::InsertMultifaceDraft" % name)

    def test_reflection_signature_agrees_on_six_parameters(self):
        """★ 反射转储里该成员的形参个数必须 == 官方页的 **6**（三源一致）。"""
        if not DUMPS.is_file():
            self.skipTest("反射转储不在：%s" % DUMPS)
        m = re.search(r"\b%s\s*\(([^)]*)\)" % ENTRY,
                      DUMPS.read_text(encoding="utf-8", errors="replace"))
        self.assertIsNotNone(m, "反射转储里找不到 %s" % ENTRY)
        params = [x for x in m.group(1).split(",") if x.strip()]
        self.assertEqual(len(params), 6, "反射转储给出 %d 个形参" % len(params))

    # ── ⑥ 状态表 ────────────────────────────────────────────────────
    def test_runtime_status_reflects_the_machine_evidence(self):
        """★★★ **状态必须与真机证据一致** —— ★ 239 时是 `None`（离线切片），★ **283 真机建成后升为 `True`**。

        ⚠⚠ **本判据 2026-10-10 订正（规格 296）** —— 原文逐字是：
        ```
        def test_runtime_status_says_untested_not_verified(self):
            '''★★ **不许把「照官方页改写」说成「真机可用」**：状态必须是 `None`（未测）。'''
            self.assertEqual(m.group(1), "None", …)
        ```
        ★★ **它当时是对的**（239 是**离线切片**，★ 那时**确实**没有真机证据）。
        ★★★ **而 283 把状态升成了 `True`，却没同步改这条判据** ⇒ ★★ **它变成一条恒红的陈旧判据**
        （★ `MEMORY.md` 规则 28 逐字：「改实现前先搜『有没有测试钉住旧行为』 ——
        ★ 不同步改就等于**在断言错的东西**」）。

        ★ 订正后的判据**保留原意图**（「不许无证据地自称可用」）：
        ★★ **状态与真机证据必须一致** —— ★ 若为 `True`，★ 283 的真机读数**必须**在。
        """
        m = re.search(r'"create_draft":\s*\(\s*(None|True|False)', self.src)
        self.assertIsNotNone(m, "状态表里找不到 create_draft")
        status = m.group(1)
        if status == "True":
            #: ★★ 升为 `True` ⇒ **必须**有真机证据（★ 283 的读数文件）
            probe = ROOT / "output" / "_probe283_draft_dir.txt"
            self.assertTrue(probe.is_file(),
                            "★ 状态是 `True` 但 283 的真机读数不见了 ⇒ **无证据地自称可用**")
            body = probe.read_text(encoding="utf-8", errors="replace")
            self.assertIn("拔模1", body, "★ 真机读数里没有建成的特征名 ⇒ 证据不支持 `True`")
        else:
            #: ★ 仍为 `None`/`False` ⇒ ★ 那是**未测**，★ 不得同时宣称可用
            self.assertIn(status, ("None", "False"), "★ 非法状态值 %r" % status)

    # ── ⑦ 内容断言（接住「写回去」）──────────────────────────────────
    def test_swfm_draft_is_never_passed_to_create_definition(self):
        """★★ `scripts/**/*.py` 里**不得**存在 `CreateDefinition(SW_FM_DRAFT…)` 这类调用。"""
        offenders: list = []
        for p in sorted((ROOT / "scripts").glob("*.py")):
            try:
                tree = ast.parse(p.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                if not (isinstance(node.func, ast.Attribute)
                        and node.func.attr == "CreateDefinition"):
                    continue
                for a in node.args:
                    text = ast.get_source_segment(p.read_text(encoding="utf-8"), a) or ""
                    if "SW_FM_DRAFT" in text or "swFmDraft" in text:
                        offenders.append("%s:%d" % (p.name, node.lineno))
        self.assertEqual(offenders, [],
                         "★ 拔模又走回官方不支持的路径了：%r" % offenders)

    # ── spec 的 spec 层字段 ─────────────────────────────────────────
    def test_spec_fields_cover_the_official_six_params(self):
        """★ `DraftFeatureSpec` 必须能表达官方 6 参（不是只留 angle/depth）。"""
        from dataclasses import fields

        sm = _import_sheet_metal()
        names = {f.name for f in fields(sm.DraftFeatureSpec)}
        for must in ("angle", "reverse_direction", "edge_draft", "prop_type",
                     "is_step_draft", "is_body_draft"):
            self.assertIn(must, names)

    def test_prop_type_out_of_official_range_is_rejected_before_com(self):
        """★ 官方 `PropType` 只列 0–4 ⇒ 越界必须在**进 COM 前**拒绝。"""
        sm = _import_sheet_metal()
        for bad in (5, -1, 99):
            with self.assertRaises(ValueError):
                sm.DraftFeatureSpec(angle=5.0, depth=0.01, prop_type=bad).validate()
        sm.DraftFeatureSpec(angle=5.0, depth=0.01, prop_type=4).validate()


if __name__ == "__main__":
    unittest.main()
