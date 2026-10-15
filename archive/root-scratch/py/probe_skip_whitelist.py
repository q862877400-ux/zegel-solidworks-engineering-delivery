r"""@brief 门禁第四层（`skipped` 的合法性）的负例 —— 独立文件，避开 `python -c` 的转义坑。

# ── 来源 ──
# 仓库:   本项目自身（只读验算，非第三方移植）
# 文件:   D:\AI\SW\probe_skip_whitelist.py
# 定位:   给 `check_gate_wiring.py` 的第四层判据（`ALLOWED_SKIP_CONDITIONS`）做**活体负例**：
#         证明「故障返回 `skipped`」会被抓、而三种**合法的** `skipped` 不会误报。
# ⚠ 写成独立文件是因为长内容内联进 `python -c` 会撞已知事实 48（转义/引号）。
# 官方依据: 不适用（本项目内部工具）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

GEN = Path(r"C:\swprojects\sw-skill-fork\scripts\check_gate_wiring.py")

#: `(名字, 源码, 期望是否命中白名单)`
CASES = [
    (
        "故障（超时/OSError）返回 skipped",
        "def f():\n"
        "    try:\n"
        "        pass\n"
        "    except OSError as exc:\n"
        '        return {"status": "skipped", "reason": str(exc)}\n',
        False,
    ),
    (
        "非 git 工作树返回 skipped（合理）",
        "def f():\n"
        "    if not _git_available():\n"
        '        return {"status": "skipped", "reason": "非 git"}\n',
        True,
    ),
    (
        "脚本约定 exit 2（合理）",
        "def f():\n"
        "    if proc.returncode == 2:\n"
        '        return {"status": "skipped", "reason": "读不到锚点"}\n',
        True,
    ),
    (
        "脚本自报 [SKIP] 驱动变量（合理）",
        "def f():\n"
        '    skipped = any(l.startswith("[SKIP]") for l in out)\n'
        "    if skipped:\n"
        '        status = "skipped"\n',
        True,
    ),
]


def main() -> int:
    spec = importlib.util.spec_from_file_location("_cgw", GEN)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_cgw"] = mod
    spec.loader.exec_module(mod)

    bad = 0
    for name, src, want in CASES:
        branches = mod.skip_branches(src)
        hit = any(any(tok in ctx for tok in mod.ALLOWED_SKIP_CONDITIONS)
                  for _ln, _cond, ctx in branches)
        ok = (hit == want)
        bad += 0 if ok else 1
        print("  %s %-34s 白名单命中=%-5s 应=%s"
              % ("✓" if ok else "**✗**", name, hit, want))
        for ln, cond, _ctx in branches:
            print("        L%d 依据: %s" % (ln, cond[:80]))
    print()
    print("  ── %d 个用例，不符 %d 个 ──" % (len(CASES), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
