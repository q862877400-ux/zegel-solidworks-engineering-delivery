r"""@brief 环境坑静态检查：`subprocess` 缺 `encoding=` / `Path("<盘符>:")` 当盘根。

## 为什么要有它（两个**刚修完的真实 bug**，都会复发）
```
① **`subprocess.run(..., text=True)` 不给 `encoding=`**
   ⇒ 用 `locale.getpreferredencoding()`（中文 Windows 是 **GBK**）
   ⇒ 子进程的 **UTF-8 中文**输出解不了 ⇒ `UnicodeDecodeError`
   ⇒ **`completed.stdout` 变成 `None`** ⇒ 下游 `json.loads(None)` 抛 `TypeError`
   （**错误信息指向不了真因** —— 你会去查 JSON，而问题在编码）
   ⇒ 2026-10-01 本仓 **11 处**这样写，**4 个基线失败全因此**（已知事实 58）。

② **`Path("D:")` 是「带盘符的**相对**路径」，不是盘根**
   ⇒ `Path("D:") / "AutoCAD 2024" / "acad.exe"` = `'D:AutoCAD 2024\acad.exe'`（**缺反斜杠**）
   ⇒ **D:/E: 盘上的安装永远发现不了**（已知事实 59，**真实功能 bug**）
```

**⇒ 把这两条做成**门禁**：它们是**机制性**的（不依赖某次运行的环境），
可以纯静态判定，**适合挂进 `release_check.py`**。**

## ⚠ 判据的两处讲究（都是本会话踩出来的）
```
· 「**某个调用带没带某参数**」必须按**括号配对**切分整段调用。
  按「第一个 `)`」截断会**假阳性** —— 我第一次就这么错，报了 23 处，真值 11 处（事实 58）。
· **跳过注释与字符串**：我第二次把来源块**散文里**的示例文本也当成了真调用（事实 60）。
  ⇒ 本检查用 `tokenize` **剥掉注释与字符串**后再扫。
```

## 与既有门禁的分工（**不重造**）
`check_provenance`（出处）/ `check_member_names`（成员名）/ `check_diff_markers`（diff 记号）
/ `check_union_conventions`（并入规范）—— 都管**内容**；本门禁管**语言/平台的机制性坑**。

# ── 来源 ──
# 仓库:   本项目自身（门禁实现）+ Python 标准库 `subprocess` / `pathlib` / `tokenize` 文档
# 文件:   scripts/check_env_pitfalls.py —— 本文件自身
#         tests/test_env_pitfalls_gate.py（契约测试 + 负例）
# 定位:   把已知事实 58（subprocess 缺 encoding）与 59（Path("D:") 不是盘根）
#         从「人记得」升级为「门禁守着」。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import ast
import io
import re
import sys
import tokenize
from pathlib import Path

#: ★★★ 2026-10-03（接手轮）**必须强制 stdout 为 UTF-8** —— ★ 本门禁会 `print` 中文与 `⇒`
#: /`→` 这类符号，
#: 而默认走 `locale.getpreferredencoding()`（★ 本机 **GBK**）⇒ ★ 一旦 stdout 是**管道**
#: ，
#: `print("… ⇒ …")` 直接 **`UnicodeEncodeError: 'gbk' codec can't encode character '\u21
#: d2'`**
#:   ⇒ ★★ **门禁自己崩掉**（★ 实测：`scripts/check_env_pitfalls.py:366` 那行；
#:     连带 `scripts/release_check.py:1192` 报「环境陷阱门禁未通过」；
#: 再连带 `tests/test_gate_negative_cases.py::test_gate_details_exposed_for_every_gate`
#: 失败）。
#:   ★ 这是 **known-facts 58** 那一族的**第四个实例** —— 前三个分别在：
#:     ① 测试里的 `subprocess.run` 缺 `encoding=`；② 本仓 11 处同类；
#:     ③ `tools/check_judge_preflight.py`（**子进程输出侧**）。
#:   ★★ 病灶的共同点：★ **中文 Windows 上，"默认编码"在两个进程之间不一致** ——
#:     ★ 而 `print` 与 `subprocess` **两侧都可能出错**，★ 只修一侧修不干净。
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]

#: 扫哪些目录（**只扫真正会被执行的代码**）
SCAN_DIRS = ("scripts", "tools", "mcp-server", "tests", "apps/desktop")

#: `subprocess` 的对端：必须显式给编码
SUBPROCESS_CALL = re.compile(r"subprocess\.(run|Popen|check_output|check_call)\s*\(")

#: ⚠ `Path("D:")` 这类**带盘符的相对路径**（真盘根应写 `"D:/"` 或 `r"D:\\"`）
DRIVE_ONLY = re.compile(r"""Path\(\s*['"]([A-Za-z]):['"]\s*\)""")

#: ⚠⚠ **真实 bug 的形态是 `Path(drive)`，不是字面量！**
#: 2026-10-01（轮 46）教训：门禁第一版**只认字面 `Path("D:")`**，
#: 而 `scripts/cad_installation.py` 里写的是 `root = Path(drive)`（`drive` 是循环变量）
#: ⇒ **负例测试当场证明门禁抓不到真 bug**（「一个存在但没人用的守卫与没有守卫等价」）。
#: **⇒ 补一条轻量数据流：先找被绑定成 `"X:"` 的变量名，再找 `Path(<那个变量>)`。**
DRIVE_LITERAL_ASSIGN = re.compile(
    r"""(?:for\s+(\w+)\s+in\s*\(|(\w+)\s*=\s*)[^)\n]*['"]([A-Za-z]):['"]"""
)
PATH_OF_VAR = re.compile(r"""Path\(\s*(\w+)\s*\)""")

#: 「这个常量看起来就是盘根名」的白名单（例如 `EXPECTED_DRIVE = "D:"` 是合法的中间量）
ALLOW_DRIVE_ONLY_IF = re.compile(r"(drive|DRIVE|盘符)")


def strip_comments_and_strings(source: str) -> str:
    """把注释与字符串**替换成等长空白** ⇒ 行号/列号不变，但扫不到散文里的示例。

    ⚠ **这一步是必须的**：本会话第二次踩坑就是把来源块**散文里**的
    `` `subprocess.run(..., text=True)` `` 当成了真调用（事实 60）。
    """
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return source  # 语法有问题时退回原文（由别的门禁报语法）
    drop = {tokenize.COMMENT, tokenize.STRING}
    out, last = [], (1, 0)
    lines = source.splitlines(keepends=True)
    for tok in tokens:
        if tok.type not in drop:
            continue
        (sr, sc), (er, ec) = tok.start, tok.end
        # 把 [start, end) 区间替换成空格（保留换行）
        for r in range(sr, er + 1):
            if r - 1 >= len(lines):
                continue
            line = lines[r - 1]
            a = sc if r == sr else 0
            b = ec if r == er else len(line.rstrip("\n"))
            if a < b:
                line = line[:a] + " " * (b - a) + line[b:]
                lines[r - 1] = line
        last = tok.end
    del out, last
    return "".join(lines)


def balanced_call(text: str, start: int) -> str:
    """按**括号配对**取 `(` 起整段调用文本。

    ⚠ 按「第一个 `)`」截断会**假阳性**（事实 58：23 vs 真值 11）。
    """
    i = text.find("(", start)
    if i < 0:
        return ""
    depth, j = 0, i
    while j < len(text):
        ch = text[j]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return text[i : j + 1]
        j += 1
    return text[i:]


def find_missing_encoding(path: Path) -> list:
    """⇒ ``[(行号, 调用片段)]``：`text=True` 但整段无 `encoding=` 的 `subprocess` 调用。"""
    src = path.read_text(encoding="utf-8", errors="replace")
    clean = strip_comments_and_strings(src)
    out = []
    for m in SUBPROCESS_CALL.finditer(clean):
        seg = balanced_call(clean, m.start())
        if "text=True" in seg and "encoding=" not in seg:
            out.append(
                (
                    clean[: m.start()].count("\n") + 1,
                    seg.strip().replace("\n", " ")[:110],
                )
            )
    return out


def find_drive_only_root(path: Path) -> list:
    """⇒ ``[(行号, 原文)]``：把「盘符裸串」交给 `Path()`（应写 `"<盘符>:/"`）。

    ★ 两种形态**都直接报**（不再要求 `/` 紧邻）：
      ① 字面量：`Path("D:")`
      ② **变量**：`for drive in ("D:", "E:"): … root = Path(drive)` ——
         **这才是 2026-10-01 那个真实功能 bug 的形态**（`cad_installation.py`）。
         ⚠ 中间隔着十几行才 `root / "AutoCAD 2024"`，**所以「要求 `/` 紧邻」的写法抓不到它**
         （轮 46 负例测试证明过）。

    **为什么不需要看后面怎么用**：`Path("D:")` 是「带盘符的**相对**路径」，
    语义上几乎**没有正当用途** —— 要指盘根只有 `Path("D:/")`（或 `r"D:\\"`）一种写法。
    即便有人真想存相对路径，改成 `"D:/"` 也**无害**。⇒ **报它就是对的。**
    """
    src = path.read_text(encoding="utf-8", errors="replace")
    clean = strip_comments_and_strings(src)
    # ⚠ 变量名要从未剥字符串的**原文**里取（盘符字面量本身就是字符串，剥掉就看不见了）
    drive_vars = set()
    for m in DRIVE_LITERAL_ASSIGN.finditer(src):
        name = m.group(1) or m.group(2)
        if name:
            drive_vars.add(name)
    lines = src.splitlines()
    out = []
    for m in DRIVE_ONLY.finditer(clean):
        ln = clean[: m.start()].count("\n") + 1
        out.append((ln, lines[ln - 1].strip()[:110] if ln - 1 < len(lines) else ""))
    for m in PATH_OF_VAR.finditer(clean):
        if m.group(1) not in drive_vars:
            continue
        ln = clean[: m.start()].count("\n") + 1
        out.append((ln, lines[ln - 1].strip()[:110] if ln - 1 < len(lines) else ""))
    seen, uniq = set(), []
    for ln, raw in sorted(out):
        if ln in seen:
            continue
        seen.add(ln)
        uniq.append((ln, raw))
    return uniq


#: ⚠⚠ **`x or <默认值>` 吞掉合法 `0`** —— 只有当 **默认值 ≠ 该类型的 falsy 值** 时才有害
#: ：
#: ```
#: int(x or 0)      # x==0 ⇒ 0 or 0 = 0        ⇒ 幂等 ⇒ 无害
#: float(x or 0.0)  # x==0.0 ⇒ 0.0 or 0.0=0.0  ⇒ 幂等 ⇒ 无害
#: int(x or -1)     # x==0 ⇒ 0 or -1 = **-1**  ⇒ 吞掉合法的 0 ⇒ 真 bug
#: ```
#: ★ 2026-10-01（轮 61）真机抓到实例：`sw_costing.read_cost_analysis` 写 `int(... or -1)
#: `，
#: 而 `CostingType` 真值是 **`0`** ⇒ 被吞成 **`-1`**（把「机加工」误报成「未知」）。
#: ⚠ 这与本项目**早已记录过**的「`bool(0)` 为 `False` ⇒ 不要用真假值判成功码」是**同一族
#: **。
#:
#: ⚠⚠ **本条用**基线白名单**而不是一次全绿**：实测全仓同族共 **45 处 / 11 个模块**，
#: 一次全改的风险高于收益（事实 61：批量改文件先证明只做加法；且每一处都要判断
#: 「那个成员的 0 是否有意义」）。⇒ 既有 38 处记进 `docs/falsy-zero-baseline.txt`，
#: **新增一处即红**；基线里已修掉的条目也要删（否则基线自己腐坏）。
FALSY_ZERO_PAT = re.compile(r'"(\w+)"\s*\)\s*or\s+(-?\d+(?:\.\d+)?|""|\'\')')
#: 幂等默认值 ⇒ 无害（`or` 之后结果不变）
FALSY_ZERO_OK = {"0", "0.0", '""', "''"}
FALSY_ZERO_BASELINE = ROOT / "docs" / "falsy-zero-baseline.txt"

#: ⚠ 检查③ **不扫 `tests/`** —— 理由（**实测撞出来的，不是想当然**）：
#: 它的负例测试里**必须**出现那串字面量（`int(get_com_member(a, "CostingType") or -1)`）
#: 才能证明门禁抓得到 ⇒ 扫 `tests/` 的话，**门禁会抓到自己的夹具**（2026-10-01 轮 61 实
#: 测）。
#: ⇒ 检查③ 只针对**生产取值代码**（运行时真的会调 COM 的那些）。
#: ⚠ ①（subprocess 编码）与 ②（盘根）**仍然扫 `tests/`** —— 那两类在测试里同样是真代码。
FALSY_ZERO_DIRS = ("scripts", "tools", "mcp-server", "apps/desktop")


def _strip_comments_only(text: str) -> str:
    """只去掉**注释**、保留字符串字面量（**偏移不变**，行号仍准）。

    ⚠⚠ **为什么需要它**（2026-10-01 轮 61 实测两次假阳性）：
    检查③ 的判据里**必须**出现那串模式 ——
    * 负例测试里（证明门禁抓得到）；
    * **`check_env_pitfalls.py` 自己的注释里**（解释这个坑）。
    ⇒ 不去注释的话，**门禁会抓到自己的文档与夹具**，然后为了让它变绿而去改注释 ——
      **那是把判据改坏去迁就实现**（本项目红线）。
    ⚠ 不能直接复用 `strip_comments_and_strings()`：检查③ 的**成员名本身就是字符串字面量**
      （`"CostingType"`），把字符串也去掉就什么都匹配不到了。
    """
    out = list(text)
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                (r1, c1), (r2, c2) = tok.start, tok.end
                for ln in range(r1, r2 + 1):
                    line_start = sum(len(x) + 1 for x in text.splitlines()[: ln - 1])
                    a = line_start + (c1 if ln == r1 else 0)
                    b = line_start + (
                        c2 if ln == r2 else len(text.splitlines()[ln - 1])
                    )
                    for i in range(a, min(b, len(out))):
                        if out[i] != "\n":
                            out[i] = " "
    except (tokenize.TokenError, IndentationError, SyntaxError):
        # 源码本身有语法问题时**退回原文** —— 检查①/② 会独立报出来，这里不吞不编。
        return text
    return "".join(out)


def find_falsy_zero_default(path: Path) -> list:
    """⇒ ``[(行号, 成员名, 默认值)]`` —— `get_com_member(..., "X") or <默认>` 里**有害**的那些。

    ⚠ 先在**去注释**的文本上匹配（理由见 `_strip_comments_only`）。
    """
    out = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return out
    code = _strip_comments_only(text)
    for m in FALSY_ZERO_PAT.finditer(code):
        member, default = m.group(1), m.group(2)
        if default in FALSY_ZERO_OK:
            continue
        out.append((code[: m.start()].count("\n") + 1, member, default))
    return out


def load_falsy_zero_baseline() -> set:
    """⇒ ``{"模块相对路径:成员名"}`` —— 已记账的存量（**未修的**）。"""
    if not FALSY_ZERO_BASELINE.is_file():
        return set()
    keys = set()
    for line in FALSY_ZERO_BASELINE.read_text(encoding="utf-8").splitlines():
        s = line.split("#", 1)[0].strip()
        if s:
            keys.add(s)
    return keys


#: ⚠⚠ **`keybd_event` 的「按下」必须在 `finally` 里被抬起**（2026-10-01 轮 62 加）。
#: 形态：`keybd_event(vk, 0, 0, 0)`（按下）→ `time.sleep(...)` → `keybd_event(vk, 0, KEY
#: UP, 0)`。
#: `sleep` **可被中断**（`KeyboardInterrupt` / 线程被停 / 进程退出）⇒ **抬起永远到不了**
#: ⇒ **修饰键卡在按下态**。后果（用户 2026-10-01 实报）：
#:   * **Ctrl 卡住** ⇒ 之后按 `A` 就是 `Ctrl+A` = **全选（蓝底）**
#:   * **Alt 卡住** ⇒ 菜单栏被激活、按键被吃掉
#:   * **Enter 卡住** ⇒ **忽然回车**
#: ⚠ **它不需要周期性** —— 一次事故就够，持续到用户单独按一下那个键为止。
#: ⇒ 定则：**按下与抬起必须在同一函数的 `try` / `finally` 配对里**，
#:   或改用 `sw_gui_input._press` / `_hold`（它们内部已保证抬起）。
KEYBD_EVENT = "keybd_event"
SAFE_PRIMITIVES = ("_press", "_hold", "_tap", "_tap_ctrl")


def _vk_kind(call):
    """⇒ ``"down"`` / ``"up"`` / ``None`` —— 该 `keybd_event(...)` 是按下还是抬起。"""
    flags = call.args[2] if len(call.args) > 2 else None
    if flags is None:
        return None
    if isinstance(flags, ast.Constant) and flags.value == 0:
        return "down"
    if (isinstance(flags, ast.Attribute) and flags.attr == "KEYEVENTF_KEYUP") or (
        isinstance(flags, ast.Name) and flags.id == "KEYEVENTF_KEYUP"
    ):
        return "up"
    return None


def find_unguarded_keypress(path):
    """⇒ ``[(行号, 函数名)]`` —— **按下之后没有 `finally` 保证抬起**的函数。

    豁免：函数体里调用了 `SAFE_PRIMITIVES` 里任一原语（它们自己保证抬起）。
    判据用 **AST**（不靠文本匹配）—— 文本匹配会把**注释里的示例**也算进来，
    而本文件的注释里正好写着这个坑的示例（「门禁抓到自己的文档」是实测撞过的假阳性）。
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    out = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        pushes, fin_ups, uses_safe = [], 0, False
        for node in ast.walk(fn):
            if isinstance(node, ast.Call):
                name = getattr(node.func, "attr", None) or getattr(
                    node.func, "id", None
                )
                if name in SAFE_PRIMITIVES:
                    uses_safe = True
                if name == KEYBD_EVENT and _vk_kind(node) == "down":
                    pushes.append(node.lineno)
            if isinstance(node, ast.Try):
                for sub in ast.walk(ast.Module(body=node.finalbody, type_ignores=[])):
                    if isinstance(sub, ast.Call):
                        nm = getattr(sub.func, "attr", None) or getattr(
                            sub.func, "id", None
                        )
                        if nm == KEYBD_EVENT and _vk_kind(sub) == "up":
                            fin_ups += 1
        if pushes and not uses_safe and fin_ups < len(pushes):
            out.append((pushes[0], fn.name))
    return out


def find_get_com_member_default(path: Path) -> list:
    """★ 找 `get_com_member(obj, attr, default=...)` —— ★ 这是个**静默致哑**的坑（真机踩过）✓

    ★★★ 2026-10-06 现场：★ 本仓的签名是 `get_com_member(obj, attr_name, *args)` ——
      ★ **没有 `default=` 这个关键字** ⇒ ★ 传 `default=None` 会被当成**位置实参** ⇒
      ★★ 变成「**用 `None` 去调那个成员**」⇒ 成员抛异常 ⇒ 外层拿到的全是 `None` ✓
    ★★ 它为什么特别坏：★ 读出全 `None` **不会报错** ⇒ ★ 上层把「读不到」当成「没变 / 没有」⇒
      ★ 于是 **B5 的门禁曾整整一轮"瞎着放行"**（SolidWorks 明明开着文档，而它读到 0 个）✗
    ★ 正解：★ 直接 `get_com_member(obj, attr)` —— ★ 该函数**本来就**会"先无参调一次、
      失败了再把成员本身返回" ⇒ ★ 属性和方法**都能读**（★ 真机实测：`GetDocumentCount` 是**属性**）✓
    """
    hits = []
    for ln, line in enumerate(
        path.read_text(encoding="utf-8", errors="replace").splitlines(), 1
    ):
        if "get_com_member(" not in line or "default=" not in line:
            continue
        #: ★ 按**括号配对**切出整段调用（★ 事实 58 的教训：不能按第一个 `)` 截）✓
        idx = line.find("get_com_member(")
        while idx != -1:
            seg = balanced_call(line, idx)
            if "default=" in seg:
                hits.append((ln, seg.strip()[:120]))
            idx = line.find("get_com_member(", idx + 1)
    return hits


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(
        description="环境坑静态检查（subprocess 编码 / Path 盘根）"
    )
    ap.add_argument("--root", default=str(ROOT))
    a = ap.parse_args(argv)
    root = Path(a.root)

    files = []
    for d in SCAN_DIRS:
        p = root / d
        if p.is_dir():
            files.extend(sorted(p.rglob("*.py")))
    files = [f for f in files if ".git" not in f.parts]

    #: 检查③ 专用的文件集（**排除 `tests/`**，理由见 `FALSY_ZERO_DIRS` 的注释）
    files_for_falsy_zero = [
        f
        for d in FALSY_ZERO_DIRS
        for f in [(root / d)]
        if f.is_dir()
        for f in sorted(f.rglob("*.py"))
        if ".git" not in f.parts
    ]

    enc_bad, drv_bad, gcm_bad = [], [], []
    for f in files:
        for ln, seg in find_missing_encoding(f):
            enc_bad.append((f.relative_to(root), ln, seg))
        for ln, raw in find_drive_only_root(f):
            drv_bad.append((f.relative_to(root), ln, raw))
        for ln, seg in find_get_com_member_default(f):
            gcm_bad.append((f.relative_to(root), ln, seg))

    print("环境坑静态检查 · 扫 %d 个 .py" % len(files))
    print()
    print(
        "⑤ `get_com_member(...)` 里误传 `default=`（★ 会被当位置实参 ⇒ **读出全是 None 而不报错**）"
    )
    if gcm_bad:
        print("   [FAIL] %d 处：" % len(gcm_bad))
        for f, ln, seg in gcm_bad[:20]:
            print("     %s:%d  %s" % (f, ln, seg))
    else:
        print("   [PASS] 0 处")
    print()
    print(
        "① `subprocess` 用 `text=True` 但缺 `encoding=`（**中文 Windows 上会炸**，事实 58）"
    )
    if enc_bad:
        print("   [FAIL] %d 处：" % len(enc_bad))
        for f, ln, seg in enc_bad[:20]:
            print("     %s:%d  %s" % (f, ln, seg))
    else:
        print("   [PASS] 0 处")
    print()
    print('② `Path("<盘符>:")` 当盘根用（**缺反斜杠 ⇒ 该盘上永远找不到**，事实 59）')
    if drv_bad:
        print("   [FAIL] %d 处：" % len(drv_bad))
        for f, ln, raw in drv_bad[:20]:
            print("     %s:%d  %s" % (f, ln, raw))
    else:
        print("   [PASS] 0 处")

    # ③ `x or <默认>` 吞掉合法的 0（**基线记账 + 只拦新增**；**不扫 tests/**，见 FALSY_Z
    # ERO_DIRS）
    baseline = load_falsy_zero_baseline()
    fz_all, fz_new = [], []
    for f in files_for_falsy_zero:
        for ln, member, default in find_falsy_zero_default(f):
            rel = f.relative_to(root)
            fz_all.append((rel, ln, member, default))
            if "%s:%s" % (rel.as_posix(), member) not in baseline:
                fz_new.append((rel, ln, member, default))
    fz_now = {"%s:%s" % (r.as_posix(), m) for r, _, m, _ in fz_all}
    fz_fixed = sorted(baseline - fz_now)  # 基线里已不存在 ⇒ 该删（防基线自己腐坏）
    print()
    print("③ `x or <默认值>` 吞掉合法 `0`（**默认值 ≠ falsy 值**才有害，事实 61 同族）")
    print("   存量 **%d** 处（基线记账）· **新增 %d** 处" % (len(fz_all), len(fz_new)))
    if fz_new:
        print("   [FAIL] 新增（**这是回归**）：")
        for rel, ln, member, default in fz_new[:20]:
            print("     %s:%d  %s or %s" % (rel, ln, member, default))
    else:
        print("   [PASS] 无新增")
    if fz_fixed:
        print(
            "   ⚠ 基线里 %d 条**已不存在**（修好了？）⇒ 请从 %s 删掉："
            % (len(fz_fixed), FALSY_ZERO_BASELINE.name)
        )
        for k in fz_fixed[:10]:
            print("     %s" % k)
    print()
    # ④ `keybd_event` 按下之后没有 `finally` 保证抬起（**卡住修饰键/回车**）
    kp_bad = []
    for f in files:
        for ln, fn in find_unguarded_keypress(f):
            kp_bad.append((f.relative_to(root), ln, fn))
    print()
    print(
        "④ `keybd_event` 按下后**没有 `finally` 保证抬起**"
        "（卡住 Ctrl/Alt/Enter ⇒ **忽然全选 / 忽然回车**）"
    )
    if kp_bad:
        print("   [FAIL] %d 个函数：" % len(kp_bad))
        for rel, ln, fn in kp_bad[:20]:
            print("     %s:%d  %s()" % (rel, ln, fn))
    else:
        print(
            "   [PASS] 0 个（全部走 `sw_gui_input._press` / `_hold` 或自带 `finally`）"
        )
    print()
    if enc_bad or drv_bad or fz_new or kp_bad:
        print(
            "环境坑门禁未通过：%d 项（%d + %d + %d + %d 处）"
            % (4, len(enc_bad), len(drv_bad), len(fz_new), len(kp_bad))
        )
        print(
            '  修法：① 补 `encoding="utf-8", errors="replace"`；'
            '② 写 `Path("D:/")`（或 `r"D:\\\\"`）而不是 `Path("D:")`；'
            "③ 数值取值**只有 `None` 才回落**（`v if v is not None else d`），"
            "**不要**写 `x or -1`。"
        )
        return 1
    if fz_fixed:
        # ⚠ 基线腐坏**不算硬失败**（不阻塞发布），但必须喊出来。
        print("环境坑门禁通过（⚠ 但基线待清理：见上）")
        return 0
    print("环境坑门禁通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
