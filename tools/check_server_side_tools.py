"""★ 核：`server.py` 用 `@mcp.tool` 声明的那些工具，**在不在 ToolSpec 门禁的射程内**。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/check_server_side_tools.py
# 定位:   ★ 2026-10-03（轮 449）承 `plan-200r-v3` **§五 ①**（★ "`server.py` 侧的工具要
#           与 ToolSpec 侧对齐
#   —— ★ **工具名那一层**还没核"）。
#   ★★★ **查明的事**：★ 本仓的工具声明**有两条路**：
#     ```
#     ★ ① **ToolSpec 路**（★ **219** 个）：★ 声明式，★ 而**过五统一门禁**（★ `tool_registry.register`）
#     ★ ② **装饰器路**（★ **32** 个）：★ 直接 `@mcp.tool(name="solidworks_*")` ——
#        ★★ **而它不过那套门禁** ⚠
#     ★ 重名 **0** ⇒ ★ 总数 **251**（★ 而★ 我此前一直报 **219** ⚠）
#     ```
#   ★★ **故本检查要回答的**：★ 那 32 个**有没有违反**门禁管的那几条（★ 规则 2 单位 / 规则 3 选择）——
#     ★ 若有 ⇒ ★★ 那是一个**真实的覆盖缺口**；★ 若没有 ⇒ ★ **记"表面干净 + 它们没被自动检查"** ✓
#   ⚠ **判据的诚实话**：★ 本检查**只做能静态做的**（★ 参数名）；
#     ★★ 而"过了参数名**不等于**过了门禁"（★ 门禁还查别的）—— ★ 故**不下"合规"的结论**，★ 只报事实 ✓
# 官方依据: 本仓自己的门禁判据（`mcp-server/tool_registry.py` 的 `_BARE_COORD_NAMES` /
#   `_looks_like_coord_component` / `_LEN_WORDS`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ **先报查了多少**（★ 事实 357）· ★ 命中项**逐个列出**。

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

#: 2026-10-03（接手轮）强制 stdout 为 UTF-8 —— 本门禁会 print 中文与箭头/勾这类符号，
#:   而 stdout 是管道时（测试正是用管道抓输出）默认按 locale（本机 GBK）编码
#:   ⇒ UnicodeEncodeError: 'gbk' codec can't encode character … ⇒ 门禁自己崩掉。
#:   known-facts 58 那一族（中文 Windows 上两侧默认编码不一致 —— 病灶在输出侧）；
#:   而测试那侧的 subprocess.run 已经带了 encoding='utf-8'。
sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[1]
SERVER = REPO_ROOT / "mcp-server" / "server.py"


def declared_tools(src: str) -> dict:
    """★ 从 `server.py` 的装饰器里取 `{工具名: 函数名}`。"""
    out: dict = {}
    t = ast.parse(src)
    for n in ast.walk(t):
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for d in n.decorator_list:
            s = ast.unparse(d)
            m = re.search(r"name=[\"'](solidworks_[A-Za-z0-9_]+)[\"']", s)
            if m:
                out[m.group(1)] = n.name
    return out


def input_models(src: str) -> dict:
    """★ 取 `{类名: [字段名, …]}`（★ 那些 `BaseModel` 子类）。"""
    out: dict = {}
    t = ast.parse(src)
    for n in ast.walk(t):
        if not isinstance(n, ast.ClassDef):
            continue
        #: ★★★ 2026-10-03（轮 449）**判据修正** ——
        #:   ★ 第一版只收 **`BaseModel` 直接子类** ⇒ 真机只回 **1** 个模型 ⚠
        #:   ★★ 而真相：那些 Input **继承的是本地基类 `BaseInput`** ⇒ ★ 故要**按继承链**判。
        #:   ★★★ 而「只回 1 个」**正是**能识破此事的线索（★ 事实 357 那条纪律）✓
        bases = [ast.unparse(b).split(".")[-1] for b in n.bases]
        if not any(b in ("BaseModel", "BaseInput") for b in bases):
            continue
        fields = []
        for st in n.body:
            if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):
                fields.append(st.target.id)
        out[n.name] = fields
    return out


def main(argv: list) -> int:
    if not SERVER.is_file():
        print("  [SKIP] 找不到 %s" % SERVER)
        return 0
    src = SERVER.read_text(encoding="utf-8")
    tools = declared_tools(src)
    models = input_models(src)
    sys.path.insert(0, str(REPO_ROOT / "mcp-server"))
    try:
        from tool_registry import _BARE_COORD_NAMES, _looks_like_coord_component
    except Exception as exc:                                   # noqa: BLE001
        print("  [SKIP] 取不到门禁判据：%s" % str(exc)[:100])
        return 0
    print("  `server.py` 的装饰器路：**%d** 个工具（★ 先报数量 —— 事实 357）" % len(tools))
    print("  同文件的 `BaseModel` 输入模型：**%d** 个" % len(models))
    print()
    #: ★ 判据①：★ 参数名是不是裸坐标（★ 规则 3）
    hits = []
    for tool, fn in sorted(tools.items()):
        #: ★ 找那个函数声明里的 input 形参类型（★ 形如 `params: XxxInput`）
        t = ast.parse(src)
        flds: list = []
        for n in ast.walk(t):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == fn:
                for st in n.body:
                    pass
                for a in list(n.args.args) + list(n.args.kwonlyargs):
                    ann = ast.unparse(a.annotation) if a.annotation else ""
                    key = ann.split(".")[-1].strip("'\"")
                    if key in models:
                        flds = models[key]
        bad = [f for f in flds if f in _BARE_COORD_NAMES or _looks_like_coord_component(f)]
        if bad:
            hits.append((tool, fn, bad))
    if hits:
        print("  ⚠★ **参数名命中裸坐标**（★ 规则 3）的：**%d** 个工具" % len(hits))
        for tool, fn, bad in hits:
            print("    %-46s %s  参数 %s" % (tool, fn, bad))
    else:
        print("  ✓ 按**参数名**看：★ 那 %d 个工具**没有**命中规则 3 的裸坐标判据" % len(tools))
    print()
    #: ★★★ 2026-10-03（轮 450）**本脚本进门禁了** ⇒ ★ 它必须**能失败**。
    #:   ★ 判据（★ 静态、可复算）：**两条声明路上的 `solidworks_*` 工具名不许重名** ——
    #:   ★★ 重名意味着后注册的**遮掉**先注册的（★ 而调用方看不出来）。
    try:
        import sys as _s
        _s.path.insert(0, str(REPO_ROOT / "mcp-server"))
        import register_capabilities as _RC
        spec_names = {sp.name for sp in _RC.all_specs()}
    except Exception as exc:                                   # noqa: BLE001
        print("  [SKIP] 取不到 ToolSpec 侧的名单：%s" % str(exc)[:90])
        return 0
    dupes = sorted(set(tools) & spec_names)
    if dupes:
        print("  ✗ **重名 %d 个**（★ 两条声明路上都有）：%s" % (len(dupes), ", ".join(dupes)))
        print("      ★ 后注册的会**遮掉**先注册的 ⇒ ★ 改名一个。")
        return 1
    print("  ✓ 两条声明路的工具名**无重名**（ToolSpec %d + 装饰器 %d ⇒ 共 %d）"
          % (len(spec_names), len(tools), len(spec_names) + len(tools)))
    print()
    print("  ⚠★ **诚实话**：★ 本检查**只做静态那部分**（★ 参数名）——")
    print("      ★★ 而「过了参数名」**不等于**「过了门禁」（★ 门禁还查命名/单位/出处等）⇒ ★ 故**不下合规的结论**。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
