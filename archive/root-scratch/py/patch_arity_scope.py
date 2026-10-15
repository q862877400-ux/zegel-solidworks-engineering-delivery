"""修两件事：① 我自己的 `GetStudy` arity 错；② arity 审计**扩到 `tools/`**（真实盲区）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（一次性补丁，非第三方移植）
# 文件:   D:\\AI\\SW\\patch_arity_scope.py
# 定位:   2026-10-01 的发现链：
#           · 我写 `audit_runtime_reachability.py` 时把 `GetStudy(Int32)` 传成
#             `GetStudy(0, out_i4())`（两个参数）⇒ COM 报 `'无效的参数数目'`；
#           · **`scripts/audit_call_arity.py` 没抓到它** —— 因为**它只审 `scripts/`**；
#           · 而 `tools/` 里有 **3 个文件 / 35 处 COM 调用**（三个证据脚本 + 本审计工具）。
#         **⇒ 这是真实盲区：COM 调用分散在两处，门禁只覆盖一处。**
#         **⇒ 「项目自己的代码全对、错的是新写的那处」** 这个模式，正是门禁该防的。
# 官方签名依据: `CWStudy GetStudy(Int32)`（反射 + `C:\\cworks_vb6` CHM 一致）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TOOL = Path(r"C:\swprojects\sw-skill-fork\tools\audit_runtime_reachability.py")
ARITY = Path(r"C:\swprojects\sw-skill-fork\scripts\audit_call_arity.py")


def fix_getstudy() -> int:
    t = TOOL.read_text(encoding="utf-8")
    # 容忍任意缩进的替换
    pat = re.compile(r'get_com_member\(mgr, "GetStudy", 0, out_i4\(\)\)')
    if not pat.search(t):
        print("  ✗ 未找到 GetStudy 调用")
        return 1
    t = pat.sub('get_com_member(mgr, "GetStudy", 0)  # CWStudy GetStudy(Int32) —— 只一个参数', t, count=1)
    # 顺手把那条误导性的注释也改掉
    t = t.replace("# `GetStudy(Int32, Int32&) -> CWStudy`（ICWStudyManager）",
                  "# `CWStudy GetStudy(Int32)` —— **只一个参数**（反射与 CHM 一致）")
    TOOL.write_text(t, encoding="utf-8")
    print("  ✓ GetStudy 已改为 1 个参数")
    return 0


def extend_arity_scope() -> int:
    """给 arity 审计加 `--all`：一次审 `scripts/` + `tools/`。

    ⚠ 不改默认行为（保持「传什么审什么」），加一个**显式的全量开关** ——
    这样既能单文件调试，也能一键查全。
    """
    t = ARITY.read_text(encoding="utf-8")
    old = '''    if len(sys.argv) < 3:'''
    if old not in t:
        print("  ⚠ 未匹配 arity 审计的 argv 段（跳过 ②）")
        return 0
    new = '''    # ⚑ 2026-10-01 加：`--all` 一次审 `scripts/` + `tools/`。
    #   起因：`tools/` 里有 3 个文件 / 35 处 COM 调用**不在本工具的覆盖内**，
    #   而我新写的一个工具因此带着 `GetStudy` 的 arity 错进了仓库。
    #   **⇒ COM 调用分散在两处，门禁必须两处都覆盖。**
    if "--all" in sys.argv:
        import glob as _glob
        targets = (sorted(_glob.glob(str(ROOT / "scripts" / "*.py")))
                   + sorted(_glob.glob(str(ROOT / "tools" / "*.py"))))
        sigs = [a for a in sys.argv[1:] if a != "--all"]
        if not sigs:
            print("用法: python scripts/audit_call_arity.py --all <iface_*.txt> [...]")
            raise SystemExit(2)
        bad_total = 0
        for _t in targets:
            _ok, _doubt, _missing, _dyn = audit(_t, sigs)
            if _doubt or _missing:
                print("%s\\n  pos=%d doubt=%d missing=%d"
                      % (_t, _ok, len(_doubt), len(_missing)))
                for row in (_doubt + _missing)[:6]:
                    print("    %s" % (row,))
                bad_total += len(_doubt) + len(_missing)
        print()
        print("全量（scripts/ + tools/）: 有问题 %d 处" % bad_total)
        raise SystemExit(0 if bad_total == 0 else 1)

    if len(sys.argv) < 3:'''
    t = t.replace(old, new, 1)
    ARITY.write_text(t, encoding="utf-8")
    print("  ✓ arity 审计已加 `--all`（scripts/ + tools/）")
    return 0


def main() -> int:
    rc = fix_getstudy()
    extend_arity_scope()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
