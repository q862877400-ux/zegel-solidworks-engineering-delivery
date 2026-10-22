"""★ 门禁：**写 COM 属性必须用 `set_com_member`**，不能用 `get_com_member`（它会去"调用"属性）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（门禁）
# 文件:   tools/check_com_write_form.py
# 定位:   ★ 2026-10-03（轮 468）★ 承用户那句「**逐个看逐个修**」。
#   ★★★ **本门禁判的是一条本仓自己早就定下的规矩**：
#     `scripts/sw_connect.py` 的 `set_com_member` docstring 原话（★ 逐字引）：
#     > ⇒ 与已知事实 4（读用 `get_com_member`）成对：**读走 `get_com_member`，写走本函数。**
#   ★★ 而**规矩没被遵守**的地方有一批：本仓有 20+ 处用 `get_com_member(obj, "<属性>", 值)`
#     去**写**属性 ⇒ ★★★ `get_com_member(obj, name, *args)` 的语义是「取或**调**」：
#     **有实参就一定调用** ⇒ ★ 它在一个 `bool` / `tuple` 上"调用" ⇒
#     `TypeError: 'bool' object is not callable` ⇒ ★★ **而外面 `return True`** ⇒
#     ★★★ **失败被报成成功**（★ `set_view_scale` 是同一族，只是值类型是 tuple）。
#   ★ **真机证据（2026-10-03，轮 468）**：`ISldWorks.CommandInProgress` ·
#     `ISelectionMgr.EnableSelection` · `ISelectionMgr.EnableContourSelection`
#     三个**全报** `TypeError: 'bool' object is not callable`
#     ⇒ ★ 而 `CommandInProgress` **正是铁律 2 点名的那个保护**
#       （"先置 `ISldWorks.CommandInProgress = True` … 是无人值守挂起的头号原因"）
#       ⇒ ★★ **那道保护从来没生效过**。
#   ★★★ **判据（可静态判，因为官方源里有 `kind: property`）**：
#     ```
#     ★ 扫全部 `get_com_member(<obj>, "<Name>", <至少一个实参>)` 调用；
#     ★ 若 `<Name>` 在 `C:\\swapi\\types\\**\\<Name>.md` 里 `kind: property`
#       ⇒ ★ **报**（写属性走了读/调 helper）✓
#     ★ 名字在官方源里查不到 ⇒ **不报**（★ 交给 `check_member_names.py`，铁律 5 不猜）
#     ```
# ⚠ **白名单**：本仓少数地方**故意**用 `get_com_member` 传实参去**调方法**（那是**对的**
# ）——
#     本门禁只报 **`kind: property` 的**，方法与"查不到"都放过 ✓
#   ⚠ **它自己有负例自证**：`tests/test_com_write_form_gate.py`（事实 62）。
# 官方依据: `C:\swapi\types\**\*.md` 的 `kind:` 字段（property / method）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   `scripts/**` · `tools/**` · `tests/**` · `mcp-server/**` 的 `.py`。
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 见上。

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
SWAPI = Path(r"C:\swapi")
OUT = R / "output" / "com-write-form-scan.json"
#: ★ 本门禁自己 + 旧扫描器不扫（★ 它们的字符串常量里会出现"调用字面量"）
SKIP_FILES = ("check_com_write_form", "scan_blind_criteria")


def property_names() -> set:
    """⇒ 官方源里 `kind: property` 的成员名（小写）。"""
    props = set()
    t = SWAPI / "types"
    if not t.is_dir():
        return props
    for d in t.iterdir():
        if not d.is_dir():
            continue
        try:
            for f in d.iterdir():
                if f.suffix != ".md" or f.name == "_overview.md":
                    continue
                head = f.read_text(encoding="utf-8", errors="replace")[:400]
                if "kind: property" in head:
                    props.add(f.stem.lower())
        except OSError:
            pass
    return props


def main() -> int:
    props = property_names()
    print("  官方源里 `kind: property` 的成员：**%d** 个" % len(props))
    if not props:
        print("  [SKIP] 官方源 `C:\\swapi\\types` 不可达 ⇒ 本门禁跳过（便携性守卫）")
        return 0
    res = {"_": "写 COM 属性却用 get_com_member（★ 它会去“调用”属性 ⇒ TypeError ⇒ 而常被 return True 掩盖）",
           "property_count": len(props), "hits": []}
    scanned = 0
    for sub in ("scripts", "tools", "tests", "mcp-server"):
        d = R / sub
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.py")):
            if any(s in p.stem for s in SKIP_FILES):
                continue
            try:
                src = p.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(src)
            except Exception:                                     # noqa: BLE001
                continue
            scanned += 1
            #: ★★★ 2026-10-03（轮 470）**判据要与"读 / 写的真实区别"对齐** ——
            #:   ★ 本门禁原判据只有一条：「名字在官方源里是 `kind: property`，且传了实参」
            #:   ⇒ ★★ **过宽**：它把**合法的「读」也报了**（★ 实测 4 处假阳性：
            #:     `sw_equation.py` 的 `get_com_member(mgr, "Equation", i)`（**索引属性**，
            #: `i` 是**下标**）· `sw_assembly.py` 的 `MateEntityType` / `MateComponentNa
            #: me`（同）·
            #: `sw_custom_property.py` 的 `CustomPropertyManager`（★ 官方那是**方法**，
            #: 收配置名））。
            #:   ★★ 而"读"与"写"在代码里的区别**就是**：**返回值用不用** ——
            #:     依据是本仓 `sw_connect.set_com_member` 的 docstring（逐字）：
            #: > 与已知事实 4（读用 `get_com_member`）成对：**读走 `get_com_member`，写
            #: 走本函数。**
            #:   ⇒ ★ 故加第二条判据：★ **返回值被使用 ⇒ 那是读 ⇒ 放过**；
            #:     ★ **返回值被丢掉（`ast.Expr`）⇒ 那是写 ⇒ 报** ✓
            #:   ⚠ 这与我在轮 470 找"过度替换"时用的判据**是同一条** —— ★ 现在它进了门禁，
            #:     不再只活在我的临时脚本里（★ 事实 61 定则④："写了一个好用的工具函数，
            #:     就要在**所有**同类场合用它"）。
            ret_used = set()
            for x in ast.walk(tree):
                if isinstance(x, ast.Call):
                    ret_used.add(id(x))
            for x in ast.walk(tree):
                if isinstance(x, ast.Expr) and isinstance(x.value, ast.Call):
                    ret_used.discard(id(x.value))
            for n in ast.walk(tree):
                if not isinstance(n, ast.Call):
                    continue
                nm = getattr(n.func, "id", None) or getattr(n.func, "attr", None)
                if nm != "get_com_member":
                    continue
                #: ★ 第 2 个实参 = 成员名；★ **有第 3 个实参** ⇒ 进了"取或调"那条路
                if len(n.args) < 3:
                    continue
                a1 = n.args[1]
                if not (isinstance(a1, ast.Constant) and isinstance(a1.value, str)):
                    continue
                name = a1.value
                if name.lower() not in props:
                    continue
                #: ★★ 第二条判据：**返回值被使用 ⇒ 那是"读"（或带参的调用）⇒ 不是"写"** 
                #: ⇒ 放过
                if id(n) in ret_used:
                    continue
                res["hits"].append({
                    "file": str(p.relative_to(R)).replace("\\", "/"),
                    "line": n.lineno, "member": name,
                    "why": "**%s** 在官方源里是 `kind: property` ⇒ 这里在**写**它（★ 返回值被丢掉），"
                           "而 `get_com_member` 有实参就**调用** ⇒ `TypeError: '...' object is not callable`"
                           "（★ 且调用方常 `return True` ⇒ 失败被报成成功）" % name})
    res["files_scanned"] = scanned
    res["count"] = len(res["hits"])
    res["hits"].sort(key=lambda x: (x["file"], x["line"]))
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("  扫了 %d 个 .py" % scanned)
    if res["hits"]:
        print()
        print("  [FAIL] **%d** 处用 `get_com_member` 写了官方源里的**属性**：" % res["count"])
        for h in res["hits"][:40]:
            print("    · %s:%d  `%s`" % (h["file"], h["line"], h["member"]))
        if res["count"] > 40:
            print("    …（共 %d 处，全表见产物）" % res["count"])
        print()
        print("  修法：把那一处改成 `set_com_member(obj, \"%s\", 值)` ——" % res["hits"][0]["member"])
        print("        ★ 那是本仓 `sw_connect.set_com_member` 的 docstring 写明的")
        print("          「**唯一被真机验证通过的形态**：属性赋值」。")
        print("        ★ 改完**回读一次**确认值真变了（规则 6：不静默成功）。")
        return 1
    print("  [PASS] 0 处 —— 没有「写属性走 get_com_member」的情况")
    print()
    print("  ⚠ 覆盖边界：本门禁只判**官方源标了 `kind: property`** 的成员；")
    print("    名字查不到的交 `check_member_names.py`（铁律 5：不猜）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
