"""★ 收集 Bunny 扇出的**产物文件**，合成一份再过门禁（★ 扇出改成"写文件"后的配套）。

★ 为什么要有它（★ 2026-10-04 的实测教训）：
```
★ 第一坡 62 路把结果**回在返回值里** ⇒ harness 的返回值**被截断**
  （`… [truncated: 155732 more characters]`）⇒ ★★ **155 KB 的产出只剩 21 行可用** ✓
★ 而子代理的会话投影缓存里**只存上下文、不存结构化输出**（最终 assistant 消息长度为 0）
  ⇒ ★ **事后也捞不回来** ✓
⇒ ★★ 所以扇出一律改成：★ **每路把结果写成 `output/bunny-rows/chunk-<start>.json`**，
  返回值只留一行摘要 ⇒ ★ 永不截断，且**天然可重跑/可续跑**（已完成的那坡不必重做）✓
```
"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（扇出配套工具，非移植）
# 文件:   `output/bunny-rows/chunk-*.json`（各路子代理写的产物）·
#         `output/bunny-rows-salvaged.json`（第一坡从截断值里救回的那 21 行）
# 定位:   把多路产物合成一份，交给 `tools/check_bunny_toolspec_rows.py` 过门禁 ✓
# 官方依据: 无（本仓自建工具）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--dir", default=Path(__file__).resolve().parents[1] / "output" / "bunny-rows"
    )
    ap.add_argument(
        "--extra",
        action="append",
        default=[],
        help="额外的行文件（如第一坡救回的那份），可多次给",
    )
    ap.add_argument(
        "--out",
        default=Path(__file__).resolve().parents[1] / "output" / "bunny-rows-all.json",
    )
    a = ap.parse_args()

    rows, files = [], []
    d = Path(a.dir)
    if d.is_dir():
        for p in sorted(d.glob("chunk-*.json")):
            try:
                obj = json.loads(p.read_text(encoding="utf-8", errors="replace"))
            except Exception as exc:  # noqa: BLE001
                print("⚠ 解析失败（跳过）: %s ⇒ %s" % (p.name, type(exc).__name__))
                continue
            got = [
                r
                for r in (obj.get("rows") or [])
                if isinstance(r, dict) and r.get("function")
            ]
            rows += got
            files.append((p.name, len(got)))
    for extra in a.extra:
        p = Path(extra)
        if not p.is_file():
            print("⚠ extra 不存在:", extra)
            continue
        obj = json.loads(p.read_text(encoding="utf-8", errors="replace"))
        got = [
            r
            for r in (obj.get("rows") or [])
            if isinstance(r, dict) and r.get("function")
        ]
        rows += got
        files.append((p.name, len(got)))

    #: ★ 去重：同 (module, function) 留**字段更全**的那条
    best: dict = {}
    for r in rows:
        k = (r.get("module"), r.get("function"))
        if k not in best or len(json.dumps(r, ensure_ascii=False)) > len(
            json.dumps(best[k], ensure_ascii=False)
        ):
            best[k] = r
    uniq = list(best.values())

    print(
        "★ 读了 %d 份产物文件 · 原始 %d 行 ⇒ 去重后 **%d 行**"
        % (len(files), len(rows), len(uniq))
    )
    print("★ 按模块:", dict(Counter(r.get("module") for r in uniq).most_common(16)))
    print(
        "★ exposable=True: %d · False: %d"
        % (
            sum(1 for r in uniq if r.get("exposable") is True),
            sum(1 for r in uniq if r.get("exposable") is False),
        )
    )
    Path(a.out).write_text(
        json.dumps({"rows": uniq}, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print("★ 落盘:", a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
