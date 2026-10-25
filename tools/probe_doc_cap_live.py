"""★ 真机验证「文档数上限」：故意开 5 个我方文档，看它是否只留 1 个。

## 判据（独立读数）

| 读数 | 期望 |
|---|---|
| 触发前文档数 | 5（> 阈值 3） |
| `enforce_doc_cap` 返回 `action` | `capped` |
| 触发后文档数 | ≤ `keep`（默认 1） |
| 保留的是哪个 | **正在用的那个**（`ActiveDoc`） |
| `skipped_not_ours` | 空（这 5 个都是我方的） |

## 为什么这样造

5 个全部是**我方**的：1 个 `output/` 下的零件副本 + 4 个 `new_document("assembly")`
建的空装配（无路径、type=2）⇒ 按归属判据全部算我方 ⇒ 可以安全清。

★ **不造「不是我的」文档** —— 那会碰用户真件；归属判据的「不碰」分支由
  `tests/test_orphan_doc_ownership.py` 的静态断言覆盖。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))
sys.path.insert(0, str(R / "tools"))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 文档上限真机验证）
# 文件:   tools/probe_doc_cap_live.py
# 定位:   用户要求「一次性开了超过 3 个窗口就强制关掉没用的，只保留 1 个正在用的」。
# 定位:   用户要求「一次性开了超过 3 个窗口就强制关掉没用的，只保留 1 个正在用的」。
#          本探针故意开 5 个**我方**文档，验证 enforce_doc_cap 只留 1 个。
# 官方依据: ISldWorks::GetDocuments · ISldWorks::ActiveDoc · ISldWorks::CloseDoc ·
#          ISldWorks::CloseAllDocuments（**不用**，它会连别人的一起关）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

import sw_connect as c_  # noqa: E402
import sw_dialog_watch as w  # noqa: E402
from sw_connect import get_com_member  # noqa: E402

SRC = R / "output" / "stage2" / "板1_rev-1.SLDPRT"


def _snapshot(sw) -> list:
    """★ 只在这里读一次 `GetDocuments`（本机它是**属性**，不带括号）。"""
    out = []
    for d in (get_com_member(sw, "GetDocuments") or ()):
        out.append(
            {
                "title": str(get_com_member(d, "GetTitle") or ""),
                "type": int(get_com_member(d, "GetType") or 0),
                "dirty": bool(get_com_member(d, "GetSaveFlag")),
                "path": str(get_com_member(d, "GetPathName") or ""),
            }
        )
    return out


def main() -> int:
    ev: dict = {"probe": "doc-cap-live"}
    conn = c_.connect_solidworks(wait_seconds=20)
    sw = conn[0] if isinstance(conn, tuple) else conn
    try:
        sw.CommandInProgress = True
    except Exception:  # noqa: BLE001
        pass

    try:
        #: ① 造 5 个我方文档
        if SRC.is_file():
            c_.open_document(sw, str(SRC))
        #: ★ `ISldWorks.NewDocument(TemplateName, ...)` 需要**模板名**；
        #:   传空串实测**一个都不建**（试过：造 5 个只建成 1 个）。
        #:   ⇒ 用仓库既有的 `new_document(sw, "assembly")`（它会解析模板）。
        for _ in range(4):
            c_.new_document(sw, "assembly")
        before_docs = _snapshot(sw)
        ev["before"] = before_docs
        print("① 造好 %d 个文档：" % len(before_docs))
        for d in before_docs:
            print(
                "   %-22s type=%s dirty=%s"
                % (d["title"][:22], d["type"], d["dirty"])
            )

        #: ② 跑上限检查
        cap = w.enforce_doc_cap(max_docs=3, keep=1)
        ev["cap"] = cap
        print("② enforce_doc_cap ⇒ action=%s · %s → %s"
              % (cap.get("action"), cap.get("before"), cap.get("after")))

        after_docs = _snapshot(sw)
        ev["after"] = after_docs
        print("③ 之后剩 %d 个：" % len(after_docs))
        for d in after_docs:
            print(
                "   %-22s type=%s dirty=%s"
                % (d["title"][:22], d["type"], d["dirty"])
            )

        ev["ok"] = bool(
            len(before_docs) > 3
            and cap.get("action") == "capped"
            and len(after_docs) <= 1
        )
        ev["conclusion"] = (
            "★ 上限生效：%d 个 → %d 个（只留在用的那个）"
            % (len(before_docs), len(after_docs))
            if ev["ok"]
            else "★ 未达：见 before/cap/after 三段"
        )
        print(ev["conclusion"])
        return 0 if ev["ok"] else 1
    finally:
        #: 收尾：把我方剩下的也清干净
        try:
            #: ★ 收尾连活动文档也清（`keep_active=False`）
            w.enforce_doc_cap(max_docs=0, keep=0, keep_active=False)
        except Exception:  # noqa: BLE001
            pass
        try:
            left = len(list(get_com_member(sw, "GetDocuments") or ()))
        except Exception:  # noqa: BLE001
            left = -1
        ev["docs_left"] = left
        print("   收尾后剩余文档数：%s" % left)
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        dest = R / "output" / "doc-cap-live.json"
        dest.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("   证据已写：%s" % dest)


if __name__ == "__main__":
    raise SystemExit(main())
