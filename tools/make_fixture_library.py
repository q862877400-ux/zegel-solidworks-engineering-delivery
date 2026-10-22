"""★ 建/校验夹具库：真实件一次性复制进来、冻结哈希清单。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（生成器）
# 文件:   tools/make_fixture_library.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B5-5**。★ 评审**收回**了「给原目
#           录设 ACL」那条
#   （SolidWorks 单进程 ⇒ 拒写会连用户自己的保存一起堵住）⇒ ★ 改成：
#   ★★ **夹具只快照一次**（真实件一次性复制到测试专用夹具库 + 冻结哈希），
#     ★ 此后测试**永远不再引用原目录** ⇒ ★ **原件不需要任何 ACL，因为没人再碰它** ✓
# 判据:   ★ `--verify` 逐个重算哈希 ⇒ 不符就报出（★ 用来发现夹具被污染过）✓
#   ★ **纯加法**：★ 不删、不覆盖；★ 同名同哈希跳过，★ 同名不同哈希换名 ✓
# ⚠ 限度: ★ 本工具**只复制**（`shutil.copy2`）—— ★ 对源件只读，
#   ★ 所以「不删用户数据」这条红线在它身上**结构上**成立 ✓
# 官方依据: 无 —— ★ 我方策略，如实标注 ✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import fixtures as FX                                                  # noqa: E402

#: ★ 默认的**素材来源**：★ 用户工作区里的模型目录（★ 只**读**它们，然后复制）✓
DEFAULT_SOURCES = (
    REPO_ROOT / "AI Solidworks" / "模型",
)


def main() -> int:
    ap = argparse.ArgumentParser(description="★ 建/校验夹具库（规格 210 · B5-5）")
    ap.add_argument("--source", action="append", default=[],
                    help="★ 素材目录（可重复；默认模型目录）")
    ap.add_argument("--recursive", action="store_true", help="★ 递归收集")
    ap.add_argument("--verify", action="store_true", help="★ 只校验哈希，不复制")
    ap.add_argument("--dry-run", action="store_true", help="★ 只说会复制什么，不动盘")
    ap.add_argument("--note", default="", help="★ 写进清单的备注")
    args = ap.parse_args()

    root = FX.library_root()
    print("★ 夹具库：%s" % root)

    if args.verify:
        v = FX.verify()
        print("★ 校验 %d 个 · 缺失 %d · 哈希不符 %d · 清单外多余 %d"
              % (v["checked"], len(v["missing"]), len(v["changed"]), len(v["extra"])))
        for name in v["changed"][:8]:
            print("   ★ 哈希不符：%s" % name)
        for name in v["missing"][:8]:
            print("   ★ 缺失：%s" % name)
        if v["extra"]:
            print("   （清单外的文件 %d 个 —— ★ 不删，只报）" % len(v["extra"]))
        print("★ 结论：%s" % ("一致 ✓" if v["ok"] else "★★ 已被污染 ⇒ 这些件不再算留出集"))
        return 0 if v["ok"] else 3

    folders = [Path(s) for s in args.source] or list(DEFAULT_SOURCES)
    sources = FX.collect_sources(folders, recursive=args.recursive)
    print("★ 素材目录：%s" % "、".join(str(f) for f in folders))
    print("★ 收集到 CAD 件 %d 个（★ 只按扩展名；★ 别的文件一律不碰）" % len(sources))
    r = FX.build(sources, note=args.note, dry_run=args.dry_run)
    print("★ 复制 %d 个 · 跳过 %d 个%s"
          % (len(r["copied"]), len(r["skipped"]), "（★ dry-run，未动盘）" if args.dry_run else ""))
    for c in r["copied"][:10]:
        print("   + %s  ⤺ %s" % (c["name"], Path(c["from"]).name))
    print("★ 清单：%s（★ 共 %d 条）" % (root / FX.MANIFEST_NAME, len(r["manifest"]["files"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
