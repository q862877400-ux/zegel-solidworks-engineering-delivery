"""★ 阶段 1 · 效应解析（补 C1 —— ★ 接上官方类型库的读写标记）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/effects.py
# 定位:   规格 `specs/316-stage1-parameter-plate` 的 C1（统一目录）的**效应解析**部分
#           。★★ 为什么必须做：实测（2026-10-11）`docs/effect-declarations.json` 里**278
#            个工具 `writes=null`**（占 476 的 58%），而该表自己的 `_limitations` 逐字写
#           ：  「★ 只用动词这一路；★ 官方类型库的读写标记**未参与**」  「★ 只跟**同模块
#           **助手 2 层；★ 跨模块调用的成员**扫不到**」  「★ writes:null 的工具，★ 注册
#           层按「未知」保守处理」⇒ ★ 而按「未知 ⇒ 不得自动执行」的纪律（I5），那 278 个
#           **全都进不了执行集**  ⇒ ★★ **方法库要用的 11 个工具里，8 个卡在这里**。
# 官方依据: ① `docs/effect-declarations.json` 的 `_` / `_judge` / `_limitations`（逐字）
#           ② `C:\\swapi\\types\\<接口>\\<成员>.md` 的 `## Returns` / 动词③ 本仓 `tools/
#           gen_effect_declarations.py`（既有生成器）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 效应解析的判据是**静态**的（AST + 成员动词），
#    ★ 尚未用真机交叉验证（那属阶段 1 的真机验收）。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]

#: ══ 一、成员动词 → 效应（★ 与既有生成器同一族口径）═══════════════════
#: ★★ 判据：**写**的动词前缀（改文档 / 改属性 / 改选择 / 写文件）
WRITE_VERBS = (
    "Insert", "Create", "Add", "Set", "Delete", "Remove", "Modify", "Edit",
    "Clear", "Save", "Close", "Open", "Export", "Import", "Rebuild", "Force",
    "Update", "Replace", "Move", "Copy", "Scale", "Mirror", "Pattern",
    "Extrude", "Revolve", "Fillet", "Chamfer", "Shell", "Draft", "Thicken",
    "Sketch", "Select", "Unselect", "Activate", "Exit", "Run", "Load",
)
#: ★ 明确**只读**的动词
READ_VERBS = (
    "Get", "Is", "Has", "Read", "List", "Count", "Find", "Query", "Collect",
    "Inspect", "Check", "Measure", "Evaluate", "Test", "Describe",
)

#: ══ 二、效应分级 ══════════════════════════════════════════════════════
WRITE = "write"
READ = "read"
UNKNOWN = "unknown"


def _member_effect(name: str) -> str:
    """★ 单个 COM 成员名的效应（★ 先判读、再判写 —— ★ 因为 `IsXxx` 比 `SetXxx` 更专指）。"""
    if name.startswith(READ_VERBS):
        return READ
    if name.startswith(WRITE_VERBS):
        return WRITE
    return UNKNOWN


def _bodies(mod: str) -> dict[str, str]:
    """★ 取模块里每个函数的**真代码**（★ 去掉 docstring —— 事实：docstring 会骗人）。"""
    p = ROOT / "scripts" / ("%s.py" % mod)
    if not p.is_file():
        return {}
    try:
        tree = ast.parse(p.read_text(encoding="utf-8"))
    except Exception:                                                      # noqa: BLE001
        return {}
    out: dict[str, str] = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef):
            b = n.body
            if b and isinstance(b[0], ast.Expr) and isinstance(b[0].value, ast.Constant) \
                    and isinstance(b[0].value.value, str):
                b = b[1:]
            out[n.name] = "\n".join(ast.unparse(x) for x in b)
    return out


def resolve_effect(mod: str, fn: str, *, depth: int = 3) -> tuple[str, list[str]]:
    """★ 从实现里**推出**效应（★ 返回 `(effect, 依据的成员名)`）。

    ★★ 与 `docs/effect-declarations.json` 的**分工**（★ 不是替代）：
      · 那张表是**生成物**（`_` 逐字「★ 不要手改」）
      · 本函数是**注册阶段的补充判据** —— 表说 `null` 时，用**同一族动词口径**
        加上**跨模块传递闭包**再判一次
      · ★ 两者结论冲突时：**保守者胜**（未知 > 写 > 读）—— ★ 与表的 `_judge` 一致

    ★★ 判据（★ 保守优先）：
      · 追到的成员里**有写** ⇒ `write`（★ 写优先 —— 一个写就够）
      · 全是读且**至少一个** ⇒ `read`
      · 一个都没追到 ⇒ `unknown`（★ **不是** `read` —— 与表的 `_judge` 逐字一致）
    """
    bodies = _bodies(mod)
    if not bodies:
        return UNKNOWN, []
    seen: set[str] = set()
    members: list[str] = []

    def walk(name: str, d: int) -> None:
        if d < 0 or name in seen:
            return
        seen.add(name)
        src = bodies.get(name)
        if not src:
            return
        #: ★★ 本仓的 COM 调用有**两种写法**（★ 实测 2026-10-11 才发现）：
        #:   ① `.Member(...)`                        —— 直接属性访问
        #:   ② `get_com_member(obj, 'Member', ...)`  —— ★ **成员名是字符串实参**
        #:      ★★ 第二路是**主流**（`sw_part.sketch_circle` 就是这种）
        #:      ⇒ 只匹配 `.Xxx(` 会**漏掉绝大多数**（实测：`sketch_circle` 判 unknown）
        for m in re.finditer(r"\.(\w+)\s*\(", src):
            members.append(m.group(1))
        for m in re.finditer(
                r"(?:get_com_member|call_com_member|safe_get_com_member)\s*\([^,]+,\s*[\"'](\w+)[\"']", src):
            members.append(m.group(1))
        #: ★ 同模块助手（★ 传递闭包 —— 补表 `_limitations` 的「只跟 2 层」）
        for m in re.finditer(r"\b([a-z_][a-z0-9_]*)\s*\(", src):
            if m.group(1) in bodies:
                walk(m.group(1), d - 1)

    walk(fn, depth)
    effects = {_member_effect(m) for m in members}
    if WRITE in effects:
        return WRITE, [m for m in members if _member_effect(m) == WRITE]
    if READ in effects:
        return READ, [m for m in members if _member_effect(m) == READ]
    return UNKNOWN, []


def conservative(*effects: str) -> str:
    """★ 保守合成（★ 未知 > 写 > 读）—— ★ 与表的 `_judge` 同口径。"""
    order = {UNKNOWN: 2, WRITE: 1, READ: 0}
    best = UNKNOWN
    for e in effects:
        if e not in order:
            continue
        if order[e] > order[best]:
            best = e
    return best
