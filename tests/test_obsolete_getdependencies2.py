"""★ 测 `sw_delivery` 不再用废弃的 `GetDependencies2`（★ 阶段 2 · T1 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\`）
# 文件:   `scripts/sw_delivery.py::_document_dependency_paths`
# 定位:   ★ 阶段 2 · T1（★ 消解废弃成员）的**逐条流程**第一条：★ **先查官方签名与 Remarks** ✓
#   ★★ **官方逐字**（★ `IModelDoc2/GetDependencies2.md`）：
#     「**Obsolete. Superseded by `IModelDocExtension::GetDependencies`**.」✓
#     旧签名 ⇒ `(bool Traverseflag, bool Searchflag, bool AddReadOnlyInfo)` ⇒ **3 参** ✓
#   ★★★ **后继逐字**（★ `IModelDocExtension/GetDependencies.md`）：
#     `(bool Traverseflag, bool Searchflag, bool AddReadOnlyInfo, bool ListBrokenRefs,
#      bool AppendImportedPaths)` ⇒ **5 参** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "scripts" / "sw_delivery.py"
OFF_OLD = Path(r"C:\swapi\types\IModelDoc2\GetDependencies2.md")
OFF_NEW = Path(r"C:\swapi\types\IModelDocExtension\GetDependencies.md")


def test_official_chain_is_still_as_documented() -> None:
    """★★★ **前提断言**：★ 官方那两页**确实**这么写（★ 判据的锚点）✓"""
    if not (OFF_OLD.is_file() and OFF_NEW.is_file()):
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    old = OFF_OLD.read_text(encoding="utf-8", errors="replace")
    new = OFF_NEW.read_text(encoding="utf-8", errors="replace")
    assert "Obsolete" in old and "IModelDocExtension::GetDependencies" in old, "★ 旧页口径变了"
    assert "ListBrokenRefs" in new and "AppendImportedPaths" in new, "★ 后继页参数变了"


def test_code_does_not_call_the_obsolete_member() -> None:
    """★★★ 核心断言：★ 代码里**不许**再调 `GetDependencies2` ✓"""
    t = SRC.read_text(encoding="utf-8", errors="replace")
    #: ★ 只看**代码**（★ 注释里引了旧名，★ 那是「补正而不是删除」）
    code = "\n".join(l for l in t.splitlines() if not l.lstrip().startswith("#"))
    assert '"GetDependencies2"' not in code, "★ 还在调废弃的 `GetDependencies2`"


def test_calls_the_successor_with_five_args() -> None:
    """★★★ 核心断言：★ 必须调**后继**、★ 且**参数个数对**（★ 5 个）✓"""
    t = SRC.read_text(encoding="utf-8", errors="replace")
    i = t.find('"GetDependencies"')
    assert i != -1, "★ 没调后继 `GetDependencies`"
    seg = t[i:i + 220]
    args = re.search(r'"GetDependencies",\s*([^)]*)', seg)
    assert args, "★ 解析不出实参"
    n = len([a for a in args.group(1).split(",") if a.strip()])
    assert n == 5, "★ 实参是 %d 个、★ 官方后继要 **5** 个" % n


def test_negative_case_interface_moved_to_extension() -> None:
    """★★★ **负例 · 归属**：★ 必须走 `model.Extension`（★ 那是后继所在的接口）✓

    ★★ 为什么重要：★ 旧成员在 `IModelDoc2`、★ **后继在 `IModelDocExtension`** ⇒
      ★★★ **只改名字不改接口 ⇒ 会 `AttributeError`**（★ 事实 36 那一族：**成员在别的接口上**）✓
    """
    t = SRC.read_text(encoding="utf-8", errors="replace")
    i = t.find('"GetDependencies"')
    seg = t[max(0, i - 400):i]
    assert "Extension" in seg, "★ 没走 `Extension` ⇒ 接口没跟着换"
