r"""@brief 探针：扫**直接属性访问**形态的疑似不存在 COM 成员 —— ★ 先量**假阳性率**。

## 为什么（顺 `077` 的真缺陷）
```
`sw_export.export_to_pdf` 第一行 `model.GetSldWorksObject()` —— **两套源都查不到该成员**
⇒ 那个函数**从未能运行过**。
★ 而仓库里**有一个**查成员名的门禁 `scripts/check_member_names.py`（138 行）——
  它**只认** `get_com_member` / `call_com_member` / `safe_get_com_member` 这三种**包装形态**
⇒ ★★★ **`model.GetSldWorksObject()` 是**直接属性访问** ⇒ 正好落在它的盲区里。**
```

## 本探针要回答的两个问题
```
① 全仓库 `scripts/*.py` 里，形如 `<标识符>.<PascalCase>(…)` 且**该名字不在任何接口里**的，
   还剩多少处？
② ★ 其中**假阳性**（Python 自己的对象，不是 COM）占比多少？
   ⇒ **假阳性率太高就不接门禁**（事实 74 那一族的纪律：命名/语义判据不可靠）
```

## ⚠ 只读
本探针**只读**代码与反射转储，**不连 SolidWorks**。

# ── 来源 ──
# 仓库:   本项目自身（静态探针）
# 文件:   tools/probe_direct_member_access.py
# 定位:   给 Spec Kit `078` 量「直接属性访问」这一类判据的**假阳性率**。
# 官方依据: 出厂反射 `D:\AI\SW\_raw\**\iface_*.txt`（成员名的唯一真源）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = Path(Path(__file__).resolve().parents[1] / "_raw")
OUT = Path(Path(__file__).resolve().parents[1] / "output" / "direct-member-access.json")
sys.stdout.reconfigure(encoding="utf-8")

#: `<对象>.<PascalCase>(` —— Python 里方法名习惯 snake_case，
#: 所以**首字母大写的方法调用**是可疑信号（COM 成员是 PascalCase）。
CALL = re.compile(r"\b([A-Za-z_]\w*)\.([A-Z]\w{2,})\s*\(")

#: ⚠⚠⚠ **第一版判据（"大驼峰 + 不在反射里"）实测假阳性率 ≈ 100%** ——
#: 323 处里全是 **Python 标准库 / pywin32 / OCP / winreg / argparse** 的对象
#: （`argparse.ArgumentParser` ×29 · `winreg.OpenKey` ×8 · `win32api.SetCursorPos` ×8 ·
#: …）
#: ⇒ ★ 印证**事实 74 那一族**：**「名字形态」判不出"是不是 COM 成员"** ⇒ **不接那条判据*
#: *。
#:
#: ★★ 第二版判据**有依据**（不是猜）：把对象名**限定到「已经被当作 COM 对象用过」的那些*
#: * ——
#: 即 `get_com_member(<OBJ>, …)` / `call_com_member(<OBJ>, …)` /
#: `safe_get_com_member(<OBJ>, …)` 的**第一个实参标识符**。
#: ⇒ 那些 `<OBJ>` **确实是 COM 对象** ⇒ 在它们身上的大驼峰调用就**值得查**。
COM_OBJECTS: set = set()
_WRAPPERS = {
    "get_com_member",
    "call_com_member",
    "safe_get_com_member",
    "get_com_member_raw",
}
WRAP_CALL = re.compile(
    r"\b(%s)\s*\(\s*([A-Za-z_]\w*)\s*," % "|".join(sorted(_WRAPPERS))
)


def members_from_reflection() -> set:
    """从出厂反射里收全部成员名（`iface_*.txt` 的 `成员(...)` 形态）。"""
    names: set = set()
    pat = re.compile(r"^\s*(?:[A-Za-z_][\w.<>,\[\] ]*?\s+)?([A-Z]\w{2,})\s*\(")
    for p in RAW.rglob("iface_*.txt"):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            continue
        for line in text.splitlines():
            m = pat.match(line)
            if m:
                names.add(m.group(1))
    return names


#: ⚠⚠⚠ **第三版判据**（轮 160）—— 前两版的教训都吃进来了：
#:   ① 第一版「大驼峰 + 不在反射里」⇒ 假阳性 ≈100%（标准库/pywin32/OCP 全都进来）；
#:   ② 第二版「对象名从 `get_com_member(<OBJ>, …)` 推导」把假阳性降到 12 处，
#:      但仍有 3 类噪音：**docstring 里的举例**、**COM 基础设施**（`QueryInterface`）、
#: **跨函数变量名重合**（OCP 的 `wire`/`surface` 与 COM 的 `wire`/`surface` 同名 —— 事实
#:  51）。
#: ⇒ 第三版：**(a) 用 `ast` 只查代码** · **(b) COM 对象名按「所在函数」定作用域** ·
#:            **(c) 加 COM 基础设施白名单**。
COM_INFRA = {
    "QueryInterface",
    "AddRef",
    "Release",
    "GetTypeInfo",
    "GetIDsOfNames",
    "Invoke",
}


def _scan_file(path: Path, known: set) -> list:
    """用 `ast` 扫一个文件：**同一函数内**被当 COM 对象用过的标识符，再查它们身上的大驼峰调用。"""
    #: ★ 2026-10-22 统一化：原来这里嵌着一个 4 行的 `def ident`，与
    #:   `scripts/check_member_names._base_name` 逐字相同 ⇒ 已收敛到
    #:   `scripts/ast_helpers.base_name`；此处按旧名 `ident` 导入（★ 调用点零改动）
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

    from ast_helpers import base_name as ident  # noqa: PLC0415

    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []

    out: list = []
    for fn in [
        n
        for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]:
        #: (b) **按函数**收 COM 对象名（事实 51：范围要贴合组织单元）
        com_objs: set = set()
        for sub in ast.walk(fn):
            if (
                isinstance(sub, ast.Call)
                and isinstance(sub.func, ast.Name)
                and sub.func.id in _WRAPPERS
                and sub.args
            ):
                o = ident(sub.args[0])
                if o:
                    com_objs.add(o)
        #: ★★★ **传播**（轮 160 补）：从 COM 对象**属性派生**出来的变量也算 COM 对象。
        #: ⚠ 少了这一步就会**漏检**真实代码里最常见的形态：
        #: `interference = asm_model.InterferenceDetectionManager`
        #: 然后 `interference.GetInterference(0)` ——
        #: ★ 这正是 `159` 那个真缺陷的形态，而**「能响测试」当场把它抓了出来**
        #:   （收窄修掉了假阳性，却引入了一个漏检 —— 靠负例才发现）。
        for _ in range(3):  #: 传三层足够（属性链不会很深）
            grew = False
            for sub in ast.walk(fn):
                if (
                    isinstance(sub, ast.Assign)
                    and len(sub.targets) == 1
                    and isinstance(sub.targets[0], ast.Name)
                    and isinstance(sub.value, (ast.Attribute, ast.Call))
                ):
                    src_obj = sub.value
                    if isinstance(src_obj, ast.Call):
                        src_obj = src_obj.func
                    base = src_obj
                    while isinstance(base, ast.Attribute):
                        base = base.value
                    if (
                        isinstance(base, ast.Name)
                        and base.id in com_objs
                        and sub.targets[0].id not in com_objs
                    ):
                        com_objs.add(sub.targets[0].id)
                        grew = True
            if not grew:
                break
        if not com_objs:
            continue
        #: (a) 只看**代码**（`ast` 天然不含 docstring/注释）
        for sub in ast.walk(fn):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
                o = ident(sub.func.value)
                name = sub.func.attr
                if o in com_objs and name not in known and name not in COM_INFRA:
                    out.append(
                        {
                            "file": path.name,
                            "line": getattr(sub, "lineno", 0),
                            "fn": fn.name,
                            "obj": o,
                            "name": name,
                        }
                    )
    return out


def main() -> int:
    ev: dict = {"started": "", "scanned_files": 0, "hits": []}
    known = members_from_reflection()
    print("  出厂反射里的成员名: **%d** 个" % len(known))
    if not known:
        print("  ⚠ 反射转储读不到 ⇒ **无法判定**，如实报，不接门禁")
        return 1

    rows = []
    for p in sorted((ROOT / "scripts").glob("*.py")):
        ev["scanned_files"] += 1
        rows.extend(_scan_file(p, known))
    ev["hits"] = rows
    print(
        "  扫了 **%d** 个文件 ⇒ 疑似**不存在**的大驼峰成员调用: **%d** 处"
        % (ev["scanned_files"], len(rows))
    )
    print()
    by_name: dict = {}
    for r in rows:
        by_name.setdefault(r["name"], []).append(r)
    print("  ── 按名字归并（同一个名字出现几次）──")
    for name, rs in sorted(by_name.items(), key=lambda kv: -len(kv[1]))[:18]:
        print(
            "    %-26s ×%-3d 例：%s:%s  %s"
            % (name, len(rs), rs[0]["file"], rs[0]["line"], rs[0]["text"][:60])
        )
    ev["distinct"] = {k: len(v) for k, v in by_name.items()}
    print()
    print("  ⚠ **下一步必须人工判这几类的假阳性率**（它们是不是 Python 自己的对象）：")
    print("     判据：这个 `<对象>` 是不是 COM 对象？若不是 ⇒ **假阳性**。")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
