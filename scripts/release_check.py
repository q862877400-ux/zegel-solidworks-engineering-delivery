"""发布前静态一致性门禁。"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from filecmp import cmp
from pathlib import Path

try:
    from .sync_bundled_skill import collect_runtime_files
except ImportError:
    from sync_bundled_skill import collect_runtime_files

ROOT = Path(__file__).resolve().parents[1]
BUNDLED_SKILL = ROOT / "apps/workbench-ui/src-tauri/resources/skill"


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（发布门禁的扩展）
# 文件:   scripts/release_check.py —— 本文件自身
# 定位:   新增 `_run_provenance_gate` 与 `run_release_check()` 里的两个阶段：
#         ① 必需文件清单补上本任务的 4 份文档与 6 个新模块（防被静默丢弃）；
#         ② 把来源可追溯性门禁（scripts/check_provenance.py）接入发布前检查。
# 为什么要接：铁律 1「每加一个能力必须能指认出处」如果只靠人工跑一次门禁，
#         必然随时间衰减；接进发布检查才成为**仓库永久强制**的约束。
# ⚠ 关于 A6 禁词为什么**不能**做成全仓严格检查（实测结论，勿改成严格版）:
#         上游基线 `C:\swprojects\sw-automation-skill`（8be39ac）自身在
#         scripts/subskills/tests/examples/docs/references 下就有 **23 处**命中
#         A6 词表（如 advanced_geometry_ocp.py 2 处、dfm_review.py 1 处、
#         advanced.md 2 处…），capabilities.yaml 另有 37 处。
#         全仓严格检查会因**上游既有内容**失败 —— 那不是新增代码的问题。
#         故 A6 只能作用于「相对锚点的新增/修改行」，必须靠 git diff 判断。
#         下文 `_run_provenance_gate` 因此设计为：锚点可解析时强制执行，
#         不可解析时**显式返回 skipped**（写进结果，不静默放行）。
# 锚点:   环境变量 PROVENANCE_ANCHOR 优先，默认 ``origin/main``（上游只读锚点）。
# 覆盖:   后续同级定义 —— 本块文档化 REQUIRED_ABILITY_FILES、_git_available、
#         _run_provenance_gate 三个单元。
# ⚠ 本组为照既有门禁模式新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────

#: 本任务新增/扩展的发布必需文件（新增即纳入清单，防被静默丢弃）
REQUIRED_ABILITY_FILES = (
    "docs/capability-matrix.md",
    "docs/gap-analysis.md",
    "docs/signature-audit.md",
    "docs/harvest-report.md",
    "docs/usage-guide.md",
    "docs/api-map.md",
    "docs/family-coverage.md",
    "docs/provenance-index.json",
    "scripts/sw_simulation.py",
    "scripts/sw_surface.py",
    "scripts/sw_render_material.py",
    "scripts/sketch_relations.py",
    "scripts/check_provenance.py",
    "scripts/audit_call_arity.py",
    "scripts/audit_byref_args.py",
    "scripts/audit_acceptance_criteria.py",
    "scripts/refresh_api_signatures.py",
    "scripts/check_diff_markers.py",
    "scripts/check_member_names.py",
    "scripts/sw_costing.py",
    "tests/test_sw_simulation_signature_contract.py",
    "tests/test_sw_surface_signature_contract.py",
    "tests/test_drawing_signature_contract.py",
)


def _git_available() -> bool:
    try:
        subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "--git-dir"],
            check=True, capture_output=True, timeout=30,
            stdin=subprocess.DEVNULL,
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return False


def _run_provenance_gate() -> dict[str, object]:
    """跑来源可追溯性门禁，返回可并入发布结果的结构。

    返回三种状态：
      ``pass``    —— 锚点可解析且门禁通过
      ``fail``    —— 锚点可解析但有违规（调用方据此 raise）
      ``skipped`` —— 无 git 或锚点不可解析；**显式报告，不静默放行**
    """
    if not _git_available():
        return {"status": "skipped", "reason": "非 git 工作树，无法判定新增行"}
    anchor = os.environ.get("PROVENANCE_ANCHOR", "origin/main")
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_provenance.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=300, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "reason": f"门禁**无法启动**（超时/OSError）: {exc}"}
    if proc.returncode == 2:
        return {"status": "skipped", "anchor": anchor,
                "reason": "门禁读不到锚点，请设置 PROVENANCE_ANCHOR"}
    ok = proc.returncode == 0
    return {
        "status": "pass" if ok else "fail",
        "anchor": anchor,
        "output": (proc.stdout or "").strip()[-2000:],
    }



def _version(path: Path, pattern: str) -> str:
    match = re.search(pattern, path.read_text(encoding="utf-8"))
    if not match:
        raise AssertionError(f"无法读取版本: {path}")
    return match.group(1)


def find_bundled_skill_drift(root: Path, bundled_skill: Path, expected_paths=None) -> list[str]:
    """@brief 返回桌面内嵌 Skill 中缺少源文件或内容不一致的相对路径。"""
    if not bundled_skill.is_dir():
        return ["<bundled-skill-missing>"]
    drift: list[str] = []
    for bundled_path in sorted(path for path in bundled_skill.rglob("*") if path.is_file()):
        relative_path = bundled_path.relative_to(bundled_skill)
        source_path = root / relative_path
        relative_name = relative_path.as_posix()
        if not source_path.is_file():
            drift.append(f"missing-source:{relative_name}")
        else:
            try:
                if not cmp(source_path, bundled_path, shallow=False):
                    drift.append(relative_name)
            except FileNotFoundError:
                # Tauri build.rs 会原子性不足地重建 resources/skill；并行检查时
                # 将瞬时消失稳定记录为缺失，而不是暴露底层文件系统异常。
                drift.append(f"missing-bundle:{relative_name}")
    for relative_path in sorted(expected_paths or [], key=lambda value: Path(value).as_posix()):
        relative = Path(relative_path)
        if not (bundled_skill / relative).is_file():
            drift.append(f"missing-bundle:{relative.as_posix()}")
    return drift


def _run_marker_gate() -> dict[str, object]:
    """跑 diff 记号残留检查（scripts/check_diff_markers.py）。

    为什么接进发布检查：写「来源块」注释时把 patch 的行首记号
    （``+ `` / ``* ``）带进来，**本项目连续三轮**都发生过，
    每次都要 ``py_compile`` 才发现，且编译错误不告诉你是哪个来源块。
    变成门禁后，提交前就能拿到「哪个文件第几行」。
    """
    # ── 来源 ─────────────────────────────────────────────────────────
    # 仓库:   本项目自身（发布门禁的扩展）
    # 文件:   scripts/release_check.py —— 本文件自身
    # 定位:   新增 `_run_marker_gate`：跑 check_diff_markers.py 并把结果
    #         并入 run_release_check 的结果（字段名 `diff_markers`）。
    # 触发原因: 本任务写来源块时**连续三轮**把 diff 行首记号带进注释
    #         （sw_simulation_loads.py / sw_routing.py / sw_costing.py），
    #         每次都由 py_compile 的 IndentationError 才发现。
    # ⚠ 门禁工具本身经过负向验证：注入真记号后确实报 FAIL 并点名行号；
    #   同一文件 py_compile 报 IndentationError —— 两者指向同一问题。
    # 覆盖:   后续同级定义
    # ⚠ 本组为照既有门禁模式新写，未在本机实测（见 AGENTS.md 铁律 2）
    # ─────────────────────────────────────────────────────────────────
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_diff_markers.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=120, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "reason": f"检查**无法启动**（超时/OSError）: {exc}"}
    return {
        "status": "pass" if proc.returncode == 0 else "fail",
        "output": (proc.stdout or "").strip()[-1500:],
    }


def _run_union_conventions_gate() -> dict[str, object]:
    """跑并入规范门禁（scripts/check_union_conventions.py）。

    为什么接进发布检查：2026-09-30 起本仓库开始并入四个外部 MCP 项目
    （MIT ×3 + Apache-2.0 ×1）。四家各有各的命名、单位、验证口径，
    **不设门禁必然并成大杂烩**。docs/union-conventions.md 立了五条规则，
    这道门把它们变成会执行的不变量。
    """
    # ── 来源 ─────────────────────────────────────────────────────────
    # 仓库:   本项目自身（发布门禁的扩展）
    # 文件:   scripts/release_check.py —— 本文件自身
    # 定位:   新增 `_run_union_conventions_gate`：跑 check_union_conventions.py
    #         并把结果并入 run_release_check 的结果（字段名 `union_conventions`）。
    # 触发原因: 并入 Eduardof0nt/andrewbartels1/vespo92/Slacker-LLC 四家时，
    #         发现四家命名（sw_/无前缀/vba_）、单位、验证口径各不相同。
    # 官方依据: 无（本门禁只读本仓库文件）
    # 覆盖:   后续同级定义
    # ⚠ 与既有门禁同模式新写，未在本机实测（见 AGENTS.md 铁律 2）；
    #   但其规则首次运行即抓到 capabilities.yaml 两条「标 verified 无版本证据」，
    #   并据此把规则收紧为「只对 CAD 后端要求版本」（见 union-conventions.md）。
    # ─────────────────────────────────────────────────────────────────
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_union_conventions.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=180, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "reason": f"检查**无法启动**（超时/OSError）: {exc}"}
    verdict = {
        "status": "pass" if proc.returncode == 0 else "fail",
        "output": (proc.stdout or "").strip()[-1500:],
    }

    # ── 来源 ─────────────────────────────────────────────────────────
    # 仓库:   本项目自身（发布门禁的扩展）
    # 文件:   scripts/release_check.py —— 本文件自身
    # 定位:   上一步的并入门禁跑完后，接着跑 **判据有效性检验**
    #         （tools/prove_authorization_check.py），结果并入 `union_conventions`。
    # 触发原因: 2026-10-01 加 R11「授权真源是 allowed_modes」的静态检查时发现 ——
    #         **门禁绿本身不构成证据**，一个永远绿的检查也是绿的。该脚本拿迁移前
    #         真实存在的那两处授权泄漏喂给判据确认命中，再拿修复后的写法确认放过；
    #         它第一次跑就抓出判据漏了「授权函数体内按 level 判」这一形状
    #         （即 unattended_allowed() 被改回旧实现的形状）。
    # 官方依据: 无（本检查只读本仓库文件）
    # 许可:   本仓库 MIT
    # ⚠ 纯文本判据的单元验证，未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）。
    # 覆盖:   后续同级定义
    # ─────────────────────────────────────────────────────────────────
    try:
        proof = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "tools" / "prove_authorization_check.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=120, cwd=str(ROOT), stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        verdict["proof"] = {"status": "fail", "reason": f"检验**无法启动**（超时/OSError）: {exc}"}
        return verdict
    verdict["proof"] = {
        "status": "pass" if proof.returncode == 0 else "fail",
        "output": (proof.stdout or "").strip()[-600:],
    }
    if proof.returncode != 0:
        # 判据本身失效时，规范门禁的绿灯不可信 —— 一并判 fail
        verdict["status"] = "fail"
    return verdict


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（发布门禁的扩展）
# 文件:   scripts/release_check.py —— 本文件自身
# 定位:   新增 `_run_member_name_gate`：跑 check_member_names.py 并把结果
#         并入 run_release_check 的结果（字段名 `member_names`）。
# 触发原因: 本任务「凭印象写 API」栽过 **9 次**（7 次多写、1 次删多、1 次拼错），
#         典型如 ``IDisplayDimension.GetValue`` / ``IModelDocExtension.MateType`` /
#         ``ICurve.IsArc``（官方**没有「圆弧」这个独立类型**）/
#         ``ISectionViewData.AccessSelections``（5 个成员全是从别的族搬来的）。
#         ⚑ 这些**单文件契约测试全都抓不到** —— 契约测试只验「引用的成员在
#           登记表里」，而登记表本身就可能是错的。**全仓扫描才查得出。**
# ⚠ 门禁工具本身经**负向验证**：注入一个确定不存在的成员名后确实报 FAIL
#   并点名文件与行号，删除后恢复 PASS。
# 覆盖:   后续同级定义
# ⚠ 本组为照既有门禁模式新写，未在本机实测（见 AGENTS.md 铁律 2）
# ─────────────────────────────────────────────────────────────────────
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把环境坑门禁接进发布前检查）+ Python 标准库 `subprocess`
# 文件:   `scripts/check_env_pitfalls.py`（本门禁的实现）
#         `D:\AI\SW\AGENTS.md` 已知事实 58（subprocess 缺 encoding）/ 59（Path("D:") 不是盘根）
# 定位:   新增 `_run_env_pitfalls_gate`：**这是硬门禁，不是诊断** ——
#         它查的两类都是**机制性**的（不依赖某次运行的环境），纯静态可判，
#         且两类都**已经在真机上造成过真实故障**：
#           · `subprocess(..., text=True)` 缺 `encoding=` ⇒ 中文 Windows 上
#             `stdout` 变 None（**4 个基线失败**，事实 58）
#           · `Path("D:")` 当盘根 ⇒ `D:AutoCAD 2024\acad.exe`（缺反斜杠）
#             ⇒ **D:/E: 盘的 CAD 一直发现不了**（真实功能 bug，事实 59）
#         **⇒ 与 `_run_interface_ownership_probe`（诊断）的区别：那个**只报告**，
#            这个**拦发布** —— 因为这两类**不是「可能有问题」，而是「一定会坏」。**
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────
def _run_env_pitfalls_gate() -> dict[str, object]:
    """@brief 跑环境坑门禁（`scripts/check_env_pitfalls.py`）。"""
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_env_pitfalls.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=180, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "output": "环境坑门禁无法执行: %s" % exc}
    status = "pass" if proc.returncode == 0 else "fail"
    return {"status": status, "output": (proc.stdout or "") + (proc.stderr or "")}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把验收命令可跑性接进发布前检查）+ Python 标准库 `subprocess`
# 文件:   `scripts/check_spec_acceptance_paths.py`（本门禁的实现）
#         `D:\AI\SW\docs\ROADMAP.md` §〇 纪律三「**验收必须是可跑的命令** —— 『我检查过了』不算」
# 定位:   新增 `_run_spec_acceptance_paths_gate`：**硬门禁** ——
#         它查的是 `specs/**/*.md` 的 `→ 验收:` 行点到的脚本**在不在仓库里**。
#         触发它的是 2026-10-01 实测的 **2 例**（`capability_gap.py`、`probe_results_api_surface.py`
#         原先只在工作区根 ⇒ **换机器 / CI 跑不了**）。
#         ⚠ **便携性**：specs 目录不在本机时，那个脚本**自己 SKIP 并 exit 0**
#           ⇒ 别的机器上不会无条件红（这一点由它的契约测试 `test_missing_specs_root_skips` 守着）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────
def _run_spec_acceptance_paths_gate() -> dict[str, object]:
    """@brief 跑验收命令可跑性门禁（`scripts/check_spec_acceptance_paths.py`）。"""
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_spec_acceptance_paths.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=180, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "output": "验收命令可跑性门禁无法执行: %s" % exc}
    status = "pass" if proc.returncode == 0 else "fail"
    return {"status": status, "output": (proc.stdout or "") + (proc.stderr or "")}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把交付报告数字新鲜度接进发布前检查）+ Python 标准库 `subprocess`
# 文件:   `scripts/check_report_freshness.py`（本门禁的实现）
# 定位:   新增 `_run_report_freshness_gate`：**硬门禁** ——
#         它查的是 `docs/harvest-report.md` 里「偏离上游：N 个文件 / +N 行 / -N 行 · N 个 commit」
#         那行**是否与 git 实际相符**。触发它的是 2026-10-01（轮 54）实测的
#         **8 倍文件数 / 20 倍行数 / 10 倍 commit 数** 偏差 ——
#         此前 `REQUIRED_ABILITY_FILES` **只查这两份报告存在、不查数字**。
#         ⚠ **便携性**：报告没有那行、或拿不到 `origin/main` ⇒ 它**自己 SKIP 并 exit 0**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────
def _run_report_freshness_gate() -> dict[str, object]:
    """@brief 跑交付报告数字新鲜度门禁（`scripts/check_report_freshness.py`）。"""
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_report_freshness.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=180, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "output": "交付报告数字新鲜度门禁无法执行: %s" % exc}
    status = "pass" if proc.returncode == 0 else "fail"
    return {"status": status, "output": (proc.stdout or "") + (proc.stderr or "")}


def _run_python_syntax_gate() -> dict[str, object]:
    """@brief 跑 `.py` 语法门禁（`scripts/check_python_syntax.py`。

    ★★ 为什么有这一道：本会话**同一处踩了五次** ——
       新建文件时把**来源块写进了头部三引号里面**（忘了闭合）⇒
       Python 报的是 `SyntaxError: invalid character '★'`（**错误信息指向星号、不是真因**）。
       ★ 而 `ast.parse` 一次抓住**所有**语法错，报的是真因的名字
       （`unterminated triple-quoted string literal`）。
    """
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_python_syntax.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=180, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "output": ".py 语法门禁无法执行: %s" % exc}
    status = "pass" if proc.returncode == 0 else "fail"
    return {"status": status, "output": (proc.stdout or "") + (proc.stderr or "")}


def _run_server_side_tools_gate() -> dict[str, object]:
    """@brief 跑**服务端侧工具名门禁**（`tools/check_server_side_tools.py`）。

    ★★ 为什么有这一道（★ 2026-10-03 轮 449 / 事实 364）：
      ★ 本仓的工具声明**有两条路** ——
        ★ **ToolSpec 路**（★ 而它**过五统一门禁**）与
        ★★ **`server.py` 装饰器路**（`@mcp.tool`）—— ★ **而它不过那套门禁** ⚠
      ⇒ ★ 故至少要把**静态可判**的那一条看住：
        ★★ **两条路上的 `solidworks_*` 工具名不许重名**（★ 重名会让后注册的**遮掉**先注册的）✓
    ⚠ 它不能代替 `tool_registry` 那套门禁 —— ★ 只是把装饰器路也**纳入可见范围**。
    """
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "tools" / "check_server_side_tools.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=300, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "output": "服务端侧工具名门禁无法执行: %s" % exc}
    status = "pass" if proc.returncode == 0 else "fail"
    return {"status": status, "output": (proc.stdout or "") + (proc.stderr or "")}


def _run_judge_preflight_gate() -> dict[str, object]:
    """@brief 跑**判据前置门禁**（`tools/check_judge_preflight.py`）。

    ★★ 为什么有这一道：★ 上一轮**五次**出现同一形态 ——
    ★ **能力好好的，而它看起来坏了**，★ 而**每一次的错都在判据**：
    选区不干净 / 算例类型错 / 算例名错 / 名单不全 / 间歇性不稳。
    ⇒ ★★ **判据本身也是被测对象** —— 它必须**先被验过**，才能拿去判别人。
    ★ 登记表：`docs/judge-registry.json`（★ 每条记：判据 / 它在哪 / 它的**已知成功场景** / 那份 evidence）。
    ★ 而它**自己有负例自证**：`tests/test_judge_preflight_gate.py`（事实 62）。
    """
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "tools" / "check_judge_preflight.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=300, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "output": "判据前置门禁无法执行: %s" % exc}
    status = "pass" if proc.returncode == 0 else "fail"
    return {"status": status, "output": (proc.stdout or "") + (proc.stderr or "")}


def _run_inject_binding_gate() -> dict[str, object]:
    """@brief 跑**注入绑定门禁**（`tools/check_inject_binding.py`）。

    ★★ 为什么有这一道：★ 2026-10-03（轮 461）**真机撞出来**的一个真缺陷 ——
    走 MCP 工具调 `solidworks_part_mass_properties` 报
    `TypeError: mass_properties() missing 1 required positional argument: 'model'`；
    ★ 根因是那条 ToolSpec **漏了 `inject="model"`**（★ 调用时不注入文档 ⇒ 包装拿到 0 个实参）。
    ★★ 而**既有的 `check_param_binding.py` 抓不到它** —— 那道门禁判「**声明了的**参数名 ∈ 形参」，
    而**不判「注入的对象覆盖了包装的必需形参」**。
    ⇒ ★ 全扫一遍：**221 个 ToolSpec 里有 16 个漏**（★ 含草图 / 拉伸 / 圆角 / 倒角 /
      工程图读 / 属性读 —— ★ 都是**基本功能**）⇒ 已修 ✓
    ★ 而它**自己有负例自证**：`tests/test_inject_binding_gate.py`（事实 62）✓
    """
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "tools" / "check_inject_binding.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=300, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "output": "注入绑定门禁无法执行: %s" % exc}
    status = "pass" if proc.returncode == 0 else "fail"
    return {"status": status, "output": (proc.stdout or "") + (proc.stderr or "")}


def _run_inout_array_audit_gate() -> dict[str, object]:
    """@brief 跑**`in,out` 数组形参审计的契约测试**。

    ★★ 为什么有这一道：★ 2026-10-03（轮 514-515）—— 那份审计
    （`tools/audit_inout_array_params.py` ⇒ `output/inout-array-params.json`）
    是**事实 128/129 的落地产物**：它用**第 4 套签名源**（类型库方法表）查出
    **62 条 `in,out` 数组形参**（涉及本仓调用过的 **496** 个成员名）。

    ⚠★ **而本轮查明：它自己没有被任何门禁引用** —— 只有 `scripts/audit_byref_args.py`
    的**注释**提到了它（★ 当年把结论写回了口径段）。
    ⇒ ★★ **故它"跑过一次"之后就再也不会被跑** ⇒ ★ 产物会**悄悄过期** ⚠

    ★ 本道门禁把它从「跑过一次」变成「**发布时必查**」：
    跑 `tests/test_inout_array_audit_contract.py`（★ 5 条 · 纯静态 · ~0.1s），
    断言**产物结构在**、**扫了多个库**、**记录字段齐**、
    ★ **审计自己那句「不做结论」还在**（★ 那是它的安全边界）、**产物内部自洽**。

    ★ 它**自己有负例自证**：★ 把 `output/inout-array-params.json` 挪走再跑本道 ⇒ 必然 fail
    （★ 事实 62：一个门禁「写了」不等于它「有效」）。
    """
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"), "-m", "pytest", "-q",
             str(ROOT / "tests" / "test_inout_array_audit_contract.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=300, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "output": "in,out 数组审计契约无法执行: %s" % exc}
    status = "pass" if proc.returncode == 0 else "fail"
    return {"status": status, "output": (proc.stdout or "") + (proc.stderr or "")}


def _run_typelib_tables_gate() -> dict[str, object]:
    """@brief 跑**出厂类型库对照门禁**（`tools/check_typelib_tables.py`）。

    ★★ 为什么有这一道：★ 能力层里有**手抄的成员表**
    （`_ERRORCODE_MEMBERS` / `_REFGEOM_MEMBERS` / `OFFICIAL_LOAD_SIGNATURES`），
    ★ 而**手抄就会漏**。真例（轮 415）：`_ERRORCODE_MEMBERS` 漏了
    `AddTemperature` / `AddRemoteLoad` ⇒ 它们**从不补 `ByRef ErrorCode`** ⇒
    `DISP_E_PARAMNOTOPTIONAL` ⇒ ★★ **两条好能力看起来调不通**。
    ★ 而定位它用的是**出厂类型库**（铁律 4 的最高裁决者）——
    ★★ 它是**托管程序集**，★ 可以用 **PowerShell 的 .NET 元数据反射**
    **离线读**（零 Python 依赖、不需要 SW 在跑）。
    ⚠ 便携性：拿不到那个 DLL ⇒ 脚本自己报 `[SKIP]` 并 exit 0。
    """
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "tools" / "check_typelib_tables.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=300, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "output": "出厂类型库对照门禁无法执行: %s" % exc}
    status = "pass" if proc.returncode == 0 else "fail"
    return {"status": status, "output": (proc.stdout or "") + (proc.stderr or "")}


def _run_undefined_names_gate() -> dict[str, object]:
    """@brief 跑**未定义名门禁**（`scripts/check_undefined_names.py`）。

    ★★ 为什么有这一道：★ `_run_python_syntax_gate` 只做 `ast.parse` ——
    **语法合法、名字没解析** ⇒ 抓不到 `NameError` 隐患。
    ★ 触发它的是**轮 403 真机抓到的真 bug**：`export_to_image` 里用了 `out_i4()`
    而 `sw_export.py` **漏了导入** ⇒ 一调就
    `NameError: name 'out_i4' is not defined`（★ 而当时 19 道门禁**全绿**）。
    ★★ 本道第一次跑就抓到 **31 处**（7 个名字 / 23 个文件），其中
    `dismiss_residual_dialogs` **21 处**（8 个 tools 文件没导入就用）、
    `time` 3 处、`SW_PID` 1 处 —— ★ 全是**同一种形态：改名之后没跟着改**。
    ⚠ 它用**保守判据**（判"整个文件都没绑定过"）⇒ ★ 宁可漏、不要噪音；
    ★ 而"运行期动态注入全局"（`globals().update(...)`）与 `import *` 的文件**整份跳过**
    （★ 真例：`mcp-server/server.py` 的 `globals().update(exports)` ——
    ★ 不跳过的话会在那一个文件上假阳性 **300+ 处**）。
    """
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_undefined_names.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=180, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "output": "未定义名门禁无法执行: %s" % exc}
    status = "pass" if proc.returncode == 0 else "fail"
    return {"status": status, "output": (proc.stdout or "") + (proc.stderr or "")}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把签名审计表新鲜度接进发布前检查）+ Python 标准库 `subprocess`
# 文件:   `scripts/check_signature_audit_freshness.py`（本门禁的实现）
# 定位:   新增 `_run_signature_audit_freshness_gate`：**硬门禁** ——
#         它按 `docs/signature-audit.md` 的**逐模块清单**实跑 `scripts/audit_call_arity.py`
#         并逐项比对调用点数。触发它的是 2026-10-01（轮 55）实测的 **3/6 模块失真**
#         （`drawing_workflow` 140→198 · `sw_simulation` 34→44 · `sw_topology` 45→49）——
#         与 `harvest-report` 是**同型**缺口（只查存在、不查数字），只是这份还能**实跑复核**。
#         ⚠ **便携性**：拿不到 `D:\AI\SW\_raw` 或模块文件 ⇒ 它**自己 SKIP 并 exit 0**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────
def _run_signature_audit_freshness_gate() -> dict[str, object]:
    """@brief 跑签名审计表新鲜度门禁（`scripts/check_signature_audit_freshness.py`）。"""
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_signature_audit_freshness.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=600, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "output": "签名审计表新鲜度门禁无法执行: %s" % exc}
    status = "pass" if proc.returncode == 0 else "fail"
    return {"status": status, "output": (proc.stdout or "") + (proc.stderr or "")}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把 A8 状态摘要的新鲜度接进发布前检查）+ Python 标准库 `subprocess`
# 文件:   `scripts/check_digest_freshness.py`（本门禁的实现）
# 定位:   新增 `_run_digest_freshness_gate`：**硬门禁** ——
#         把 `AGENTS.md §一 A8`「报告写明并入了什么 / 仍空缺什么 / 为什么」做成**可跑的那一半**。
# ⚠ 为什么必须是硬门禁：`docs/harvest-digest.md` 是**生成物**，
#   一旦它与真源（`capabilities.yaml` / `git log` / 门禁栈）分叉，报告就在**说假话** ——
#   而这类分叉**不会自己暴露**（本项目已多次记录「文档与代码不符比没有文档更糟」）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数
# ─────────────────────────────────────────────────────────────────────
def _run_digest_freshness_gate() -> dict[str, object]:
    """@brief 跑交付状态摘要的新鲜度门禁（`scripts/check_digest_freshness.py`）。"""
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_digest_freshness.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=600, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "output": "交付摘要新鲜度门禁无法执行: %s" % exc}
    status = "pass" if proc.returncode == 0 else "fail"
    return {"status": status, "output": (proc.stdout or "") + (proc.stderr or "")}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把 A6 许可红线接进发布前检查）+ Python 标准库 `subprocess`
# 文件:   `scripts/check_license_redlines.py`（本门禁的实现）
# 定位:   新增 `_run_license_redlines_gate`：**硬门禁** ——
#         把 `AGENTS.md §一 A6`「逐文件对照许可判定表」做成**可跑的那一半**。
#         三条判据：① 点名第三方 ⇒ 许可须含白名单词（MIT / Apache-2.0）；
#         ② **已知 Apache-2.0 的来源** ⇒ 许可须**明写 Apache**（不能只写「本仓库 MIT」）；
#         ③ 声明 Apache-2.0 ⇒ `THIRD-PARTY-NOTICES.md` 必须存在。
#         ⚠ 它判**声明是否自洽/越界**，**不判声明是否属实**（后者是语义判断，靠人核）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────
def _run_license_redlines_gate() -> dict[str, object]:
    """@brief 跑 A6 许可红线门禁（`scripts/check_license_redlines.py`）。"""
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_license_redlines.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=300, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "output": "A6 许可红线门禁无法执行: %s" % exc}
    status = "pass" if proc.returncode == 0 else "fail"
    return {"status": status, "output": (proc.stdout or "") + (proc.stderr or "")}


def _run_param_binding_gate() -> dict[str, object]:
    """跑**参数绑定**门禁（`scripts/check_param_binding.py`）。

    判据：每个工具声明的参数名**要么在目标函数的形参表里、要么在 `param_alias` 里**；
    `param_alias` 指向的目标名必须真的存在；`inject` 必须是 `RESOLVERS` 的键。

    ★ 触发它的是 **2026-10-01 两次真实事故**（`magnitude_n` / `study_name` 都漏写别名
    ⇒ 真机 `TypeError`）—— ★ 而"记下来"不等于"下次不犯"，所以把它**机器化**。
    """
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_param_binding.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=180, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "reason": f"检查**无法启动**（超时/OSError）: {exc}"}
    return {
        "status": "pass" if proc.returncode == 0 else "fail",
        "output": (proc.stdout or "").strip()[-1500:],
    }


def _run_member_name_gate() -> dict[str, object]:
    """跑成员名存在性门禁（scripts/check_member_names.py）。

    只查**名字在官方反射里查得到**，不查 arity ——
    arity 由 audit_call_arity.py 负责，两道门禁分工不同。
    """
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_member_names.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=180, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "reason": f"检查**无法启动**（超时/OSError）: {exc}"}
    return {
        "status": "pass" if proc.returncode == 0 else "fail",
        "output": (proc.stdout or "").strip()[-1500:],
    }


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把「**别去调已证到不了的成员**」接进发布前检查）
# 文件:   `scripts/check_unreachable_members.py`（本门禁的实现）
# 定位:   新增 `_run_unreachable_members_gate`：**硬门禁**。
#   ★ 2026-10-03（轮 579）★ 它与既有两道**分工不同**（★ 三道互补）：
#     · `check_member_names.py`              —— 判「名字在**某个**接口里存在」
#     · `check_interface_member_ownership.py` —— 判「成员属于**这个**接口」
#     · **本道**                              —— 判「这个名字在本机**调不调得动**」
#       ★ 依据：一份**每条带真机证据**的 deny 名单（事实 456 · 428 等）
#   ★★ **为什么接进硬门禁**（★ 事实 40 的教训）：★ **一个存在但没人用的守卫，
#     与没有守卫等价 —— 且更糟**（让人以为防住了）。
#   ★ 而它**第一次跑就逼出了自己的契约**：命中了 3 处，★ 而那 3 处是**事实 428 的取证代码**
#     ⇒ ★ 故补了**带理由的取证豁免**（`ALLOWED`），★ **而新增的命中会被拦**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#: ★ 2026-10-03（轮 594）接进：**A4** —— `level: verified` 必须带**我们自己的运行证据**。
#:   实测：95 条 verified、**0 条无 evidence**（数据干净）——
#:   而**之前没有任何门禁在守它** ⇒ 危险在于「数据干净、而没有东西保证它继续干净」。
#: ★ 2026-10-03（轮 600）接进：**「后端到不了」名单必须写明依据**。
#:   任务书逐字：那三族要「**写明依据并单列**」——
#:   ★ 而轮 599 才刚把那个桶接进台账 ⇒ 名单内容还没人守（事实 40：没人查的桶等于没桶）。
def _run_backend_limited_completeness_gate() -> dict[str, object]:
    """跑名单**完整性**门禁（scripts/check_backend_limited_completeness.py）。"""
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_backend_limited_completeness.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=180, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "reason": f"检查**无法启动**（超时/OSError）: {exc}"}
    return {
        "status": "pass" if proc.returncode == 0 else "fail",
        "output": (proc.stdout or "").strip()[-1500:],
    }


def _run_backend_limited_gate() -> dict[str, object]:
    """跑「后端到不了」名单的证据门禁（scripts/check_backend_limited_evidence.py）。"""
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_backend_limited_evidence.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=180, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "reason": f"检查**无法启动**（超时/OSError）: {exc}"}
    return {
        "status": "pass" if proc.returncode == 0 else "fail",
        "output": (proc.stdout or "").strip()[-1500:],
    }


def _run_verified_evidence_gate() -> dict[str, object]:
    """跑 A4 证据门禁（scripts/check_verified_evidence.py）。"""
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_verified_evidence.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=180, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "reason": f"检查**无法启动**（超时/OSError）: {exc}"}
    return {
        "status": "pass" if proc.returncode == 0 else "fail",
        "output": (proc.stdout or "").strip()[-1500:],
    }


def _run_unreachable_members_gate() -> dict[str, object]:
    """跑可达性门禁（scripts/check_unreachable_members.py）。"""
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_unreachable_members.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=180, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "reason": f"检查**无法启动**（超时/OSError）: {exc}"}
    return {
        "status": "pass" if proc.returncode == 0 else "fail",
        "output": (proc.stdout or "").strip()[-1500:],
    }
# ⚠⚠ **为什么现在才接**（2026-10-01 轮 70）：该门禁**早就存在**，却**不在硬门禁列表里**
#   ⇒ 它**红着也没人知道**。实测时它报：
#   ```
#   [FAIL] 工作区根有 1 个会遮蔽依赖包的文件/目录：mcp ← D:\AI\SW\mcp.py
#   ```
#   后果很实在：以该工作区为 CWD 的 Python 进程里 `import mcp` 拿到的是**那个本地文件**
#   ⇒ `No module named 'mcp.server'; 'mcp' is not a package`。
#   ★ **一个存在但没人跑的门禁，与没有门禁等价** —— 这次是同一教训的**另一个面**：
#     门禁在，但**没接线**。
# ⚠ **便携性**：工作区不在（别的机器）⇒ 该脚本自己 `[SKIP]` 并 exit 0 ⇒ **可以无条件接线**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数
# ─────────────────────────────────────────────────────────────────────
def _run_workspace_shadowing_gate() -> dict[str, object]:
    """@brief 跑工作区遮蔽门禁（`scripts/check_workspace_shadowing.py`）。"""
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_workspace_shadowing.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=180, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "output": "工作区遮蔽门禁无法执行: %s" % exc}
    status = "pass" if proc.returncode == 0 else "fail"
    return {"status": status, "output": (proc.stdout or "") + (proc.stderr or "")}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**元门禁**：门禁接线自检）+ Python 标准库 `subprocess`
# 文件:   `scripts/check_gate_wiring.py`（本门禁的实现）
# 定位:   新增 `_run_gate_wiring_gate`：**硬门禁**。
# ⚠⚠ **为什么需要它**（2026-10-01 轮 70 实测暴露）：`check_workspace_shadowing.py`
#   **早就存在，却从没被调用** —— 而它当时**正红着**（工作区根的 `mcp.py` 遮蔽 `mcp` 包）。
#   ★ **一个存在但没人跑的门禁，与没有门禁等价** —— 「接线」这一步此前**只靠人记**。
#   ⇒ 本门禁把「接线」也变成机器判据：每个 `scripts/check_*.py` 必须**被调用**，
#     或登记进 `docs/gate-wiring-exemptions.json`（带非空 reason + evidence）。
# ⚠ **它自己也接受同一条检查**（不自外于规则）—— 否则就是同一个笑话。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数
# ─────────────────────────────────────────────────────────────────────
def _run_gate_wiring_gate() -> dict[str, object]:
    """@brief 跑门禁接线元门禁（`scripts/check_gate_wiring.py`）。"""
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_gate_wiring.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=180, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "output": "门禁接线元门禁无法执行: %s" % exc}
    status = "pass" if proc.returncode == 0 else "fail"
    return {"status": status, "output": (proc.stdout or "") + (proc.stderr or "")}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把「报告判据编号一致性」接进发布前检查）+ Python 标准库 `subprocess`
# 文件:   `scripts/check_report_criteria_alignment.py`（本门禁的实现）
# 定位:   新增 `_run_report_criteria_alignment_gate`：**硬门禁**。
# ⚠⚠ **为什么需要**（2026-10-01 轮 82 实测）：`harvest-report.md §四` 的逐条自评
#   用了**另一套编号**（**同名不同事**）—— 旧表的「A3」实为 A5、「A5」实为 A6、
#   「A7」实为 A8，还混入「官方 API 覆盖」这条**非 A 判据**的行，**并缺 A1/A9/A10**。
#   ⇒ 读者拿 §四 去对 `AGENTS.md §一` **对不上** —— 而那正是 **A8** 要的东西（「报告写明…」）
#     **自己没做到**。同类问题此前已犯过一次（旧 §一 的「A1」指的是官方 API 覆盖）。
#   ★ **靠人记必然再漂** ⇒ 把「编号一致」变成机器判据。
# ⚠ **便携性**：`AGENTS.md` 在工作区（不在本仓库）⇒ 拿不到时该脚本**自己 SKIP 并 exit 0**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数
# ─────────────────────────────────────────────────────────────────────
def _run_report_criteria_alignment_gate() -> dict[str, object]:
    """@brief 跑报告判据编号门禁（`scripts/check_report_criteria_alignment.py`）。"""
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_report_criteria_alignment.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=180, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "output": "报告判据编号门禁无法执行: %s" % exc}
    status = "pass" if proc.returncode == 0 else "fail"
    return {"status": status, "output": (proc.stdout or "") + (proc.stderr or "")}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把「负例输入自证」审计接进发布前检查）+ Python 标准库 `subprocess`
# 文件:   `scripts/check_negative_input_selfproof.py`（本门禁的实现；**它扫的是 `tools/`**）
# 定位:   新增 `_run_negative_input_selfproof_gate`：**硬门禁**。
# ⚠⚠ **为什么需要**（2026-10-01 轮 84 撞见、轮 85 固化）：
#   `tools/probe_skip_semantics.py` 里有个用例「**用正则把逐模块表删掉**来造坏文档」——
#   而**那条正则根本没匹配上** ⇒ 产出的"坏文档"**仍带完整的表** ⇒ 门禁照常 `[PASS]`，
#   **而它被当成了"修好了"的证据**（轮 83 的结论就建立在这个假用例上）。
#   ★ **一个假用例比没有用例更糟** —— 它给出一份**看起来验过的**证据。
#   ⇒ 本门禁把其中**可机器判的那一类**钉住：
#     **凡「用变换（`re.sub`/`replace`）造负例输入」的地方，必须在前后若干行内自证变换生效**
#     （比对不等 / 打印前后字节数 / 断言）。
# ⚠ **覆盖面**：它**只**判「变换没生效」这一类；类型 2/3/4
#   （坏的理由不对 / 负例与正例同结果 / 断言打在恒定字段）**需要语义判断，未判** ——
#   门禁自己在 `[PASS]` 时也会把这条声明打出来（**不夸大覆盖面**）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数
# ─────────────────────────────────────────────────────────────────────
def _run_negative_input_selfproof_gate() -> dict[str, object]:
    """@brief 跑负例输入自证门禁（`scripts/check_negative_input_selfproof.py`）。"""
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_negative_input_selfproof.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=180, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "output": "负例输入自证门禁无法执行: %s" % exc}
    status = "pass" if proc.returncode == 0 else "fail"
    return {"status": status, "output": (proc.stdout or "") + (proc.stderr or "")}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（发布门禁的一个检查项）
# 文件:   `scripts/check_enum_values_vs_reflection.py`（本门禁的实现）
# 定位:   新增 `_run_enum_values_gate`：**硬门禁**。
# ⚠⚠ **为什么需要**（2026-10-01 轮 106）：
#   连着两轮的错**都在「值」上，不在「名字」上**——
#   023：螺旋线枚举凭记忆写反（`height_and_pitch` 1↔2）；
#   024：`swSketchChamfer_DistanceDistance` 两源冲突（md −1 / 反射 1）。
#   ★ **而当时所有门禁都抓不到** —— 它们查的是「名字在不在官方清单里」，
#     **没有一个查「值对不对」**。⇒ 本门禁补这个覆盖缺口。
# ⚠ **覆盖面**：它判「代码里写了官方成员名的**值**是否与出厂反射一致」，
#   并**顺带报出两源冲突**（冲突**不判失败** —— 铁律 4 已定取反射）。
#   它**不判**「成员名写的是不是对的枚举」「值的语义对不对」。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数
# ─────────────────────────────────────────────────────────────────────
def _run_enum_values_gate() -> dict[str, object]:
    """@brief 跑枚举值门禁（`scripts/check_enum_values_vs_reflection.py`）。"""
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "scripts" / "check_enum_values_vs_reflection.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=180, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "output": "枚举值门禁无法执行: %s" % exc}
    status = "pass" if proc.returncode == 0 else "fail"
    return {"status": status, "output": (proc.stdout or "") + (proc.stderr or "")}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把接口归属**诊断**接进发布前检查）
# 文件:   `scripts/check_interface_member_ownership.py`（判「成员在**这个**接口上存在」）
#         `C:\swapi\types\<接口>\<成员>.md`（官方类型表，**机器本地数据源**）
# 定位:   新增 `_run_interface_ownership_probe`：⚠⚠ **这是**诊断**，不是门禁** ——
#         与同文件里的 `_run_*_gate` **有三个差别**：
#
#           **① 不 `raise`。** 映射表来自**官方文本匹配**（第 41 轮现状：31 唯一
#              （自动 24 + 人工确证 7）/ 0 歧义 / 4 未映射），**有洞**。一个覆盖不全的
#              门禁会让人以为防住了（第 40 轮的教训）⇒ 它报 `[HIT]` 时**值得看**，
#              但**不拦发布**。
#
#           **② 假绿必须可见。** 该脚本在「检查量为 0」时**返回非 0**（与
#              `audit_byref_args.py` 的「≥300」同源）。本探针把它标成
#              `checked_nothing` —— **不 raise，但绝不静默**。
#
#           **③ 数据源缺失不算违规。** `C:\swapi` 不在时脚本报 `[SKIP]` 并退出 0
#              （**缺数据源与检查失败是两件事**）。
#
#          ⚠ 检测 `[HIT]` 必须**按行首**匹配：该脚本的**说明文字里**也写着「报 `[HIT]` 时
#            值得看」，用 `in` 判会**误报**（本轮踩过）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ────────────────────────────────────────────────────────────────────
def _run_interface_ownership_probe() -> dict[str, object]:
    """@brief 跑接口归属**诊断**（详细定位见上方来源块）。"""
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_interface_member_ownership.py")],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=180, cwd=str(ROOT), stdin=subprocess.DEVNULL,
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    # ⚠ **按行首**判 `[HIT]` —— 该脚本的说明文字里也写着「报 `[HIT]` 时值得看」，
    #   用 `"[HIT]" in output` 会**误报**（本轮踩过：明明 `[OK]` 却报 hits）。
    hits = any(l.lstrip().startswith("[HIT]") for l in output.splitlines())
    skipped = any(l.lstrip().startswith("[SKIP]") for l in output.splitlines())
    # 退出码非 0 且不是 SKIP ⇒ 就是「检查量为 0」那条假绿守卫
    checked_nothing = proc.returncode != 0 and not skipped
    if skipped:
        status = "skipped"
    elif checked_nothing:
        status = "checked_nothing"
    elif hits:
        status = "hits"
    else:
        status = "clean"
    return {
        "status": status,
        "returncode": proc.returncode,
        "hits": hits,
        "checked_nothing": checked_nothing,
        "output": output,
    }


def _gate_detail(res: dict) -> str:
    """@brief 从一道门禁的结果里取**它能给的最有信息量的那一句**（供返回体的 `gate_details`）。

    :param res: 某个 `_run_*` 的返回值（应为 dict）。
    :returns: **非空**字符串。优先级：`output`（说的是「扫了多少 / 跳过了什么」）>
        `reason`（说不出别的时，至少说明**为什么没跑**）> `status`。

    ⚠ 为什么优先级是 `output` 而不是 `status`：**`status: pass` 与「没覆盖任何东西」在输出上
    长得一模一样** —— 而「判据没覆盖」和「没有问题」是两回事（轮 190 的定则）。
    ★ 所以能拿到 `output` 就一定要拿到；`output` 是空的（有些门禁的 pass 分支不打印）时，
    退回 `reason`/`status`，**但绝不返回空串**（空串会让读者以为"没有明细"）。
    """
    for key in ("output", "reason", "status"):
        v = res.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()[:700]
    return "（该门禁没给 output/reason/status ⇒ 明细缺失，**按未知对待**）"


def run_release_check() -> dict[str, object]:
    """@brief 校验应用版本、能力真源和必需发布文件。"""
    ui_version = _version(ROOT / "apps/workbench-ui/package.json", r'"version"\s*:\s*"([^"]+)"')
    tauri_version = _version(ROOT / "apps/workbench-ui/src-tauri/tauri.conf.json", r'"version"\s*:\s*"([^"]+)"')
    cargo_version = _version(ROOT / "apps/workbench-ui/src-tauri/Cargo.toml", r'(?m)^version\s*=\s*"([^"]+)"')
    app_version = _version(ROOT / "apps/workbench-ui/src/App.tsx", r'const APP_VERSION\s*=\s*"([^"]+)"')
    if len({ui_version, tauri_version, cargo_version, app_version}) != 1:
        raise AssertionError(f"版本不一致: npm={ui_version}, tauri={tauri_version}, cargo={cargo_version}, app={app_version}")
    manifest = json.loads((ROOT / "capabilities.yaml").read_text(encoding="utf-8"))
    capabilities = manifest.get("capabilities", [])
    ids = [item.get("id") for item in capabilities]
    if len(ids) != len(set(ids)) or len(ids) < 10:
        raise AssertionError("能力清单 ID 重复或数量不足")
    required = [
        "SKILL.md",
        "README.md",
        "capabilities.yaml",
        "scripts/stability_regression.py",
        "scripts/release_check.py",
        "scripts/dfm_review.py",
        *REQUIRED_ABILITY_FILES,
    ]
    missing = [item for item in required if not (ROOT / item).is_file()]
    if missing:
        raise AssertionError("发布文件缺失: " + ", ".join(missing))
    # 来源可追溯性门禁：**放在 bundled-skill 检查之前**。
    # 原因：bundled-skill 检查在本工作副本上是「既有失败」（上游基线同样失败），
    #   放后面会被它先抛的异常挡住，provenance 永远不执行 —— 一个跑不到的
    #   门禁等于没有门禁。
    provenance = _run_provenance_gate()
    if provenance.get("status") == "fail":
        raise AssertionError(
            "来源可追溯性门禁未通过（新增代码缺少出处）：\n"
            + str(provenance.get("output", ""))
        )
    markers = _run_marker_gate()
    if markers.get("status") == "fail":
        raise AssertionError(
            "diff 记号残留检查未通过：\n" + str(markers.get("output", "")))
    # ⚑ 成员名门禁放在 provenance 之后、bundled 校验之前 ——
    #   它需要读 6 份反射清单（最慢的一道），但它拦下的是
    #   「代码里写了官方不存在的成员」这种必然在运行时炸的问题。
    member_names = _run_member_name_gate()
    if member_names.get("status") == "fail":
        raise AssertionError(
            "成员名门禁未通过（代码里用了官方不存在的成员名）：\n"
            + str(member_names.get("output", "")))
    # ⚑ **可达性门禁**（硬门禁，2026-10-03 轮 579 接进）：前三道「名字」门禁判的是
    #   「**存在 / 属于哪个接口**」，而**本道判「在本机调不调得动」** ——
    #   依据一份**每条带真机证据**的 deny 名单（事实 456 的 `IMathUtility` 族 ·
    #   事实 428 的 `InsertWeldmentCutList2` …）。
    #   ★ 接进来的理由（事实 40）：**存在但没人用的守卫，与没有守卫等价、且更糟**。
    backend_full = _run_backend_limited_completeness_gate()
    if backend_full.get("status") == "fail":
        raise AssertionError(
            "名单完整性门禁未通过（★ 该进「后端到不了」的漏了）：\n"
            + str(backend_full.get("output", "")))
    backend_lim = _run_backend_limited_gate()
    if backend_lim.get("status") == "fail":
        raise AssertionError(
            "「后端到不了」名单的证据门禁未通过（任务书：写明依据并单列）：\n"
            + str(backend_lim.get("output", "")))
    verified_ev = _run_verified_evidence_gate()
    if verified_ev.get("status") == "fail":
        raise AssertionError(
            "证据门禁未通过（A4：`verified` 必须带运行证据）：\n"
            + str(verified_ev.get("output", "")))
    unreachable = _run_unreachable_members_gate()
    if unreachable.get("status") == "fail":
        raise AssertionError(
            "可达性门禁未通过（代码里调了**已证到不了**的成员）：\n"
            + str(unreachable.get("output", "")))
    # ⚑ **工作区遮蔽门禁**（硬门禁）：工作区根若有与 `server.py` 依赖包同名的 `.py`/目录，
    #   以该工作区为 CWD 的 Python 进程就会 `import` 到**那个本地文件**而不是真包
    #   （实测：`D:\AI\SW\mcp.py` 遮蔽 `mcp` ⇒ `No module named 'mcp.server'`）。
    #   ⚠⚠ **它此前不在这个列表里** ⇒ **红着也没人知道**（轮 70 实测才发现）。
    #   ★ 一个存在但**没人跑**的门禁，与没有门禁等价。
    shadowing = _run_workspace_shadowing_gate()
    if shadowing.get("status") == "fail":
        raise AssertionError(
            "工作区遮蔽门禁未通过（工作区根有会遮蔽依赖包的文件/目录）：\n"
            + str(shadowing.get("output", "")))
    # ⚑ **门禁接线元门禁**（硬门禁）：每个 `scripts/check_*.py` 必须被本文件调用，
    #   或登记进 `docs/gate-wiring-exemptions.json`（带非空 reason + evidence）。
    #   ⚠ 轮 70 实测：`check_workspace_shadowing.py` 早就存在却**从没被调用**，
    #     而它当时**正红着** ⇒ ★ 一个存在但没人跑的门禁，与没有门禁等价。
    wiring = _run_gate_wiring_gate()
    if wiring.get("status") == "fail":
        raise AssertionError(
            "门禁接线元门禁未通过（有门禁没被接线也没豁免）：\n"
            + str(wiring.get("output", "")))
    # ⚑ **报告判据编号门禁**（硬门禁）：`docs/harvest-report.md §四` 的逐条自评
    #   必须与 `AGENTS.md §一` 的 **A1–A10 逐条对齐**（编号、条数、含义三样）。
    #   ⚠⚠ **为什么需要**（2026-10-01 轮 82 实测）：该节此前用的是**另一套编号**
    #     （**同名不同事**）—— 旧表的「A3」实为 A5、「A5」实为 A6、「A7」实为 A8，
    #     还混入「官方 API 覆盖」这条**非 A 判据**的行，**并缺 A1/A9/A10**。
    #     ⇒ 读者拿 §四 去对 §一 **对不上** —— 而那正是 **A8** 要的东西（「报告写明…」）
    #       **自己没做到**。同类问题此前已犯过一次（旧 §一 的「A1」指官方 API 覆盖）。
    #     ★ **靠人记必然再漂** ⇒ 把「编号一致」变成机器判据。
    #   ⚠ **便携性**：`AGENTS.md` 在工作区（不在本仓库）⇒ 拿不到时它**自己 SKIP 并 exit 0**。
    crit_align = _run_report_criteria_alignment_gate()
    if crit_align.get("status") == "fail":
        raise AssertionError(
            "报告判据编号门禁未通过（§四 的自评编号与 AGENTS.md §一 不一致）：\n"
            + str(crit_align.get("output", "")))
    # ⚑ **负例输入自证门禁**（硬门禁）：`tools/` 下探针里「用变换造负例输入」的地方，
    #   必须**自证变换生效** —— 否则那个"坏输入"等于真输入，**用例空转却显示通过**。
    #   ⚠⚠ 触发它的是 2026-10-01 轮 84 撞见的**假用例**：删逐模块表的正则**没匹配上**
    #     ⇒ 门禁照常 `[PASS]`，而它被当成了"修好了"的证据（轮 83 的结论建立在此）。
    #   ★ **假用例比没有用例更糟**。同族见已知事实 62（门禁写了不等于有效），只是发生在**测试**上。
    selfproof = _run_negative_input_selfproof_gate()
    if selfproof.get("status") == "fail":
        raise AssertionError(
            "负例输入自证门禁未通过（探针里的「坏输入」可能是空转的）：\n"
            + str(selfproof.get("output", "")))
    # ⚑ **枚举值门禁**（硬门禁，轮 106）：补「**值级**」覆盖缺口。
    #   ⚠ 旧门禁查的是「名字在不在官方清单里」，**不查「值对不对」** ——
    #     023（枚举凭记忆写反）与 024（两源冲突）连着两轮的错**都从那里漏过去**。
    #   本门禁把「代码里写了官方成员名的值」与**出厂反射**逐条比对，
    #   并**顺带报出两源冲突**（冲突不判失败：铁律 4 已定取反射）。
    enum_values = _run_enum_values_gate()
    if enum_values.get("status") == "fail":
        raise AssertionError(
            "枚举值门禁未通过（代码里的官方枚举值与出厂反射对不上）：\n"
            + str(enum_values.get("output", "")))
    # ⚑ 并入规范门禁（docs/union-conventions.md §四）：
    #   校验「来源出处 / 许可白名单 / 规范与地图存在 / 地图与来源同步 /
    #   能力验证等级合法」五条。**放在成员名之后、bundled 校验之前** ——
    #   bundled-skill 是已知的上游基线失败（本工作副本必然失败），
    #   放它前面才能保证这道门真的跑得到。
    union = _run_union_conventions_gate()
    if union.get("status") == "fail":
        raise AssertionError(
            "并入规范门禁未通过（见 docs/union-conventions.md）：\n"
            + str(union.get("output", "")))
    # ⚑ **参数绑定门禁**（硬门禁）：每个工具声明的参数名必须**有归属** ——
    #   要么在目标函数的形参表里，要么在 `param_alias` 里。
    #   触发它的是 **2026-10-01 两次真实事故**：W7 的 `magnitude_n` 与 段1.1 的 `study_name`
    #   都**漏写 `param_alias`** ⇒ 真机 `TypeError`（★ 两次都是"走工具真实路径"的证据脚本抓到的）。
    #   ★ **"记下来"不等于"下次不犯"** ⇒ 本门禁把那类变成**机器检查**（并用负例证明过它抓得住）。
    param_binding = _run_param_binding_gate()
    if param_binding.get("status") == "fail":
        raise AssertionError(
            "参数绑定门禁未通过（声明的参数既不在形参表、也不在 param_alias 里）：\n"
            + str(param_binding.get("output", "")))
    # ⚑ **环境坑门禁**（硬门禁）：查「subprocess 缺 encoding=」（事实 58）与
    #   「Path("<盘符>:") 当盘根」（事实 59）—— 两类都**已在真机上造成真实故障**。
    env_pitfalls = _run_env_pitfalls_gate()
    if env_pitfalls.get("status") == "fail":
        raise AssertionError(
            "环境坑门禁未通过（subprocess 编码 / Path 盘根）：\n"
            + str(env_pitfalls.get("output", "")))
    # ⚑ **验收命令可跑性门禁**（硬门禁）：`specs/**/*.md` 的 `→ 验收:` 行点到的脚本
    #   必须在**仓库里**（ROADMAP §〇 纪律三「验收必须是可跑的命令」）。
    #   触发它的是 2026-10-01 实测到的 **2 例仓库外验收脚本**。
    #   ⚠ **便携性**：specs 目录不在本机时它**自己 SKIP 并 exit 0** ⇒ 别的机器上不会无条件红。
    spec_paths = _run_spec_acceptance_paths_gate()
    if spec_paths.get("status") == "fail":
        raise AssertionError(
            "验收命令可跑性门禁未通过（→ 验收: 行点到了仓库外的脚本）：\n"
            + str(spec_paths.get("output", "")))
    # ⚑ **交付报告数字新鲜度门禁**（硬门禁）：`docs/harvest-report.md` 声称的
    #   「偏离上游：N 个文件 / +N 行 / -N 行 · N 个 commit」必须与 git 实际相符。
    #   触发它的是 2026-10-01（轮 54）实测的**8 倍/20 倍/10 倍**偏差 ——
    #   此前 `REQUIRED_ABILITY_FILES` **只查这两份报告存在，不查数字** ⇒ 报告可烂 50 轮而门禁全绿。
    #   ⚠ **便携性**：报告没有那行、或拿不到 `origin/main` ⇒ 它**自己 SKIP 并 exit 0**。
    report_fresh = _run_report_freshness_gate()
    if report_fresh.get("status") == "fail":
        raise AssertionError(
            "交付报告数字新鲜度门禁未通过（harvest-report 的偏离数字与 git 不符）：\n"
            + str(report_fresh.get("output", "")))
    # ⚑ **`.py` 语法门禁**（硬门禁）：`scripts/` `tools/` `tests/` `mcp-server/` `subskills/`
    #   下**每个** `.py` 必须能 `ast.parse`。★ 触发它的是**本会话同一处踩了五次**：
    #   新建文件时把**来源块写进了头部三引号里**（忘了闭合）⇒ Python 报的是
    #   `SyntaxError: invalid character '★'`（**错误信息指向星号、不是真因**），
    #   而 `ast.parse` 报的是真因的名字（`unterminated triple-quoted string literal`）。
    #   ⚠ **第五条正是在写这道门禁的脚本本身**上踩的。
    py_syntax = _run_python_syntax_gate()
    if py_syntax.get("status") == "fail":
        raise AssertionError(
            ".py 语法门禁未通过（有文件不能 ast.parse）：\n" + str(py_syntax.get("output", "")))
    # ⚑ **未定义名门禁**（硬门禁）：★ 与语法门禁**互补** —— 语法只判"能不能 parse"，
    #   本道判"读到的名字有没有被绑定过"。★ 触发它的是轮 403 真机抓到的
    #   `out_i4` 漏导入（★ 语法合法、19 道门禁全绿、而一调用就 NameError）。
    undef = _run_undefined_names_gate()
    if undef.get("status") == "fail":
        raise AssertionError(
            "未定义名门禁未通过（有名字读之前从未被绑定 ⇒ NameError 隐患）：\n"
            + str(undef.get("output", "")))
    # ⚑ **出厂类型库对照门禁**（硬门禁）：能力层里**手抄的成员表**
    #   必须与 `SolidWorks.Interop.cosworks.dll` 的元数据**逐条一致**。
    #   ★ 触发它的是轮 415：`_ERRORCODE_MEMBERS` 手抄 CHM 时漏了两个名字 ⇒
    #   两条好能力看起来调不通（`DISP_E_PARAMNOTOPTIONAL`）。
    # ⚑ **判据前置门禁**（硬门禁）：凡“用某个回读去判某条能力”的判据，
    #   必须先在**已知成功场景**上被验过（`docs/judge-registry.json` 登记）。
    #   ★ 触发它的是上一轮**五次**“能力好好的、而它看起来坏了”。
    #: ★ 2026-10-03（轮 450）：服务端侧工具名也要进门禁（事实 364）
    ss = _run_server_side_tools_gate()
    if ss.get("status") == "fail":
        raise AssertionError(
            "服务端侧工具名门禁未通过（两条声明路上有**重名**）：\n"
            + str(ss.get("output", "")))
    jp = _run_judge_preflight_gate()
    if jp.get("status") == "fail":
        raise AssertionError(
            "判据前置门禁未通过（有判据没登记清楚、或它的“已知成功”证据不成立）：\n"
            + str(jp.get("output", "")))
    #: ★ 注入绑定门禁（硬）：每条 ToolSpec 声明的 inject 必须覆盖包装的必需对象形参。
    #:   ⚠ 它**必须紧跟自己的 fail 检查** —— 元门禁 `check_gate_wiring.py` 判 hard/diagnostic
    #:   看的就是「该赋值节点的**下一个兄弟语句**是不是 fail 检查」。
    #:   ★ 我第一版把它插在 `jp` 与 `jp` 的检查**之间** ⇒ 两条一起被判成 diagnostic（实测）。
    ib = _run_inject_binding_gate()
    if ib.get("status") == "fail":
        raise AssertionError(
            "注入绑定门禁未通过（有 ToolSpec 漏声明 inject ⇒ 那条工具走 MCP 必炸）：\n"
            + str(ib.get("output", "")))
    tl_tables = _run_typelib_tables_gate()
    if tl_tables.get("status") == "fail":
        raise AssertionError(
            "出厂类型库对照门禁未通过（手抄的成员表与出厂类型库不一致）：\n"
            + str(tl_tables.get("output", "")))
    #: ★★ 2026-10-03（轮 515）**新增**：`in,out` 数组形参审计的**契约门禁** ——
    #:   ⚠ 为什么加：那份审计（`tools/audit_inout_array_params.py` ⇒
    #:   `output/inout-array-params.json`）是事实 128/129 的落地产物，
    #:   ★★ **而它自己没有被任何门禁引用**（只有 `audit_byref_args.py` 的**注释**提到它）
    #:   ⇒ ★ 它**"跑过一次"之后就再也不会被跑**、产物会**悄悄过期** ⚠
    #:   ★ 本道把它变成「**发布时必查**」：跑它那 5 条契约测试（纯静态 · ~0.1s）。
    inout = _run_inout_array_audit_gate()
    if inout.get("status") == "fail":
        raise AssertionError(
            "in,out 数组形参审计的契约未通过（产物缺失/过期，或审计的安全边界被删）：\n"
            + str(inout.get("output", "")))
    # ⚑ **签名审计表新鲜度门禁**（硬门禁）：`docs/signature-audit.md` 的**逐模块调用点数**
    #   必须与实跑 `scripts/audit_call_arity.py` 的结果相符（A5 的制品）。
    #   触发它的是 2026-10-01（轮 55）实测的 **3/6 模块失真** ——
    #   与 `harvest-report` **完全同型**的缺口（只查存在、不查数字），只是这份还能**实跑复核**。
    #   ⚠ **便携性**：拿不到 `D:\AI\SW\_raw` 或模块文件 ⇒ 它**自己 SKIP 并 exit 0**。
    sig_fresh = _run_signature_audit_freshness_gate()
    if sig_fresh.get("status") == "fail":
        raise AssertionError(
            "签名审计表新鲜度门禁未通过（signature-audit 的逐模块数字与实跑不符）：\n"
            + str(sig_fresh.get("output", "")))
    # ⚑ **A6 许可红线门禁**（硬门禁）：来源块声明的来源与许可必须在**白名单**内 ——
    #   把 `AGENTS.md §一 A6`「逐文件对照许可判定表」做成**可跑的那一半**。
    #   ⚠ 它判**声明是否自洽/越界**，**不判声明是否属实**（后者是语义判断，靠人核）。
    license_rl = _run_license_redlines_gate()
    if license_rl.get("status") == "fail":
        raise AssertionError(
            "A6 许可红线门禁未通过（来源声明 vs 许可白名单）：\n"
            + str(license_rl.get("output", "")))
    # ⚑ **A8 交付状态摘要门禁**（硬门禁）：`docs/harvest-digest.md` 必须与生成器输出一致 ——
    #   把 `AGENTS.md §一 A8`「报告写明并入了什么 / 仍空缺什么 / 为什么」做成**可跑的那一半**。
    #   ⚠ 它是**生成物**：与真源分叉时报告就在**说假话**，而这类分叉**不会自己暴露**。
    digest_fresh = _run_digest_freshness_gate()
    if digest_fresh.get("status") == "fail":
        raise AssertionError(
            "A8 交付状态摘要新鲜度门禁未通过（digest 与真源分叉）：\n"
            + str(digest_fresh.get("output", "")))
    # ⚑ 接口归属**诊断**（**不是门禁**，不拦发布）—— 放在所有硬门禁**之后**：
    #   诊断慢、且映射表有洞，放前面没意义。**假绿（检查量为 0）会在返回体里标出来。**
    ownership = _run_interface_ownership_probe()
    expected_runtime_files = collect_runtime_files(ROOT)
    bundled_drift = find_bundled_skill_drift(ROOT, BUNDLED_SKILL, expected_runtime_files)
    if bundled_drift:
        preview = ", ".join(bundled_drift[:10])
        suffix = " ..." if len(bundled_drift) > 10 else ""
        # ⚠ **把「该怎么办」写进报错里**（2026-10-01）：原来只报
        #   `桌面内嵌 Skill 与根 Skill 不一致: <bundled-skill-missing>`，
        #   **看不出来那是一步**没跑的构建**（该目录在 `.gitignore` 里，是 `sync_bundled_skill.py`
        #   生成的产物）⇒ 新人会以为是代码 bug。
        #   ⇒ 本分支现在**分开报两种情况**，并给出**可直接执行的修复命令**。
        if bundled_drift == ["<bundled-skill-missing>"]:
            raise AssertionError(
                "桌面内嵌 Skill 快照**尚未生成**：%s 不存在。\n"
                "  该目录在 .gitignore 里，是**构建产物**（不是源码）⇒ 跑一次：\n"
                "      python scripts/sync_bundled_skill.py\n"
                "  ⚠ 全新 clone 后必须先跑这一步，`release_check` 才可能通过。"
                % BUNDLED_SKILL
            )
        raise AssertionError(
            f"桌面内嵌 Skill 与根 Skill 不一致: {preview}{suffix}\n"
            "  ⇒ 源码改了但快照没重生成 ⇒ 重跑：python scripts/sync_bundled_skill.py"
        )
    bundled_file_count = sum(1 for path in BUNDLED_SKILL.rglob("*") if path.is_file())
    # ⚑ **汇总所有门禁的状态**（2026-10-01 轮 74 加）—— **同一问题的第五层**。
    #   轮 71–73 依次解决了：接线了没 · 接线方式对不对 · 跳过时算不算数。
    #   本轮问第四问：**「跳过了」在结果里看得见吗？**
    #   ⚠ 实测：返回体只列了 **4 个**门禁（`provenance` / `diff_markers` /
    #     `member_names` / `interface_ownership`），其余 **9 个的状态根本没被汇总** ——
    #     更关键的是 **没有任何地方统计 `skipped`** ⇒ **「跳过了」是隐形的**。
    #   ★ 一个**静默跳过**的门禁与**没跑**等价（本项目已记录的第三种面孔）。
    #   ⇒ 把 13 个状态一次全列出来，并**单独列出被跳过的**（**显式**，不靠人去翻各段）。
    _gate_results = {
        "provenance": provenance,
        "diff_markers": markers,
        "member_names": member_names,
        #: ★ 2026-10-03（轮 579）★ **元门禁当场抓到我没加这一行** ——
        #:   `check_gate_wiring.py` 报「`unreachable` **没进返回体** ⇒ 静默跳过与没跑等价」⚠
        "unreachable": unreachable,
        #: ★ 2026-10-03（轮 594）★ 同一道元门禁，★ **第二次**教了同一课
        "verified_evidence": verified_ev,
        "backend_limited": backend_lim,
        "backend_limited_complete": backend_full,
        "workspace_shadowing": shadowing,
        "gate_wiring": wiring,
        "param_binding": param_binding,
        "union_conventions": union,
        "env_pitfalls": env_pitfalls,
        "spec_acceptance_paths": spec_paths,
        "report_freshness": report_fresh,
        "signature_audit_freshness": sig_fresh,
        "license_redlines": license_rl,
        "digest_freshness": digest_fresh,
        "report_criteria_alignment": crit_align,
        "negative_input_selfproof": selfproof,
        "enum_values": enum_values,
        "interface_ownership": ownership,
        #: ★ 2026-10-01（轮 356）：**`.py` 语法门禁**必须汇总进返回体 ——
        #:   元门禁当场报了「`py_syntax` 的结果**没有进返回体** ⇒ 『它跳过了/它没跑』在外面**看不见**
        #:   （★ 静默跳过与没跑等价）」。★ **这条正是元门禁存在的意义**（轮 191 的定则）。
        "py_syntax": py_syntax,
        #: ★ 2026-10-03（轮 404）：**未定义名门禁**同样必须进返回体 ——
        #:   ⚠ 而这一条**正是元门禁当场抓到的**：我先前只加了门禁与它的 fail 判据，
        #:   却没把它汇总进 `_gate_results` ⇒ 元门禁报「`undef` 的结果**没有进返回体**
        #:   ⇒ 『它跳过了/它没跑』在外面**看不见**（静默跳过与没跑等价）」。
        #:   ★★ 那是元门禁**第二次**抓到同一类疏漏（第一次是轮 356 的 `py_syntax`）。
        "undefined_names": undef,
        #: ★ 2026-10-03（轮 416）：出厂类型库对照也必须进返回体
        #:   —— ★元门禁已两次抓到同一类疏漏（「跳过与没跑等价」）。
        "typelib_tables": tl_tables,
        #: ★★ 2026-10-03（轮 515）：**`in,out` 数组审计契约**也必须进返回体 ——
        #:   ⚠ 而这一条**又是元门禁当场抓到的**（第三次同一类）：
        #:   我只加了 gate 与 fail 判据，却没汇总进 `_gate_results`
        #:   ⇒ 元门禁报「`inout` 的结果没有进返回体 ⇒ 『它跳过了/它没跑』在外面看不见」。
        #:   ★★ 那已是元门禁**第三次**抓到它（轮 356 `py_syntax` · 轮 404 `undef` · 本轮 `inout`）。
        "inout_array_audit": inout,
        #: ★ 2026-10-03（轮 420）：判据前置也必须进返回体（元门禁的第三条）
        "judge_preflight": jp,
        "inject_binding": ib,
        #: ★ 2026-10-03（轮 450）：服务端侧工具名也进返回体（元门禁的第三条）
        "server_side_tools": ss,
    }
    # ⚠ 容错：不是每个 `_run_*` 都保证返回 dict ⇒ 取不到就标 `unknown`（**不谎报 `pass`**）。
    gates: dict = {}
    #: ⚑⚑ **2026-10-01（轮 191）：`gates` 与 `gate_details` 在**同一个循环**里一起建** ——
    #:   这样两者**不可能分叉**（一个门禁要么两处都有，要么两处都没有）。
    #: ★ 为什么加 `gate_details`：轮 74 已经把「**13 个门禁的 `status`**」和 `skipped` 都暴露了，
    #:   但**每道门禁的 `output`（「扫了多少 / 跳过了什么 / 覆盖面在哪」）仍只有 4 道有**
    #:   ⇒ ★★ 于是「**status 隐形**」修好了，「**覆盖面隐形**」没修 ——
    #:   而**「判据没覆盖」与「没有问题」在输出上长得一模一样**（轮 190 的定则）。
    #: ⇒ 现在每道门禁都带一条**明细**（优先 `output`，其次 `reason`，最后退回 `status`），
    #:   于是「它到底扫了什么」**永远可见**，不必去翻各门禁自己的源码。
    gate_details: dict = {}
    for _name, _res in _gate_results.items():
        if isinstance(_res, dict):
            gates[_name] = _res.get("status", "unknown")
            gate_details[_name] = _gate_detail(_res)
        else:
            gates[_name] = "unknown"
            gate_details[_name] = "unknown（非 dict 结果 ⇒ 无明细）"
    skipped = sorted(n for n, s in gates.items() if s == "skipped")
    return {
        "status": "pass",
        "version": ui_version,
        "capabilities": len(capabilities),
        "bundled_skill_files": bundled_file_count,
        # ⚑ **13 个门禁的状态一次全列**（此前只列 4 个 ⇒ 其余是隐形的）
        "gates": gates,
        # ⚑ **每道门禁的明细**（轮 191 加）：优先 `output`（它说的是**扫了多少 / 跳过了什么**），
        #   其次 `reason`，最后退回 `status` ⇒ ★ **保证每道都非空**（与 `gates` 同键）。
        #   ⚠ 截断到 700 字符：完整的 output 由各门禁自己的 stdout 提供，这里只要**够读**。
        "gate_details": gate_details,
        # ⚑ **被跳过的单独列出**：跳过的门禁**没有在检查** ⇒ 必须一眼可见
        "skipped": skipped,
        "skipped_count": len(skipped),
        "gates_passed": sorted(n for n, s in gates.items() if s == "pass"),
        "gates_diagnostic": sorted(n for n, s in gates.items()
                                   if s in ("clean", "hits", "checked_nothing")),
        "provenance": provenance,
        "diff_markers": markers,
        "member_names": member_names,
        #: ★ 2026-10-03（轮 579）★ 元门禁要的**第二处**：★ 登记表**必须覆盖每一个调用点** ⚠
        "unreachable": unreachable,
        "verified_evidence": verified_ev,
        "interface_ownership": ownership,
        "missing": [],
    }


if __name__ == "__main__":
    print(json.dumps(run_release_check(), ensure_ascii=False, indent=2))
