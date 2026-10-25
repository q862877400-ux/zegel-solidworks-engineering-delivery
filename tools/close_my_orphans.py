"""清掉我这两轮 E4 探针留下的 3 个孤儿文档（**先逐条核归属，再关**）。

## 为什么是我留下的

```
title=板1_rev-1.SLDPRT  type=1 dirty=False path=...\\output\\stage2\\板1_rev-1.SLDPRT
title=装配体2            type=2 dirty=True  path=''
title=装配体3            type=2 dirty=True  path=''
```

- `板1_rev-1.SLDPRT`：E4 探针**直跑**（不经沙箱）时打开的那份交付件 —— 路径在 `output/` 下
- `装配体2/3`：两个探针 `new_document("assembly")` 建的空装配，**从没保存** ⇒ `dirty=True`

## 为什么脏文档比干净文档难关

`ISldWorks.CloseDoc` 对 `dirty` 文档会因「是否保存」而**关不掉**；
而 `ISldWorks.SetSaveFlag()` 按官方定义是「**把文档标脏**」，不能用来清脏
（事实族 561）。唯一可行的路是 `CloseAllDocuments(IncludeUnsaved=True)` —— 但它
**会连非我方文档一起关**，所以必须先逐条核归属。

## 与 `tools/discard_orphan_via_closeall.py` 的关系

那个工具的前置是「**恰好 1 个**文档」，本机是 3 个 ⇒ 它拒绝执行（那是它的保守判据）。
本脚本的判据放宽到「**任意个，但每一个都必须是我方产物**」：

| 归属判据 | 说明 |
|---|---|
| 路径在 `<仓库根>/output/` 下 | 我方产物目录（`output/` 已 gitignore） |
| 或者**无路径且是装配体** | 我方探针 `new_document` 建的空装配 |

★ 任一条不满足 ⇒ **立刻停手**，不调 `CloseAllDocuments`。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as c_  # noqa: E402
from scripts.sw_connect import get_com_member  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 孤儿文档清理）
# 文件:   tools/close_my_orphans.py
# 定位:   E4 探针直跑（不经沙箱）留下 1 个交付件副本 + 2 个未保存装配；
#          脏文档 `CloseDoc` 关不掉、`SetSaveFlag` 是"标脏"不能清脏
#          ⇒ 只能用 `CloseAllDocuments(IncludeUnsaved=True)`，但必须先逐条核归属。
# 官方依据: ISldWorks::CloseAllDocuments · ISldWorks::CloseDoc · ISldWorks::GetDocuments
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

OUTPUT_ROOT = str(R / "output")


def _docs(sw) -> list:
    return list(get_com_member(sw, "GetDocuments") or ())


def _info(d) -> dict:
    return {
        "title": str(get_com_member(d, "GetTitle") or ""),
        "type": int(get_com_member(d, "GetType") or 0),
        "dirty": bool(get_com_member(d, "GetSaveFlag")),
        "path": str(get_com_member(d, "GetPathName") or ""),
    }


def _mine(i: dict) -> tuple[bool, str]:
    """★ 归属判据：`output/` 下，或无路径的装配体（我方 `new_document` 建的）。"""
    p = i["path"]
    if p:
        if p.lower().startswith(OUTPUT_ROOT.lower()):
            return True, "路径在 output/ 下"
        return False, "路径不在 output/ 下：%s" % p
    if i["type"] == 2:
        return True, "无路径且是装配体（我方 new_document 建的）"
    return False, "无路径且不是装配体（可能是我方新建零件，但无一例外须人工确认）"


def main() -> int:
    ev: dict = {"probe": "close-my-orphans"}
    conn = c_.connect_solidworks(wait_seconds=20)
    sw = conn[0] if isinstance(conn, tuple) else conn
    try:
        sw.CommandInProgress = True
    except Exception:  # noqa: BLE001
        pass

    docs = _docs(sw)
    infos = [_info(d) for d in docs]
    ev["before"] = infos
    print("清理前文档数：%d" % len(infos))
    for i in infos:
        ok, why = _mine(i)
        print("  %s %-24s type=%s dirty=%s ⇒ %s" % (
            "✓我方" if ok else "✗非我方", i["title"][:24], i["type"], i["dirty"], why
        ))

    bad = [(i, _mine(i)[1]) for i in infos if not _mine(i)[0]]
    if bad:
        ev["abort"] = "有 %d 个不是我方的文档 ⇒ 不调 CloseAllDocuments" % len(bad)
        print("★ " + ev["abort"])
        for i, why in bad:
            print("   %s：%s" % (i["title"], why))
        (R / "output" / "close-my-orphans.json").write_text(
            json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return 1

    if not infos:
        print("★ 没有文档，不需要清理")
        ev["after"] = []
        (R / "output" / "close-my-orphans.json").write_text(
            json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return 0

    get_com_member(sw, "CloseAllDocuments", True)
    left = _docs(sw)
    ev["after"] = [_info(d) for d in left]
    ev["ok"] = len(left) == 0
    print("清理后文档数：%d" % len(left))
    for i in ev["after"]:
        print("  仍在：%s" % i["title"])

    try:
        sw.CommandInProgress = False
    except Exception:  # noqa: BLE001
        pass
    (R / "output" / "close-my-orphans.json").write_text(
        json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("★ 结论：%s" % ("已清空" if ev["ok"] else "仍有残留"))
    return 0 if ev["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
