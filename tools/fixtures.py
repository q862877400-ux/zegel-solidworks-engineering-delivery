"""★ 夹具库：真实件**一次性**复制进来、**冻结哈希清单**，此后测试只认它、不再碰原目录。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试基础设施）
# 文件:   tools/fixtures.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B5-5**。★ 外部评审的判决（**它收回过一次建议**）：
#   ★★ 它原先主张「给原目录设 ACL 拒写」⇒ **自己收回了**：SolidWorks 是**单进程**，
#     ★ 给那个账户拒写会**连用户自己的保存一起堵住** ✗
#   ⇒ ★ 改成两层：★ **① 夹具只快照一次**（真实件一次性复制到测试专用夹具库、冻结哈希；
#     ★ 此后测试**永远不再引用原目录** —— ★ 于是**原件不需要任何 ACL**，因为**没人再碰它**）·
#     ★ ② ACL 只留给夹具库（★ 本文件不设 ACL，只把「只读」做成**约定 + 校验**）✓
# 判据:   ★ `verify()` 逐个重算哈希 ⇒ 与清单不符就报出（★ 用来发现「夹具被污染过」）✓
#   ★ `fixture_path(name)` **只在夹具库内解析** —— ★ **绝不去原目录取** ✓
#   ★★ 构建是**纯加法**：★ 不删、不覆盖已有夹具；★ 同名不同内容 ⇒ **换名并报出** ✓
# 官方依据: 无 —— ★ 这是**我方策略**，如实标注，不假托官方 ✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

#: ★★ 夹具库的落点：★ `output/` 是**不入库**的产物目录 ⇒ 用户的设计件不会被提交进仓库 ✓
DEFAULT_LIBRARY = REPO_ROOT / "output" / "fixtures"

MANIFEST_NAME = "MANIFEST.json"

#: ★ 认得作夹具的 CAD 扩展名（★ 只收这些；★ 别的文件**不碰**）✓
CAD_SUFFIXES = (".sldprt", ".sldasm", ".slddrw")


def library_root() -> Path:
    """★ 夹具库根 —— ★ 可用 `SW_FIXTURE_LIBRARY` 覆盖（测试就是这么隔离的）✓"""
    given = str(os.environ.get("SW_FIXTURE_LIBRARY", "")).strip()
    return Path(given) if given else DEFAULT_LIBRARY


def sha256_of(path, *, chunk: int = 1 << 20) -> str:
    """★ 流式算 SHA-256（★ 大件也不吃内存）✓"""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def load_manifest(root=None) -> dict:
    """★ 读清单；★ 没有就回空壳（★ **不假装有**）✓"""
    path = (Path(root) if root else library_root()) / MANIFEST_NAME
    if not path.is_file():
        return {"_": "★ 还没建夹具库", "created": "", "sources": [], "files": {}}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:                                                   # noqa: BLE001
        return {"_": "★ 清单读取失败", "created": "", "sources": [], "files": {}}


def fixture_path(name, *, must_exist: bool = True):
    """★★ **只在夹具库内**解析夹具名 —— ★ **绝不去原目录取**（这是 B5-5 的全部要点）✓

    :returns: `Path` 或 `None`（`must_exist=False` 时允许不存在）
    ★★ 为什么这点最要紧：★ 若测试还会「顺手」从用户目录取件，★ 那么**原目录就仍然会被打开**
      ⇒ ★ 评审收回 ACL 方案的前提（「没人再碰它」）就**不成立**了 ✗
    """
    p = library_root() / str(name)
    if not p.is_file():
        return None if not must_exist else None
    return p


def verify(root=None) -> dict:
    """★ 逐个重算哈希与清单比对 ⇒ **发现夹具被污染**就报出来 ✓

    :returns: `{"ok", "checked", "missing": [...], "changed": [...], "extra": [...]}`
    ★★ 为什么必须能查这个：★ 评审的判据是「**哈希一变，这些件就不再算留出集**」 ✓
    """
    base = Path(root) if root else library_root()
    man = load_manifest(base)
    files = man.get("files") or {}
    missing, changed = [], []
    present = set()
    for name, rec in files.items():
        p = base / name
        if not p.is_file():
            missing.append(name)
            continue
        present.add(name)
        if sha256_of(p) != rec.get("sha256"):
            changed.append(name)
    on_disk = {str(p.relative_to(base)).replace("\\", "/")
               for p in base.rglob("*")
               if p.is_file() and p.name != MANIFEST_NAME}
    return {"ok": not missing and not changed, "checked": len(present),
            "missing": sorted(missing), "changed": sorted(changed),
            "extra": sorted(on_disk - set(files))}


def collect_sources(folders, *, recursive: bool = False):
    """★ 从给定目录收集**可能是夹具**的 CAD 件（★ 只按扩展名，★ 其它文件一律不碰）✓"""
    found = []
    for folder in (folders or ()):
        base = Path(str(folder))
        if not base.is_dir():
            continue
        walker = base.rglob("*") if recursive else base.glob("*")
        for p in sorted(walker):
            if p.is_file() and p.suffix.lower() in CAD_SUFFIXES:
                found.append(p)
    return found


def build(sources, root=None, *, note: str = "", dry_run: bool = False) -> dict:
    """★★ **一次性快照**：把源件复制进夹具库并**冻结哈希清单** —— ★ 纯加法，绝不删、绝不覆盖 ✓

    :returns: `{"library", "copied": [...], "skipped": [...], "manifest", "dry_run"}`
    ★★ 三条安全判据：
      ① ★ **不删任何东西**（连夹具库里已有的多余文件也不删）✓
      ② ★ **同名且哈希相同 ⇒ 跳过**（★ 不浪费时间，也不动它）✓
      ③ ★ **同名但哈希不同 ⇒ 换名复制**（★ 覆盖会毁掉上一次那份夹具）✓
    """
    base = Path(root) if root else library_root()
    man = load_manifest(base)
    files = dict(man.get("files") or {})
    copied, skipped = [], []
    for src in (sources or ()):
        src = Path(str(src))
        if not src.is_file():
            skipped.append({"source": str(src), "why": "★ 不是文件"})
            continue
        digest = sha256_of(src)
        name = src.name
        existing = files.get(name)
        if existing and existing.get("sha256") == digest:
            skipped.append({"source": str(src), "why": "★ 同名同哈希 ⇒ 已有，跳过"})
            continue
        if name in files:
            n = 1
            while ("%s__%d%s" % (src.stem, n, src.suffix)) in files:
                n += 1
            name = "%s__%d%s" % (src.stem, n, src.suffix)
        if not dry_run:
            base.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src), str(base / name))
        files[name] = {"sha256": digest, "size": src.stat().st_size,
                       "source": str(src),
                       "copied": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        copied.append({"name": name, "from": str(src), "sha256": digest[:16]})
    new_man = {
        "_": "★ 夹具库清单（规格 210 · B5-5）：★ 冻结哈希 —— ★ 哈希一变就不再算留出集。★ 不要手改。",
        "_regenerate": "python tools/make_fixture_library.py",
        "_why": "★ 评审收回 ACL 方案后的替代：★ 夹具只快照一次，此后**没人再碰原目录** ✓",
        "created": man.get("created") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "note": note,
        "sources": sorted({str(Path(c["from"]).parent) for c in copied}
                          | set(man.get("sources") or [])),
        "files": files,
    }
    if not dry_run:
        base.mkdir(parents=True, exist_ok=True)
        (base / MANIFEST_NAME).write_text(
            json.dumps(new_man, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
            encoding="utf-8")
    return {"library": str(base), "copied": copied, "skipped": skipped,
            "manifest": new_man, "dry_run": dry_run}
