r"""★ 判据：打包副本必须与源一致，且不得再**把非官方 sg 名当合法值**（spec 223 / US3）。

背景（F4）：`apps/workbench-ui/src-tauri/resources/skill/` 落后于源 ——
本轮实测 `find_bundled_skill_drift()` 报 **4** 处内容不一致
（`scripts/sw_part.py`、`scripts/sketch_relations.py`、`mcp-server/tool_specs_batch16.py`、
`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`）
+ **1** 个文件缺失（`scripts/sw_sketch_relations.py`）。
★ 并且本轮**新发现**：源头的 `references/part-modeling.md` 自己就把 `sgEQUAL` / `sgMIDPOINT`
当「常用约束类型」列出（222 只改了 `.py`，**漏了这份文档**）⇒ 同步会把错值一起搬进发布包。

★ 判据分两类（**这是本轮踩过的坑**）：
  · **文档类**（按字面列合法值）⇒ 那两个串**一个都不许出现**；
  · **代码类**（222 的修正**就在**「这些名字不存在」的注释与别名表里）⇒
    判据只能是**与源逐字节一致**，**不能**要求「串不出现」（那会把正确的说明判红）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_bundled_skill_enum_freshness.py —— 本文件自身
# 定位:   spec 223 US3 的判据；被测对象是打包 Skill 快照。
# 官方依据: C:/swapi/types/IModelDoc2/SketchAddConstraints.md 的 ## Remarks（无 sgEQUAL / sgMIDPOINT）
#           specs/222-relation-enum-and-public-contract/ 的裁决
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLED = REPO_ROOT / "apps/workbench-ui/src-tauri/resources/skill"

#: 222 已判定的**非官方名**（官方 Remarks 里 0 命中）
NON_OFFICIAL = ("sgEQUAL", "sgMIDPOINT")
#: 它们对应的**官方名**
OFFICIAL_NAMES = ("sgSAMELENGTH", "sgATMIDDLE")

#: 文档类：按字面列「常用约束类型」⇒ 非官方名**一个都不许出现**
DOC_FILES = ("references/part-modeling.md",)
#: 代码类：允许在「这些名字不存在」的说明/别名表里出现 ⇒ 判据是**与源逐字节一致**
PY_FILES = ("scripts/sw_part.py", "mcp-server/tool_specs_batch16.py")


def test_bundled_doc_lists_only_official_sg_names():
    r"""★ 判据是**清单行**（`常用约束类型：…`）里只许有官方名 ——

    而**不是**「串不出现」：订正说明**必然**要提到那两个旧名
    （★ 本轮踩过：把「串不出现」当判据 ⇒ 正确的说明被自己判红）。"""
    for rel in DOC_FILES:
        p = BUNDLED / rel
        assert p.is_file(), "打包副本缺文件：%s" % rel
        lines = [ln for ln in p.read_text(encoding="utf-8", errors="replace").splitlines()
                 if ln.startswith("常用约束类型")]
        assert lines, "%s 里找不到「常用约束类型」清单行" % rel
        for ln in lines:
            for bad in NON_OFFICIAL:
                assert bad not in ln, (
                    "%s 的清单行仍把非官方名 %s 当合法值：%s" % (rel, bad, ln))
            for good in OFFICIAL_NAMES:
                assert good in ln, "%s 的清单行缺官方名 %s" % (rel, good)


def test_bundled_py_copies_are_byte_identical_to_source():
    """★ 代码副本必须**逐字节**等于源（★ 那正是 `find_bundled_skill_drift` 的判据）。"""
    for rel in PY_FILES:
        src = REPO_ROOT / rel
        dst = BUNDLED / rel
        assert src.is_file(), "源缺文件：%s" % rel
        assert dst.is_file(), "打包副本缺文件：%s" % rel
        assert src.read_bytes() == dst.read_bytes(), (
            "打包副本 %s 与源不一致 ⇒ 跑 scripts/sync_bundled_skill.py" % rel)


def test_bundled_skill_matches_source():
    """FR-020：打包副本与源**零漂移**（与 `release_check` 的同一判据，此处做成快速单元判据）。"""
    sys.path.insert(0, str(REPO_ROOT))
    from scripts.release_check import find_bundled_skill_drift
    drift = find_bundled_skill_drift(REPO_ROOT, BUNDLED)
    assert drift == [], (
        "打包副本与源不一致（先跑 scripts/sync_bundled_skill.py）：\n  " + "\n  ".join(drift))


# ── 直接运行 ─────────────────────────────────────────────────────────

def _main():
    failures = []
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        try:
            test()
            print(f"  PASS  {test.__name__}")
        except Exception as exc:  # noqa: BLE001
            failures.append((test.__name__, exc))
            print(f"  FAIL  {test.__name__}: {exc}")
    print(f"\n{len(tests) - len(failures)}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    raise SystemExit(_main())
