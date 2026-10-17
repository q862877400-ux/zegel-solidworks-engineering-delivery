"""★ T1-4：把采纳的别名按 D-2 **只追加**一行进那 10 个工具的 `doc`（不动 schema 契约、可回退）。"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
MCP = ROOT / "mcp-server"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

final = json.loads((ROOT / "output" / "t1-alias-final.json").read_text(encoding="utf-8"))
ADOPT = {x["tool"]: x for x in final["same"]}
#: ★ 别名文本 = 该工具自己的 op + keys（★ 与增益实测同一批词）
cand = json.loads((ROOT / "output" / "t1-alias-candidates.json").read_text(encoding="utf-8"))
alias_of: dict = {}
for k in cand["kept"]:
    if k["tool"] in ADOPT:
        a = alias_of.setdefault(k["tool"], {"ops": set(), "keys": set()})
        a["ops"].add(k["op"])
        a["keys"] |= set(k["keys"])

MARK = "★ 别名:"


def patch(path: Path, tool: str, alias_text: str) -> str:
    """★ 把别名拼到 `doc=` 值**最后一个字符串字面量的末尾**。

    ★★ 为什么不是"在 doc 值之后插一行"（我第一版的做法）：
      隐式拼接的 doc 值**后面可能还跟着别的关键字实参** ⇒ 插一行字符串会变成
      【位置实参】⇒ `SyntaxError: positional argument follows keyword argument` ✓
      （★ 本脚本第一次跑就把 `tool_specs_batch25.py` 写坏了，靠脚本内的 `ast.parse` 自检当场抓到，
        已用 `git checkout --` 恢复）
    ★ 现在这个做法**只延长一个已有字符串字面量** ⇒ 不可能改变语法结构 ✓
    """
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    lines = src.splitlines(keepends=True)
    #: ★ 取 doc 值的最后一段字面量的位置
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        kw = {k.arg: k.value for k in node.keywords if k.arg}
        nm = kw.get("name")
        if not (isinstance(nm, ast.Constant) and nm.value == tool):
            continue
        doc = kw.get("doc")
        if doc is None:
            return "没有 doc="
        if MARK in "".join(lines[doc.lineno - 1:doc.end_lineno]):
            return "已有别名行"
        last = doc.end_lineno                     #: ★ 值结束所在行（1 基）
        #: ★★ 实测定准（`tools/_probe_doc_span.py` 量的）：
        #:   该行形如 `            "...model).",` —— `end_col_offset` **指向逗号之后**
        #:   ⇒ `end_col-3` 是值的末字符、`end_col-2` 是**闭合引号**、`end_col-1` 是逗号。
        #:   ⇒ 要插在**引号之前** ⇒ 正确列 = `end_col_offset - 2` ✓
        #: ★ 我前两版分别用「值之后插一行」与 `-1`，**两次都插到 doc 值外面**
        #:   （一次在关键字之后、一次夹在引号与逗号之间）⇒ 都变成位置实参 ⇒ 语法错。
        #:   ★ 两次都被脚本内的 `ast.parse` 自检当场抓到，并用 `git checkout --` 恢复 ✓
        lastcol = doc.end_col_offset
        raw = lines[last - 1]
        #: ★★★ `col_offset` / `end_col_offset` 是【**UTF-8 字节**】偏移，**不是字符下标** ——
        #:   这些行里有 `★` 与汉字（各 3 字节）⇒ 直接当下标会越界/错位 ✓
        #:   ⇒ 先把字节前缀解回字符，取长度才是字符下标。
        end_idx = len(raw.encode("utf-8")[:max(0, lastcol)].decode("utf-8", "ignore"))
        #: ★★★ 然后**往左扫**找闭合引号 —— 不硬算 `-1/-2`：
        #:   `end_col_offset` 的确切落点依赖「是否含逗号/换行」等约定，
        #:   ★ 我先后用过「值之后插一行」「-1」「-2」三种写法，**每次都差一点**；
        #:   ⇒ 改成扫描：跳过逗号与空白后，遇到的就该是闭合引号 ✓（与偏移约定无关）
        j = min(end_idx, len(raw))
        while j > 0 and raw[j - 1] in " \t,":
            j -= 1
        #: ★★ 守卫：扫到的必须是引号，否则**拒绝写入**（让这类错误不可能发生）
        if j == 0 or raw[j - 1] not in "\"'":
            return "★ 拒绝写入：左扫未找到闭合引号（实测 %r）" % (raw[max(0, j - 2):j],)
        char_idx = j - 1                                  #: ★ 闭合引号的位置
        #: ★ 在值结束处插入 `" ★ 别名: …"` —— 只延长字面量序列
        #: ★★ 插入点已在**字符串内容里面**（`char_idx` 就是闭合引号的位置）
        #:   ⇒ 插入的是**内容**，**不能再带外层引号**（否则变成嵌套引号 ⇒ 语法错）✓
        ins = " %s %s" % (MARK, alias_text)
        lines[last - 1] = raw[:char_idx] + ins + raw[char_idx:]
        path.write_text("".join(lines), encoding="utf-8")
        ast.parse(path.read_text(encoding="utf-8"))    #: ★ 立刻语法自检（写坏就抛，配合 git checkout 恢复）
        return "已追加（延长末段字面量）"
    return "没找到该 ToolSpec"


done, skip = [], []
for tool, x in sorted(ADOPT.items()):
    a = alias_of.get(tool, {"ops": set(), "keys": set()})
    alias_text = ", ".join(sorted(a["ops"] | a["keys"]))
    #: ★ 在 mcp-server/tool_specs_batch*.py 里找声明该工具的那个文件
    hit = None
    for f in sorted(MCP.glob("tool_specs_batch*.py")):
        if ('"%s"' % tool) in f.read_text(encoding="utf-8"):
            hit = f
            break
    if hit is None:
        skip.append((tool, "没找到声明文件"))
        continue
    r = patch(hit, tool, alias_text)
    (done if r == "已追加" else skip).append((tool, "%s · %s" % (hit.name, r)))

print("★ 采纳 %d 条 ⇒ 改了 %d 个文件，跳过 %d" % (len(ADOPT), len(done), len(skip)))
for t, w in done:
    print("   ✓ %-42s %s" % (t.removeprefix("solidworks_"), w))
for t, w in skip:
    print("   ✗ %-42s %s" % (t.removeprefix("solidworks_"), w))
