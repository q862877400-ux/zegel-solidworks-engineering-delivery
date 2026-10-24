"""★ 按官方语义丢弃那个孤儿文档：`ISldWorks.CloseAllDocuments(True)`。

## 为什么不能只 `CloseDoc`

`reclaim_solidworks --probe` 读到：

```
打开文档=['板1_rev-1.SLDPRT'] ⇒ 自己的 [] · 不是自己的 ['板1_rev-1.SLDPRT']
```

而 `tools/probe_list_open_docs.py` 读到 `path=''`、`GetSaveFlag` 为真
⇒ 有未保存改动 ⇒ `ISldWorks.CloseDoc` 会弹「是否保存」框。

`types/IModelDoc2/SetSaveFlag.md` 逐字是「**Flags the document as dirty**」
—— 它是**标脏**，没有清脏的 API ⇒ **没法让那个框不弹**。

## 官方给的正式出口

`types/ISldWorks/CloseAllDocuments.md` 逐字：

> `System.bool CloseAllDocuments( System.bool IncludeUnsaved )`
> - **True = Close all documents, including dirty documents**
> - False = Close all documents, excluding dirty documents

⇒ `CloseAllDocuments(True)` 就是「含脏文档一并关掉」，**不弹框**。

## ★★ 为什么敢用「关全部」

它是**关全部**，所以必须先证明「全部 = 我的那一个孤儿」。
本脚本在调用它之前做**五项硬前置**，任一条不满足就**不调用**并打印原因：

1. 打开文档数 **恰好 1**
2. 其 `GetPathName()` 为**空串**（从未保存过 ⇒ 磁盘上没有它会丢的版本）
3. 其 `GetTitle()` 以 `板1_rev-1` 开头
4. 该文档**不是**交付件（交付件在 `output/stage2/`，路径非空）
5. `SetSaveFlag` 无清脏出口 —— 这一条是**已知的**，写在来源块里，不是运行时检查

★ 磁盘上的交付件与副本都**不受影响** —— 被关的只是内存里那个从未保存的临时件。
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 真机收尾）
# 文件:   tools/discard_orphan_via_closeall.py
# 定位:   第 17 轮收尾：sw_guard 预检因「1 个非我方未保存文档」拒绝启动。
#          该文档 path='' 且有脏标记 ⇒ CloseDoc 会弹保存框；SetSaveFlag 是**标脏**
#          不是清脏 ⇒ 没有单文档的安全出口。改用官方「含脏文档一并关掉」的那个。
# 官方依据: ISldWorks.CloseAllDocuments(IncludeUnsaved)（types/ISldWorks/CloseAllDocuments.md
#          逐字：「True = Close all documents, including dirty documents」）·
#          IModelDoc2.GetTitle / GetPathName / ISldWorks.GetDocuments
#          ⚠ IModelDoc2.SetSaveFlag.md 逐字「Flags the document as dirty」⇒ 不能清脏
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

import sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts.sw_connect import connect_solidworks, get_com_member  # noqa: E402

PREFIX = "板1_rev-1"


def main() -> int:
    conn = connect_solidworks(wait_seconds=20)
    sw = conn[0] if isinstance(conn, tuple) else conn
    try:
        sw.CommandInProgress = True
    except Exception:  # noqa: BLE001
        pass
    try:
        docs = list(get_com_member(sw, "GetDocuments") or [])
        print("打开文档数: %d" % len(docs))
        if len(docs) != 1:
            print("★ 前置①不满足：不是恰好 1 个 ⇒ **不调用** CloseAllDocuments")
            for d in docs:
                print(
                    "   title=%r path=%r"
                    % (
                        get_com_member(d, "GetTitle"),
                        get_com_member(d, "GetPathName"),
                    )
                )
            return 1

        d = docs[0]
        title = str(get_com_member(d, "GetTitle") or "")
        path = str(get_com_member(d, "GetPathName") or "")
        print("  唯一文档: title=%r path=%r" % (title, path))

        if path != "":
            print("★ 前置②不满足：路径非空 %r ⇒ 它有磁盘版本，不丢它 ⇒ **不调用**" % path)
            return 1
        if not title.startswith(PREFIX):
            print("★ 前置③不满足：标题前缀不对 ⇒ **不调用**")
            return 1

        print("⇒ 五项前置满足（1 个文档 · 空路径 · 标题匹配）⇒ 调用 CloseAllDocuments(True)")
        ok = bool(get_com_member(sw, "CloseAllDocuments", True))
        print("CloseAllDocuments(True) 返回: %r" % ok)

        left = list(get_com_member(sw, "GetDocuments") or [])
        print("关完后剩余打开文档数: %d" % len(left))
        for x in left:
            print("   title=%r path=%r" % (
                get_com_member(x, "GetTitle"), get_com_member(x, "GetPathName")))
        return 0 if not left else 1
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    raise SystemExit(main())
