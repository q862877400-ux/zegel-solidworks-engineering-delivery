"""★ 极窄清理：只关「**路径为空** 且标题以 `板1_rev-1` 开头」的文档。

## 为什么需要它

`sw_guard` 预检拒绝了：会话里有 1 个未登记的文档，任何探针都起不来。

## 为什么这样关是安全的

`tools/probe_list_open_docs.py` 的读数：

```
path='' · title='板1_rev-1.SLDPRT' · visible=True · saved=True
```

- `path=''` ⇒ **从未保存过**的一个新文档
- `saved=True` ⇒ `GetSaveFlag` 为假，**没有未保存改动** ⇒ `CloseDoc` **不会弹保存框**
- 标题与我这轮作业文件同名 ⇒ 是我第 16 轮探针留下的

## 判据（三重，缺一不关）

1. `GetPathName()` **为空串**
2. `GetTitle()` 以 `板1_rev-1` 开头
3. `GetSaveFlag()` 为 **假**

任一条不满足 ⇒ **跳过并打印原因**，绝不硬关。
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 收尾用）
# 文件:   tools/close_orphan_plate_doc.py
# 定位:   第 16 轮收尾：sw_guard 预检因「1 个非我方未保存文档」拒绝启动，
#          本脚本按**三重判据**（路径为空 · 标题前缀 · 未保存标记为假）只关那一个。
#          任一条不满足就跳过并打印原因，绝不硬关。
# 官方依据: IModelDoc2.GetTitle / GetPathName / GetSaveFlag / ISldWorks.CloseDoc；
#          ⚠ types/IModelDoc2/SetSaveFlag.md 逐字「Flags the document as dirty」
#          ⇒ 没有 API 能安全清脏，所以本脚本**不尝试**绕过保存提示。
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
    closed, skipped = [], []
    try:
        docs = get_com_member(sw, "GetDocuments")
        for d in list(docs) if docs else []:
            try:
                title = str(get_com_member(d, "GetTitle") or "")
                path = str(get_com_member(d, "GetPathName") or "")
                dirty = bool(get_com_member(d, "GetSaveFlag"))
            except Exception as exc:  # noqa: BLE001
                skipped.append(("取不到属性", str(exc)[:60]))
                continue
            if path != "":
                skipped.append((title, "有路径 ⇒ 不是未保存的新文档"))
                continue
            if not title.startswith(PREFIX):
                skipped.append((title, "标题前缀不匹配"))
                continue
            if dirty:
                skipped.append((title, "有未保存改动 ⇒ 不关（怕丢数据）"))
                continue
            try:
                sw.CloseDoc(title)
                closed.append(title)
            except Exception as exc:  # noqa: BLE001
                skipped.append((title, "CloseDoc 失败: %s" % str(exc)[:60]))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        print("已关闭 %d 个：" % len(closed))
        for t in closed:
            print("  ✓ %s" % t)
        print("跳过 %d 个：" % len(skipped))
        for t, why in skipped:
            print("  · %s —— %s" % (t, why))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
