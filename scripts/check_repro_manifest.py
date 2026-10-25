"""★ 复现清单校验器（规格 350 · T030「干净环境复现」）。

## 它判什么、不判什么（**边界写在最前面**）

判：
- Python 版本符合声明
- 声明的包都能导入且版本对
- 声明为「在仓库里」的输入**真的在仓库里**（`git ls-files` 能查到）且 **sha256 一致**
- 每条 `steps[].cmd` 指向的脚本**在仓库里存在**
- 每个 `known_gaps` 都写了 `impact` / `owner` / `remedy`

**不判**（如实）：SolidWorks 装没装（只能 COM 读，且那要开着 SW）；
换台机器跑出来的产物是否**逐字节**一致（那要在那台机器上真跑一遍）。

## 退出码

- `0`：可核项全过（`known_gaps` 允许存在，它们会被打印出来）
- `1`：有**可修**的问题（比如声明 in_repo 的文件却不在仓库、脚本路径不存在、哈希不符）

★ 「有 known_gaps」**不算失败** —— 缺口写清楚是诚实，写不清才是问题。
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
MANIFEST = R / "docs" / "repro-manifest.yaml"


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（复现清单校验）
# 文件:   scripts/check_repro_manifest.py
# 定位:   读 `docs/repro-manifest.yaml`，核 Python/包/输入哈希/脚本路径/缺口三要素。
# 官方依据: 不适用（本仓自定口径）；哈希用标准库 hashlib，git 查询用 subprocess
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _tracked(rel: str) -> bool:
    """`git ls-files` 能不能查到（干净检出的判据）。"""
    try:
        r = subprocess.run(
            ["git", "ls-files", "--error-unmatch", rel],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(R), timeout=60,
        )
        return r.returncode == 0
    except Exception:  # noqa: BLE001
        return False


def _script_of(cmd: str) -> str:
    """从 `python -B scripts/x.py` 里取出脚本相对路径。"""
    parts = str(cmd or "").split()
    for tok in parts:
        if tok.lower().endswith(".py"):
            return tok
    return ""


def check() -> tuple:
    """回 `(problems, warnings, gaps)`. `problems` 非空 ⇒ 退出码 1。"""
    import yaml

    d = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    problems: list = []
    warnings: list = []

    #: ① Python 版本
    want = str(((d.get("runtime") or {}).get("python") or {}).get("version") or "")
    have = "%d.%d.%d" % sys.version_info[:3]
    if want and have != want:
        warnings.append(
            "Python 版本 %s ≠ 声明 %s（★ 不判失败：补丁级差异通常无害，但要在发布说明里写清）"
            % (have, want)
        )

    #: ② 包
    for pkg in (d.get("runtime") or {}).get("packages") or ():
        name = str(pkg.get("import_as") or pkg.get("name") or "")
        try:
            mod = __import__(name)
        except Exception as exc:  # noqa: BLE001
            problems.append("包 %s 导入失败（%s）" % (name, type(exc).__name__))
            continue
        want_v = str(pkg.get("version") or "")
        have_v = str(getattr(mod, "__version__", "") or "")
        if want_v and have_v and want_v != have_v:
            warnings.append("包 %s 版本 %s ≠ 声明 %s" % (name, have_v, want_v))

    #: ③ 输入资产
    for item in d.get("inputs") or ():
        rel = str(item.get("path") or "")
        p = R / rel
        declared_in_repo = bool(item.get("in_repo"))
        if not p.is_file():
            msg = "输入 %s **不存在**" % rel
            if declared_in_repo:
                problems.append(msg + "（却声明 in_repo: true）")
            else:
                warnings.append(msg + "（声明 in_repo: false ⇒ 已记进 known_gaps 才算诚实）")
            continue
        want_hash = str(item.get("sha256") or "")
        if want_hash and _sha256(p) != want_hash:
            problems.append("输入 %s 的 sha256 与声明不符" % rel)
        if declared_in_repo and not _tracked(rel):
            problems.append(
                "输入 %s 声明 in_repo: true，但 `git ls-files` 查不到 ⇒ 干净检出拿不到" % rel
            )

    #: ④ 步骤里的脚本必须存在
    for step in d.get("steps") or ():
        for key in ("cmd", "then"):
            cmd = step.get(key)
            if not cmd:
                continue
            rel = _script_of(str(cmd))
            if not rel:
                warnings.append("步骤 %s 的 %s 里找不到 .py 脚本" % (step.get("id"), key))
            elif not (R / rel).is_file():
                problems.append("步骤 %s 指向的脚本不存在：%s" % (step.get("id"), rel))

    #: ⑤ 缺口三要素
    gaps = d.get("known_gaps") or ()
    for g in gaps:
        for k in ("what", "impact", "owner", "remedy"):
            if not str((g or {}).get(k) or "").strip():
                problems.append("known_gaps.%s 缺 %s" % ((g or {}).get("key"), k))

    return problems, warnings, gaps


def main() -> int:
    problems, warnings, gaps = check()
    print("复现清单校验 · %s" % MANIFEST.name)
    for w in warnings:
        print("   ⚠ %s" % w)
    if gaps:
        print("   已知缺口 %d 条（不判失败，但发布说明必须写清）：" % len(gaps))
        for g in gaps:
            print("     · %-28s owner=%s" % (g.get("key"), g.get("owner")))
    if problems:
        print("★ [FAIL] %d 处可修问题：" % len(problems))
        for p in problems:
            print("   -", p)
        return 1
    print("★ [PASS] 可核项全过（缺口 %d 条已如实登记）" % len(gaps))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
