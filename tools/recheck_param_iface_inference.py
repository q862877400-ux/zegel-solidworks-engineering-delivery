r"""@brief 复算：`check_member_owner_interface.py` 的**形参接口推断**推错了哪两处。

## 为什么留着它（轮 174）
轮 174 试了一条退路（`:param` 缺失时用「恰好 1 形参 + docstring 里恰好 1 个反射接口名」推形参类型），
★ **实测两处都推错** ⇒ **该退路已回退**。本脚本是**那次实测的可复算证据** ——
★ 留着它，是为了让下一个人**不必再试一遍**（事实 114 的落地）。

## 判据（可复算，只读）
```
① `check_member_owner_interface` 的 `param_ifaces_from_docstring` 对
   `sw_mold.py` 的 6 个函数各推出什么
② ★ 两处**错**必须复现出来：
   · `insert_parting_line` 等 5 个 ⇒ 推成 `Feature`（docstring 里的**散文词** `feature` 命中了接口名 `Feature`）
   · `mold_undercut_detect`      ⇒ 推成 `IFeatureManager`（docstring 提到的是**成员全名**，**不是形参类型**）
③ `mold_evidence` ⇒ docstring 里有 **6** 个接口名 ⇒ 判据**放弃**（如实：**正确地放弃**）
```

## ⚠ 安全
**纯静态**：只读反射 + 读源码；**不连 SolidWorks、不改任何文件**。

# ── 来源 ──
# 仓库:   本项目自身（把轮 174 的一次性验证收进 tools/，按门禁要求）
# 文件:   tools/recheck_param_iface_inference.py
# 定位:   复算「从 docstring 推形参接口」这条退路**为什么会错**（事实 114 的可复算证据
#           ）。
# 官方依据: `D:/AI/SW/_raw/reflect_sldworks/iface_sldworks.txt` 的 `## <Iface>` 分段
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(ROOT / "scripts"))
import check_member_owner_interface as C          # noqa: E402

def param_ifaces_from_docstring(fn, iface_names: set) -> dict:
    """★ **被回退的那条推断逻辑**（轮 174）—— **本脚本把它内联在这里，只为复算它为何错**。

    ⚠ 它**不在** `check_member_owner_interface.py` 里（那条退路**已回退**，事实 114）。
    ⇒ 本函数是**反面教材的可执行版本**，**不要**把它搬回检查器。
    """
    doc = ast.get_docstring(fn) or ""
    if not doc:
        return {}
    out: dict = {}
    blocks = re.split(r"(?m)^\s*:(?:param|return|returns|raises)\b", doc)
    for b in blocks:
        m = re.match(r"\s*(\w+)\s*:", b)
        if not m:
            continue
        pname = m.group(1)
        for cand in sorted(iface_names, key=len, reverse=True):
            if re.search(r"(?<![A-Za-z0-9_])" + re.escape(cand) + r"(?![A-Za-z0-9_])", b):
                out[pname] = cand
                break
    #: ⚠ 那条退路：没有 `:param` 时，若**恰好 1 个形参**且 docstring 里接口名**恰好 1 个
    #: ** ⇒ 采纳
    args = [a.arg for a in fn.args.args if a.arg not in ("self", "cls")]
    if len(args) == 1:
        found = sorted({c for c in iface_names
                        if re.search(r"(?<![A-Za-z0-9_])" + re.escape(c) + r"(?![A-Za-z0-9_])", doc)})
        if len(found) == 1:
            out[args[0]] = found[0]
    return out


EXPECT = {
    #: ★ 两处**已知会推错**的（轮 174 实测）
    "insert_parting_line": "Feature",
    "insert_parting_surface": "Feature",
    "insert_shut_off_surface": "Feature",
    "insert_core_cavity_solids": "Feature",
    "mold_draft_analysis": "Feature",
    "mold_undercut_detect": "IFeatureManager",
}


def main() -> int:
    ifaces = C.load_interfaces(C.REFLECT)
    names = set(ifaces.keys())
    print("  反射: %d 个接口" % len(ifaces))

    t = (ROOT / "scripts" / "sw_mold.py").read_text(encoding="utf-8")
    tree = ast.parse(t)
    got: dict = {}
    for fn in ast.walk(tree):
        if isinstance(fn, ast.FunctionDef):
            pi = param_ifaces_from_docstring(fn, names)
            if pi:
                got[fn.name] = pi
    print()
    print("  ── 推断结果 ──")
    for k in sorted(EXPECT):
        v = got.get(k, {})
        mark = "★ 已知推错" if k in EXPECT else ""
        print("    %-28s %-40s %s" % (k, v, mark))

    print()
    n_ok = 0
    for k, want in EXPECT.items():
        v = (got.get(k) or {}).get("model")
        ok = (v == want)
        n_ok += 1 if ok else 0
        print("    %s %-28s 推成 %-18s（复现预期 %s）" % ("✓" if ok else "**✗**", k, v, want))

    #: ★ `mold_evidence` 必须**放弃**（推不出 ⇒ 留白）—— 那是"正确地放弃"
    me = got.get("mold_evidence")
    print()
    print("    %s mold_evidence ⇒ %s（docstring 里接口名太多 ⇒ **正确地放弃**）"
          % ("✓" if not me else "**✗**", me if me else "{}"))

    total = len(EXPECT) + 1
    passed = n_ok + (1 if not me else 0)
    print()
    print("  ── %d/%d · %s ──" % (passed, total, "pass" if passed == total else "fail"))
    print("  ⚠ 本脚本证的是「**这条退路会推错**」，**不是**「推断正确」—— 事实 114。")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
