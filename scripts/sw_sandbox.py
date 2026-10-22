"""★ 沙盒策略：外部路径**复制进来再用副本**，跑完把结果**拷到配置的输出根目录**。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力实现，铁律 3 的 `scripts/`）
# 文件:   scripts/sw_sandbox.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B5-3**（`copy-in / run / copy-ou
#           t`）。
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


# ── 产品模式（规格 210 · B5-4）────────────────────────────────────────────
# ★★ 业主已拍板：★ **产品模式**（用户让智能体改**他自己的**模型）下，
#   ★ 分析类产物**默认放进一个明确命名的子目录**，★ 并在**工具返回值里报出实际路径**，
#   ★ 不再静默落在零件旁边 ✓
# ⚠⚠ **一处必须说清的限度**：★ 分析类产物的**落点是 SolidWorks 自己决定的** ——
#   ★ 它就在零件旁边写结果文件，**那一步不经过我们的调用**（评审也确认了：
#   「内部写不经过你们的调用，所以应用层守卫对它无效」）✓
#   ⇒ ★★ 所以本段的做法**不是**「拦住它」，而是：★ **跑完检测出新增/改动的文件** ⇒
#     ★ **搬进那个明确命名的子目录** ⇒ ★ **把搬到的路径写进返回值** ✓
#   ⇒ ★ 我们不假装能控制它，★ 只保证「**产物有名字、有去处、能被报出来**」 ✓

POLICY_SANDBOX = "sandbox"
POLICY_PRODUCT = "product"


def policy() -> str:
    """★ 输出策略：`sandbox`（测试/自动化，默认）或 `product`（用户让自己的模型被改）✓"""
    value = str(os.environ.get("SW_OUTPUT_POLICY", POLICY_SANDBOX)).strip().lower()
    return POLICY_PRODUCT if value == POLICY_PRODUCT else POLICY_SANDBOX


def product_output_dir(source_doc) -> Path:
    """★ 产品模式下分析产物的**明确命名的子目录** —— ★ 放在**该零件所在目录**下的一个子目录里 ✓

    ★ 为什么放「旁边」而不是别处：★ 产品模式下用户**就是要改自己的模型**，
      ★ 产物跟着零件走才找得到；★ 但**必须有个名字**，★ 不能散落在零件旁边（那正是当初出事的样子）✓
    """
    src = Path(str(source_doc))
    return src.parent / ("%s_MCP_output" % src.stem)


def snapshot_dir(folder) -> dict:
    """★ 给一个目录拍**只读**快照（`路径 -> (大小, 修改时间)`），★ 用来算「跑完多了什么」 ✓

    ⚠ 只读：★ 本函数**不创建、不修改、不删除**任何东西 ✓
    """
    base = Path(str(folder))
    if not base.is_dir():
        return {}
    snap = {}
    for p in base.rglob("*"):
        try:
            if p.is_file():
                st = p.stat()
                snap[str(p)] = (st.st_size, int(st.st_mtime))
        except OSError:                                                 # 权限/竞态
            continue
    return snap


def new_since(before: dict, folder) -> list:
    """★ 跑完之后**多了什么、什么被改了** —— ★ 这就是「SolidWorks 自己写出来的那些文件」✓

    ★★ 这是我们能做的**唯一**可靠办法：★ 拦不住它写，★ 但**能看见它写了什么** ✓
    """
    after = snapshot_dir(folder)
    return [p for p, sig in sorted(after.items()) if before.get(p) != sig]


def tidy_outputs(files, source_doc) -> dict:
    """★★ 把「跑完多出来的文件」**搬进明确命名的子目录**，★ 并回一份**可写进返回值的报告** ✓

    :returns: `{"output_dir": …, "moved": [{"from","to"}], "skipped": [{"path","why"}]}`
    ★★ 三条安全判据（★ 都是「不许删数据」的直接后果）：
      ① ★ **只搬调用方点名给的那些** —— ★ 不做目录级清理 ✓
      ② ★ **目标已存在就不覆盖**（★ 覆盖会毁掉上一次的产物）⇒ 记进 `skipped` 并**换名** ✓
      ③ ★ 搬不动（占用/权限）⇒ **记进 `skipped`** 并如实报出，★ **不假装成功** ✓
    """
    dest_dir = product_output_dir(source_doc)
    moved, skipped = [], []
    for f in (files or ()):
        src = Path(str(f))
        if not src.is_file():
            skipped.append({"path": str(src), "why": "★ 不是文件（已消失或不是常规文件）"})
            continue
        if _inside(src, dest_dir):
            skipped.append({"path": str(src), "why": "★ 已经在目标子目录里了"})
            continue
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:                                          # noqa: BLE001
            skipped.append({"path": str(src), "why": "★ 建不了目标目录：%s" % exc})
            continue
        dest = dest_dir / src.name
        n = 1
        while dest.exists():
            dest = dest_dir / ("%s__%d%s" % (src.stem, n, src.suffix))
            n += 1
        try:
            shutil.move(str(src), str(dest))
        except OSError as exc:                                          # noqa: BLE001
            skipped.append({"path": str(src), "why": "★ 搬不动：%s" % exc})
            continue
        moved.append({"from": str(src), "to": str(dest)})
    return {"output_dir": str(dest_dir), "moved": moved, "skipped": skipped}


def output_report(source_doc, files, *, run_id_value: str = "") -> dict:
    """★★ **可写进工具返回值**的产物报告（★ 业主拍板的「报出实际路径」就落在这里）✓

    ★ 形状固定，便于调用方直接塞进返回值：`{"output_dir", "files": [...], "run_id", "policy"}` ✓
    ★★ 若 `policy() == product` ⇒ **顺手搬进那个命名子目录**，★ 并把搬到的**新路径**报出来 ✓
    """
    if policy() == POLICY_PRODUCT:
        tidy = tidy_outputs(files, source_doc)
        paths = [m["to"] for m in tidy["moved"]] + [s["path"] for s in tidy["skipped"]]
        return {"output_dir": tidy["output_dir"], "files": paths,
                "moved": tidy["moved"], "skipped": tidy["skipped"],
                "run_id": run_id_value or run_id(), "policy": POLICY_PRODUCT}
    return {"output_dir": str(output_root()), "files": [str(p) for p in (files or ())],
            "moved": [], "skipped": [], "run_id": run_id_value or run_id(),
            "policy": POLICY_SANDBOX}

