"""★ 沙盒策略：外部路径**复制进来再用副本**，跑完把结果**拷到配置的输出根目录**。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力实现，铁律 3 的 `scripts/`）
# 文件:   scripts/sw_sandbox.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B5-3**（`copy-in / run / copy-out`）。
#   ★★ 外部评审的判决：★ 要守的规则**不是**「输出不落在输入旁边」，而是
#     「**SolidWorks 打开的永远不是原件**」⇒ ★ 出事的根因是「对**原件路径**直接开了分析」 ✓
#   ⇒ ★ 所以做法是 **copy-in / run / copy-out**，而不是去拦 SolidWorks 的内部写 ✓
# 判据:   ★★ `resolve_input(path)`：路径在沙盒**外** ⇒ **复制进沙盒**并返回副本路径；
#   ★ 在沙盒内 ⇒ 原样返回；★ **复制是加法**，不动原件 ✓
#   ★ `collect_outputs(...)`：把跑出来的结果拷到 `output_root()`（★ 带 run id 防重名）✓
#   ★★ **默认 `passthrough`**（不改变既有行为）—— ★ 由**护栏**给探针子进程设 `enforce`
#     （★ 见 `tools/sw_guard.py`）⇒ ★ 于是「真机跑」这条路被保护，而单测/离线调用不受影响 ✓
# 官方依据: 无（这是**我方策略**，不是官方 API）—— ★ 如实标注，不假托官方 ✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path

#: ★ 本仓根（★ 沙盒与输出根的默认落点在**不入库**的 `output/` 下）✓
REPO_ROOT = Path(__file__).resolve().parents[1]

MODE_ENFORCE = "enforce"
MODE_PASSTHROUGH = "passthrough"

#: ★★ 被「判为在沙盒外」的路径才需要复制；★ 这些**只读来源**永远放行（★ 它们是共享素材，不在沙盒里）✓
#: ★★★ 2026-10-06 我第一版把**模型素材库**也列了进来 ⇒ ★★ 那会原样重演当初的事故：
#:   ★ 出事的正是「对**素材库里的件**直接开分析」⇒ 分析产物**落在那个目录里**（写进了用户目录）✗
#:   ⇒ ★ **模型素材也必须复制进沙盒**（★ 它是**输入**，不是「只读文档」）；
#:   ★ 只有 `C:\swapi` 那种**纯文档**（SolidWorks 永远不会打开它、更不会往旁边写结果）才豁免 ✓
DEFAULT_READONLY_SOURCES = (
    Path(r"C:\swapi"),
)


def mode() -> str:
    """★ 沙盒模式 —— ★★ **默认 `passthrough`**（★ 不改变既有行为）；★ 由护栏给探针设 `enforce` ✓"""
    value = str(os.environ.get("SW_SANDBOX_MODE", MODE_PASSTHROUGH)).strip().lower()
    return MODE_ENFORCE if value == MODE_ENFORCE else MODE_PASSTHROUGH


def run_id() -> str:
    """★ 本次运行的 id（★ 用来给输出目录防重名）—— ★ 可用 `SW_RUN_ID` 覆盖 ✓"""
    given = str(os.environ.get("SW_RUN_ID", "")).strip()
    return given or datetime.now().strftime("%Y%m%d-%H%M%S")


def sandbox_root() -> Path:
    """★ 沙盒根（★ 我们自己的地盘 ⇒ 在这里改、存、跑都安全）✓"""
    given = str(os.environ.get("SW_SANDBOX_ROOT", "")).strip()
    return Path(given) if given else (REPO_ROOT / "output" / "sandbox")


def output_root() -> Path:
    """★★ **输出根目录独立配置**（评审要求）—— ★ 默认按 run id 分开；★ 可用 `SW_OUTPUT_ROOT` 覆盖 ✓"""
    given = str(os.environ.get("SW_OUTPUT_ROOT", "")).strip()
    return Path(given) if given else (REPO_ROOT / "output" / "runs" / run_id())


def _norm(value) -> str:
    text = str(value or "").strip()
    return os.path.normcase(os.path.normpath(text)) if text else ""


def _inside(path, root) -> bool:
    """★ `path` 是否在 `root` 之内（★ 归一化后按**公共前缀**判，不用字符串 startswith 的坑）✓"""
    p, r = _norm(path), _norm(root)
    if not p or not r:
        return False
    try:
        return os.path.commonpath([p, r]) == r
    except ValueError:                                                  # 不同盘符
        return False


def resolve_input(file_path, *, extra_readonly=()):
    """★★ **copy-in**：返回**真正该打开的那个路径** —— ★ 沙盒外的输入会被**复制进沙盒** ✓

    :returns: `{"path": 该打开的路径, "materialized": 是否复制过, "source": 原路径, "why": 说明}`
    ★★ 三条判序（★ 都是**加法**，删不了任何东西）：
      ① 模式是 `passthrough` ⇒ 原样返回（★ 默认，不改变既有行为）✓
      ② 路径**在沙盒内** ⇒ 原样返回（★ 它本来就是我们的地盘）✓
      ③ 路径是**只读共享来源**（官方源 / 模型素材）⇒ 原样返回（★ 只读打开即可，复制纯浪费）✓
      ⇒ ★ 其余一律**复制进沙盒**，返回副本 ✓
    """
    src = Path(str(file_path))
    if mode() != MODE_ENFORCE:
        return {"path": str(src), "materialized": False, "source": str(src),
                "why": "★ 模式是 passthrough ⇒ 不复制（★ 默认行为）"}
    if not src.exists():
        return {"path": str(src), "materialized": False, "source": str(src),
                "why": "★ 源不存在 ⇒ 交给上层报错（★ 本函数不假装成功）"}
    if _inside(src, sandbox_root()):
        return {"path": str(src), "materialized": False, "source": str(src),
                "why": "★ 已在沙盒内 ⇒ 原样用"}
    for allowed in tuple(DEFAULT_READONLY_SOURCES) + tuple(extra_readonly):
        if _inside(src, allowed):
            return {"path": str(src), "materialized": False, "source": str(src),
                    "why": "★ 只读共享来源（%s）⇒ 不复制" % Path(allowed).name}
    dest_dir = sandbox_root() / "inputs"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    #: ★ 重名不覆盖：★ 换一个带序号的名字（★ 覆盖会**毁掉上一次的输入**，那是删数据）✓
    n = 1
    while dest.exists() and _norm(dest) != _norm(src):
        dest = dest_dir / ("%s__%d%s" % (src.stem, n, src.suffix))
        n += 1
    if _norm(dest) != _norm(src):
        shutil.copy2(str(src), str(dest))
    return {"path": str(dest), "materialized": True, "source": str(src),
            "why": "★★ 沙盒外的输入 ⇒ **已复制进沙盒**再用副本（★ 打开的永远不是原件）"}


def collect_outputs(paths, *, note: str = ""):
    """★ **copy-out**：把跑出来的结果从沙盒**拷到配置的输出根目录**（★ 带 run id）✓

    :returns: `[{"source", "copied_to"} …]` —— ★ **拷贝**，★ 沙盒里那份留下（★ 便于复查）✓
    """
    dest_dir = output_root() / "results"
    dest_dir.mkdir(parents=True, exist_ok=True)
    moved = []
    for p in (paths or ()):
        src = Path(str(p))
        if not src.exists() or not src.is_file():
            continue
        dest = dest_dir / src.name
        n = 1
        while dest.exists():
            dest = dest_dir / ("%s__%d%s" % (src.stem, n, src.suffix))
            n += 1
        shutil.copy2(str(src), str(dest))
        moved.append({"source": str(src), "copied_to": str(dest)})
    if note:
        (dest_dir / "_note.txt").write_text(note, encoding="utf-8")
    return moved


def sweep(root=None):
    """★ 列出沙盒里的文件（★ 只读，给「跑完看看产出了什么」用）✓"""
    base = Path(root) if root else sandbox_root()
    if not base.is_dir():
        return []
    return [str(p) for p in sorted(base.rglob("*")) if p.is_file()]
