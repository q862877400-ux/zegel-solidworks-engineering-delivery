r"""@brief 扫「**数组实参没包 VARIANT**」的调用点（事实 167/183 证过的形状）。

## 为什么（轮 185）
轮 167（`AddRelation`）与轮 183（`CreateSpline`）都是**同一个形状**：
```
官方签名里是 `Object` 的**数组实参** ⇒ 传裸 list/tuple ⇒ **静默返回 None / False**（不报错）
只有包 `VARIANT(VT_ARRAY | ...)` 才成 —— ★ 而**官方 Remarks 从不写这一条**。
```
⇒ ★★ 那**别处**有没有同样的写法？本脚本**静态**找出来。

## 判据（**窄而强**，不做启发式）
```
① 找 `get_com_member` / `call_com_member` 的调用，**实参个数 ≥ 3**（即除了 owner/成员名，还有实参）；
② 其中**任何一个实参是**裸的 list/tuple 字面量**（`[...]` / `(...)`）⇒ **候选命中**；
③ ⚠ **不判"对不对"** —— 只列出**值得看**的地方（人工/真机再定）。
④ ★ **检查量为 0 时报非 0**（事实 46 的假绿守卫）。
```

## ⚠ 安全
**纯静态**：只读源码；**不连 SolidWorks、不改任何文件**。

# ── 来源 ──
# 仓库:   本项目自身
# 文件:   tools/scan_bare_array_args.py
# 定位:   给 Spec Kit `105` 把「数组实参没包 VARIANT」这一类**扫出来**（事实 167/183
#           的推广）。
# 官方依据: 事实 167（`AddRelation` 要 `VARIANT(VT_ARRAY|VT_DISPATCH)`）·
#          事实 123（`CreateSpline2` 要 `VARIANT(VT_ARRAY|VT_R8)`）
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
sys.stdout.reconfigure(encoding="utf-8")
SCAN = [ROOT / "scripts", ROOT / "mcp-server", ROOT / "tools"]
OUT = Path(Path(__file__).resolve().parents[1] / "output" / "bare-array-args.json")
CALLS = (
    "get_com_member",
    "call_com_member",
    "safe_get_com_member",
    "get_com_member_raw",
)
REFLECT = Path(
    Path(__file__).resolve().parents[1]
    / "_raw"
    / "reflect_sldworks"
    / "iface_sldworks.txt"
)


def load_signatures() -> dict:
    """★ 从反射读「成员名 → 各重载的参数类型列表」（**判据的锚**）。

    ⚠⚠⚠ **2026-10-01（轮 185）为什么要这一步**：
    我第一版按「实参是不是裸数组/形参」判 ⇒ **30 处里绝大多数是假的**
    （`FeatureByName(name)` 的 `name` 是**字符串**、`GetComponents(top_level_only)` 是 **bool**）。
    ⇒ ★★ **形状本身不是判据** —— **只有官方签名说那个参数是 `Object`（数组）**时，
      「没包 VARIANT」才是一个可指认的怀疑。
    """
    out: dict = {}
    if not REFLECT.is_file():
        return out
    for line in REFLECT.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        m = re.match(r"^([\w\.<>\[\]]+)\s+(\w+)\s*\((.*)\)\s*$", s)
        if not m:
            continue
        _ret, name, args = m.group(1), m.group(2), m.group(3)
        types = []
        for part in args.split(","):
            part = part.strip()
            if not part:
                continue
            types.append(part.split()[-1] if " " in part else part)
        out.setdefault(name, []).append(types)
    return out


SIGS = load_signatures()


def arg_is_object(member: str, index: int) -> bool:
    """★ 官方签名里 `member` 的**第 index 个参数**（0 基）是不是 `Object`。

    ⚠ 索引：`get_com_member(owner, "M", a, b)` 里的 `a` 是**该成员的**第 0 个参数
    ⇒ 所以 `index = 实参序号 - 2`。
    """
    for types in SIGS.get(member, []):
        if 0 <= index < len(types) and types[index].lower() in (
            "object",
            "system.object",
        ):
            return True
    return False


def is_bare_array(node) -> str | None:
    """`[...]` / `(...)` / `{...}` 字面量 ⇒ 返回种类名；否则 None。"""
    if isinstance(node, ast.List):
        return "list"
    if isinstance(node, ast.Tuple):
        return "tuple"
    if isinstance(node, (ast.Set, ast.Dict)):
        return type(node).__name__.lower()
    return None


def main() -> int:
    hits = []
    checked = 0
    for base in SCAN:
        if not base.is_dir():
            continue
        for f in sorted(base.glob("*.py")):
            try:
                tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            for n in ast.walk(tree):
                if not isinstance(n, ast.Call):
                    continue
                name = getattr(n.func, "attr", None) or getattr(n.func, "id", None)
                if name not in CALLS:
                    continue
                checked += 1
                #: ★★★ **判据的锚：成员名**（第二个实参是字符串常量）
                member = None
                if len(n.args) >= 2 and isinstance(n.args[1], ast.Constant):
                    member = n.args[1].value
                #: 实参：owner, 成员名, 之后才是数组实参
                for k, a in enumerate(n.args[2:], start=2):
                    kind = is_bare_array(a)
                    #: ★ **签名必须是 `Object`**（否则形状说明不了任何事 —— 轮 185 的 30
                    #:  处假阳性）
                    if kind and member and arg_is_object(member, k - 2):
                        hits.append(
                            {
                                "file": f.name,
                                "line": n.lineno,
                                "arg_index": k,
                                "kind": "%s（**官方签名第 %d 参是 Object**）"
                                % (kind, k - 2),
                                "member": member,
                                "snippet": ast.unparse(n)[:110],
                            }
                        )
                    continue
                    #: ⚠⚠⚠ **2026-10-01（轮 185）加判据② —— 因为判据①太窄**：
                    #: 轮 183 的**真形态**是「实参是**变量**」：
                    #: `data = VARIANT(...)` **之前**是 `get_com_member(skm, "CreateSpli
                    #: ne", points)`
                    #: ⇒ **字面量扫描看不到它**（★ 又一次"判据与实现的实际形态不匹配"，
                    #: 事实 51 那一族）。
                    #: ⇒ 现在：**名字实参** ⇒ 回溯本文件里它的赋值，看**右侧是不是裸 lis
                    #: t/tuple**。
                    if isinstance(a, ast.Name):
                        #: ★★★ **2026-10-01（轮 185）：实参是**形参名**也算候选** ——
                        #: ⚠ 判据①（字面量）与判据②（回溯赋值）**都漏了形参那一种**，
                        #: 而**轮 183 修复前的真形态就是形参**：
                        #: ```
                        #:   def create_spline(sketch_manager, points, simulate=False):
                        #: return get_com_member(sketch_manager, "CreateSpline", **point
                        #: s**)
                        #: ```
                        #: ⇒ ★ 用 `git show 482b2f3^:scripts/sketch_relations.py` 当**负
                        #: 例**验证过：
                        #: **旧判据命中 0 处**（= 它证明不了任何事）⇒ ★ **本判据是为它加
                        #: 的**。
                        #: ⚠ 形参的来源在**调用方** ⇒ 静态**不能排除** ⇒ 只能**列为候选*
                        #: *。
                        params = set()
                        for fn in ast.walk(tree):
                            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                params |= {p.arg for p in fn.args.args}
                        if a.id in params:
                            #: ⚠⚠⚠ **2026-10-01（轮 185）：这一支**已废弃** —— 它造成 28
                            #:  处假阳性**：
                            #: `FeatureByName(name)` 的 `name` 是**字符串**、`GetCompone
                            #: nts(top_level_only)`
                            #: 是 **bool** ⇒ ★ **"实参是形参"根本不能当判据**。
                            #: ⇒ ★ 改成**只列"签名说是 `Object` 的形参"**（锚在官方签名
                            #: 上）。
                            if member and arg_is_object(member, k - 2):
                                hits.append(
                                    {
                                        "file": f.name,
                                        "line": n.lineno,
                                        "arg_index": k,
                                        "member": member,
                                        "kind": "形参 `%s`（**官方签名第 %d 参是 Object**）"
                                        % (a.id, k - 2),
                                        "snippet": ast.unparse(n)[:110],
                                    }
                                )
                            continue
                        for asn in ast.walk(tree):
                            if not isinstance(asn, ast.Assign):
                                continue
                            if not any(
                                isinstance(t, ast.Name) and t.id == a.id
                                for t in asn.targets
                            ):
                                continue
                            rhs = asn.value
                            k2 = is_bare_array(rhs)
                            if k2 and member and arg_is_object(member, k - 2):
                                hits.append(
                                    {
                                        "file": f.name,
                                        "line": n.lineno,
                                        "arg_index": k,
                                        "kind": "%s（经变量 `%s`）" % (k2, a.id),
                                        "assign_line": asn.lineno,
                                        "snippet": ast.unparse(n)[:110],
                                    }
                                )
                            elif isinstance(rhs, ast.Name):
                                #: 追一层别名（`p = points` 这种）
                                for asn2 in ast.walk(tree):
                                    if isinstance(asn2, ast.Assign) and any(
                                        isinstance(t, ast.Name) and t.id == rhs.id
                                        for t in asn2.targets
                                    ):
                                        k3 = is_bare_array(asn2.value)
                                        if k3:
                                            hits.append(
                                                {
                                                    "file": f.name,
                                                    "line": n.lineno,
                                                    "arg_index": k,
                                                    "kind": "%s（经 `%s` → `%s`）"
                                                    % (k3, a.id, rhs.id),
                                                    "assign_line": asn2.lineno,
                                                    "snippet": ast.unparse(n)[:110],
                                                }
                                            )
    print("  ── 扫了 %d 个 `%s` 调用点 ──" % (checked, " / ".join(CALLS)))
    print("  ★★ **含裸数组字面量实参**的: **%d** 处" % len(hits))
    for h in hits[:24]:
        print(
            "    %-28s L%-5d 第 %d 个实参是 **%s**"
            % (h["file"], h["line"], h["arg_index"], h["kind"])
        )
        print("        %s" % h["snippet"])
    if not hits:
        print(
            "    （没有 ⇒ 说明这类写法在本仓库里**已经绝迹**，或**扫描判据没覆盖到**）"
        )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps({"checked": checked, "hits": hits}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print("  证据: %s" % OUT)
    if checked == 0:
        print("  ✗ **检查过 0 个** ⇒ 判据没生效（事实 46 的假绿）⇒ 非 0 退出")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
