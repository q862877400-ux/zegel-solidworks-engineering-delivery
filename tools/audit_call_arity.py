#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""COM 调用 arity 自动比对（不猜宿主接口，只判「有没有这种形状的成员」）。

要解决的问题
------------
工程图子技能里所有 COM 访问都走 ``_safe_member(obj, "Name", *args)`` 包装。
好处是单个成员缺席不会整体崩，**坏处是签名错了也不会报错，只会静默无效果**——
这正是 AGENTS.md 铁律 2 要防的情况。手工逐个比对 70+ 个调用点不现实，故自动化。

判定口径（刻意保守，不猜宿主接口）
--------------------------------
对每个调用点 ``_safe_member(obj, "Member", a, b, c)``：

- **通过** —— ``sldworks.dll`` 中**至少有一个接口**声明了同名成员，
  且该成员的参数个数与实参个数一致。
- **存疑** —— 同名成员存在，但**所有**同名成员的参数个数都与实参个数不符。
  ⇒ 几乎必然是错的，列出该成员在各接口上的真实 arity 供人工确认。
- **查不到** —— 全程序集都没有这个成员名。

不按「宿主接口」判定，是因为调用点的 ``obj`` 变量名无法静态确定类型；
而「全库没有任何这种形状」是**不需要知道宿主也能判定**的强信号。

⚠ 本工具只做文本/元数据比对，不导入任何 CAD 模块、不连接 SolidWorks、
  不执行任何 COM 调用（见 AGENTS.md 铁律 2）。

用法
----
    python audit_call_arity.py <目标.py> <iface_*.txt> [...]
"""
from __future__ import annotations

import ast
import io
import re
import sys
from collections import defaultdict
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass

SAFE_MEMBER = re.compile(r"^(?:_safe_member|get_com_member)\s*\(")
IFACE_HEAD = re.compile(r"^##\s+(\w+)\s*$")
IFACE_SIG = re.compile(r"^\s+(\S+)\s+(\w+)\((.*)\)\s*$")


def load_signatures(paths):
    """{成员名: {参数个数: [接口.签名, ...]}}"""
    table: dict[str, dict[int, list[str]]] = defaultdict(lambda: defaultdict(list))
    for path in paths:
        current = None
        for raw in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
            head = IFACE_HEAD.match(raw)
            if head:
                current = head.group(1)
                continue
            sig = IFACE_SIG.match(raw)
            if sig and current:
                ret, name, params = sig.groups()
                if name.startswith("get_") or name.startswith("set_"):
                    name = name[4:]
                count = 0 if not params.strip() else len(params.split(","))
                table[name][count].append(f"{current}.{name}({params.strip()}) -> {ret}")
    return table


def call_sites(path):
    """用 AST 精确取 _safe_member / get_com_member 调用点：行号、成员名、实参数。"""
    src = Path(path).read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src)
    rows = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
        if name not in {"_safe_member", "get_com_member"}:
            continue
        args = node.args
        if len(args) < 2:
            continue
        member_node = args[1]
        if not (isinstance(member_node, ast.Constant) and isinstance(member_node.value, str)):
            continue
        # ⛔ 含 *args / **kwargs 解包时，AST 只能数到「1 个 Starred 节点」，
        #   真实实参个数在运行期才确定。这类调用点**无法静态判定 arity**，
        #   必须跳过，否则会把 get_com_member(o, "M", *args4) 误报成 arity=1。
        #   宁可漏报也不误报 —— 误报会让人去改本来正确的代码。
        if any(isinstance(a, ast.Starred) for a in args[2:]):
            rows.append((node.lineno, name, member_node.value, None))
            continue
        rows.append((node.lineno, name, member_node.value, len(args) - 2))
    return sorted(rows)


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    target = sys.argv[1]
    table = load_signatures(sys.argv[2:])
    rows = call_sites(target)

    ok, doubt, missing, dynamic = [], [], [], []
    for lineno, fn, member, argc in rows:
        if argc is None:
            dynamic.append((lineno, member, fn))
        elif member not in table:
            missing.append((lineno, member, argc, fn))
        elif argc in table[member]:
            ok.append((lineno, member, argc))
        else:
            doubt.append((lineno, member, argc, sorted(table[member].items())))

    print(f"目标: {target}")
    print(f"签名源: {', '.join(Path(p).name for p in sys.argv[2:])}")
    print(f"调用点: {len(rows)} 个（{len({m for _, _, m, _ in rows})} 个不同成员）\n")
    print(f"  通过     {len(ok)}")
    print(f"  存疑     {len(doubt)}   ← 同名成员存在但 arity 全对不上")
    print(f"  查不到   {len(missing)}")
    print(f"  动态     {len(dynamic)}   ← 含 *args 解包，静态不可判定，需人工核对\n")

    if doubt:
        print("── 存疑明细 ──")
        for lineno, member, argc, variants in doubt:
            print(f"  {target}:{lineno}  {member}() 实参 {argc}")
            for arity, sigs in variants:
                print(f"        官方 arity={arity}  例: {sigs[0][:96]}")
        print()
    if missing:
        print("── 查不到明细 ──")
        for lineno, member, argc, fn in missing:
            print(f"  {target}:{lineno}  {member}() 实参 {argc}  经 {fn}()")
        print()
    if dynamic:
        print("── 动态实参（需人工核对）──")
        for lineno, member, fn in dynamic:
            print(f"  {target}:{lineno}  {member}(*args)  经 {fn}()")
        print()
    return 1 if (doubt or missing) else 0


if __name__ == "__main__":
    raise SystemExit(main())
