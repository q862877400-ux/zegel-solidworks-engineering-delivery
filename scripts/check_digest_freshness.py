r"""@brief 门禁：`docs/harvest-digest.md` 必须与 `tools/gen_harvest_digest.py` 的输出一致。

## 为什么需要它
`docs/harvest-digest.md` 是**生成物**（承接 `AGENTS.md §一 A8`：
报告要写「并入了什么 / 仍空缺什么 / 为什么」）。
⚠ **生成物一旦允许手改，真源与产物就会分叉** —— 而这类分叉**不会自己暴露**
（本项目已多次记录：「文档串与代码不符比没有文档更糟」）。

⇒ 判据：**重跑生成器 ⇒ 必须与当前文件逐字节相同**。
这正是 `check_union_conventions.py` 的「地图与来源同步」段与 R8 段用的同一手法。

## 手法（与 R8 一致）
把生成器的 `OUT` 指到**临时路径**跑一遍，读回来比对 —— **绝不覆盖真文件**。
⇒ 失败时**不留下**任何被改过的产物（本门禁是**只读**的）。

# ── 来源 ──
# 仓库:   本项目自身（门禁，非第三方移植）
# 文件:   scripts/check_digest_freshness.py
# 定位:   给 `tools/gen_harvest_digest.py` 的产物加新鲜度判据。
#         与 `check_union_conventions.py` 的 R8 段同源手法（生成物 + 新鲜度）。
# 官方依据: 不适用（本项目内部工具，不调 SolidWorks API）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "tools" / "gen_harvest_digest.py"
TARGET = ROOT / "docs" / "harvest-digest.md"


def _load_gen():
    spec = importlib.util.spec_from_file_location("_gen_harvest_digest", GEN)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_gen_harvest_digest"] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    if not GEN.is_file():
        print("[FAIL] 缺生成器 %s" % GEN.relative_to(ROOT))
        return 1
    if not TARGET.is_file():
        print("[FAIL] 缺生成物 %s ⇒ 跑 `python tools/gen_harvest_digest.py`"
              % TARGET.relative_to(ROOT))
        return 1

    current = TARGET.read_text(encoding="utf-8")
    gen = _load_gen()
    original_out = gen.OUT

    with tempfile.TemporaryDirectory() as td:
        try:
            gen.OUT = Path(td) / "harvest-digest.md"
            rc = gen.main()
            if rc != 0:
                print("[FAIL] 生成器退出码 %s" % rc)
                return 1
            fresh = gen.OUT.read_text(encoding="utf-8")
        finally:
            gen.OUT = original_out        # ⚠ 恢复，绝不指向真文件

    if fresh == current:
        print("交付摘要新鲜度门禁 · %s（%d 字节）"
              % (TARGET.relative_to(ROOT), len(current.encode("utf-8"))))
        print("[PASS] 与生成器输出逐字节相同")
        return 0

    print("[FAIL] %s 与生成器输出不一致" % TARGET.relative_to(ROOT))
    cur_lines = current.splitlines()
    frh_lines = fresh.splitlines()
    diff = next((i for i in range(max(len(cur_lines), len(frh_lines)))
                 if (cur_lines[i] if i < len(cur_lines) else None)
                 != (frh_lines[i] if i < len(frh_lines) else None)), 0)
    print("   首个不同在第 %d 行：" % (diff + 1))
    print("     当前: %s" % (cur_lines[diff][:110] if diff < len(cur_lines) else "（缺行）"))
    print("     应为: %s" % (frh_lines[diff][:110] if diff < len(frh_lines) else "（多行）"))
    print("   ⇒ 修法：`python tools/gen_harvest_digest.py` 后提交该生成物")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
