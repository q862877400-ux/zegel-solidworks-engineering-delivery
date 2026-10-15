"""★ 规格 296 判据：`create_draft` 的 `pre_call` 必须**同时**建立两个选择（方向项 mark 1 + 面 mark 2）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch4.py`（★ `_pre_draft` · `solidworks_sheet_metal_create_draft`）
#         `output/_probe283_draft_dir.txt`（★ 真机配方：`Front Plane` + 面#0 ⇒ 成功「拔模1」）
#         `C:\swapi\types\IFeatureManager\InsertMultiFaceDraft.md`（★ mark 1/2/4）
# 定位:   ① `pre_call` 必须**同时**选**平面（mark 1）**与**面（mark 2）**；
#         ② 方向项必须是**声明式**参数（平面**名**，★ 规则 3 不给裸坐标）；
#         ③ 前置没备齐**必须抛**（★ 不许静默继续）；
#         ④ 判据能红（★ 事实 62）；⑤ 边界冻结（不改实现签名）。
# 官方依据: `C:/swapi/types/IFeatureManager/InsertMultiFaceDraft.md`（★ 6 参 · mark 1/2/4）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 不连 COM；★ 真机读数由 283 的探针产出）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECS_FILE = ROOT / "mcp-server" / "tool_specs_batch4.py"
IMPL_FILE = ROOT / "scripts" / "sw_sheet_metal.py"

#: ★★★ 283 的真机配方（★ 逐字来自 `output/_probe283_draft_dir.txt`）
MACHINE_RECIPE = {"plane": "Front Plane", "face_index": 0, "selected": 2, "feature_name": "拔模1"}
#: ★★ 官方 mark（`InsertMultiFaceDraft.md` 逐字）
MARK_DIRECTION = 1
MARK_FACE = 2


def _src() -> str:
    return SPECS_FILE.read_text(encoding="utf-8")


def _func_src(name: str) -> str:
    """★ 取 `tool_specs_batch4.py` 里某个函数的源码段（★ 按名字，不按行号）。"""
    text = _src()
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(text, node) or ""
    return ""


def test_pre_call_selects_both_a_plane_and_a_face():
    """★★★ FR-001：`_pre_draft` 必须**同时**选**平面（mark 1）**与**面（mark 2）**。

    ★ 283 逐字：★ 只给面（18 臂）⇒ 全失败，报文恒定「此拔模方向尚未定义。」
      ★ 而 `Front Plane` + 面#0 ⇒ **成功**（`拔模1`）。
    ⇒ ★★ 少给任何一个前置 ⇒ 真机**必失败**。
    """
    body = _func_src("_pre_draft")
    assert body, "`_pre_draft` 不见了"
    #: ★ 必须**同时**出现「平面」与「面」两条选择路径
    has_plane = ("PLANE" in body) or ("plane" in body) or ("方向" in body)
    has_face = "FACE" in body
    assert has_plane and has_face, (
        "★ `_pre_draft` 只建立了**一个**选择 ⇒ 真机会报「此拔模方向尚未定义。」\n"
        "   平面（mark 1）在不在：%s · 面（mark 2）在不在：%s\n%s" % (has_plane, has_face, body)
    )
    #: ★★ 两个 mark 都要出现（★ 官方 mark 1 / 2）
    assert re.search(r"\b1\b", body) and re.search(r"\b2\b", body), (
        "★ 两个 mark（方向项 1 / 面 2）没有都出现：\n%s" % body
    )


def test_direction_is_a_declarative_param():
    """★★ FR-002：方向项必须是**声明式**参数（★ 平面**名**，★ 规则 3 不给裸坐标）。"""
    src = _src()
    assert "direction_plane" in src, (
        "★ 工具参数里没有 `direction_plane` ⇒ ★ 调用方**无法表达方向项** ⇒ "
        "★ 283 的真机配方（Front Plane + 面）经工具层复现不了"
    )
    #: ★ 规则 3：参数名不得是裸坐标（x / y / z / cx / cy / cz）
    for bad in ("cx", "cy", "cz"):
        assert not re.search(r'Param\(\s*"%s"' % bad, src), "★ 出现裸坐标参数 %r（违反规则 3）" % bad


def _called_chain(name: str, depth: int = 3) -> str:
    """★ 取 `name` 及其**传递闭包**里各函数的源码（★ 本模块内）。

    ★ 为什么要闭包：★★ 纪律（`MEMORY.md` 规则 21）逐字「**「只看点式调用」= 空判据** ——
      调用**藏在共用骨架**里时读成 0 个调用 ⇒ 改前也是绿的」⇒ ★ 修法 = **做传递闭包**。
    ★ 本处形态：★ 「前置没备齐就抛」这个性质**可以**落在 `_pre_draft` 自己身上、
      ★ 也**可以**落在它调用的帮手（`_select_plane`）身上 —— ★ 后者同样成立
      ⇒ ★★ 只看 `_pre_draft` 一个函数会**误报**（★ 正是规则 21 的形态）。
    """
    text = _src()
    tree = ast.parse(text)
    funcs = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    seen: set[str] = set()
    parts: list[str] = []

    def walk(fn_name: str, left: int) -> None:
        if fn_name in seen or left <= 0 or fn_name not in funcs:
            return
        seen.add(fn_name)
        node = funcs[fn_name]
        parts.append(ast.get_source_segment(text, node) or "")
        for inner in ast.walk(node):
            if isinstance(inner, ast.Call):
                f = inner.func
                callee = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")
                if callee in funcs:
                    walk(callee, left - 1)

    walk(name, depth)
    return "\n".join(parts)


def test_pre_call_raises_when_the_plane_is_missing():
    """★★★ FR-003：前置没备齐**必须抛**（★ 不许静默继续 —— 那会把"前置没上"记成"能力不成"）。

    ★ 判据取 `_pre_draft` 的**传递闭包**（★ 规则 21：只看一个函数会误报）。
    """
    body = _called_chain("_pre_draft")
    assert body, "`_pre_draft` 不见了"
    assert "raise" in body, (
        "★ `_pre_draft` 及其调用的帮手**都没有 `raise`** ⇒ ★ 平面选不上时会**静默继续** ⇒ "
        "★ 真机报「此拔模方向尚未定义。」而**看不出是前置没上**：\n%s" % body
    )


def test_criterion_is_red_able():
    """★★★ FR-004：判据必须**能红**（★ 事实 62：写了 ≠ 有效）。

    ★ 拿**旧形态**（只选面）当负例喂进判据的核心断言 ⇒ ★ 必须报错。
    """

    def judge(body: str) -> list:
        """★ 复刻 `test_pre_call_selects_both_a_plane_and_a_face` 的核心判据。"""
        bad = []
        if not (("PLANE" in body) or ("plane" in body) or ("方向" in body)):
            bad.append("缺平面")
        if "FACE" not in body:
            bad.append("缺面")
        return bad

    #: ★ 负例 = **修复前的真形态**（★ 逐字来自 git 历史里的 `_pre_draft`）
    old_form = 'def _pre_draft(params):\n    _select(params, "FACE")\n'
    assert judge(old_form), "★ 旧形态（只选面）**没被判红** ⇒ 判据是空判据"
    #: ★ 正例
    new_form = 'def _pre_draft(params):\n    _select_plane(params, mark=1)\n    _select(params, "FACE")\n'
    assert not judge(new_form), "★ 新形态被判红了 ⇒ 判据过严"


def test_implementation_signature_untouched():
    """★★ FR-005：边界冻结 —— ★ 不改 `sw_sheet_metal.create_draft` 的签名与调用。"""
    text = IMPL_FILE.read_text(encoding="utf-8")
    assert re.search(r"def create_draft\(model, face_ref, spec: DraftFeatureSpec\)", text), (
        "★ `create_draft` 的签名被改了 —— 本轮**只接 `pre_call`**，★ 不动实现"
    )
    assert "InsertMultiFaceDraft" in text, "★ 实现里的官方入口不见了"


def test_machine_recipe_is_recorded():
    """★★ 283 的真机配方必须**留档可查**（★ 判据的靶子来自它，★ 不能只有散文）。"""
    probe = ROOT / "output" / "_probe283_draft_dir.txt"
    assert probe.is_file(), "★ 283 的真机读数不见了（★ 本规格的靶子）"
    body = probe.read_text(encoding="utf-8", errors="replace")
    assert "Front Plane" in body and "拔模1" in body, (
        "★ 283 的读数里没有 `Front Plane` / `拔模1` ⇒ 配方对不上"
    )
    assert MACHINE_RECIPE["feature_name"] in body
