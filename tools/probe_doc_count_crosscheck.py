"""★ 核对 `open_doc_count` 与已验证的 `probe_list_open_docs` 是否一致。

## 为什么要查

第 22 轮装配探针报「收尾后剩余文档数：**2**」，
而同一次真机上 `tools/probe_list_open_docs.py`（早前验过的只读探针）报「合计 **0** 个」。

两者用的是同一个成员 `ISldWorks.GetDocuments`，读数却不一致 ⇒
**至少有一个错**。而 `open_doc_count` 从第 18 轮起被我当作「关闭成功」的判据
⇒ 如果它错，前几轮那些「1 → 0 · closed True」的结论都要重新看。

## 怎么查

把 `GetDocuments` 的原始返回**原样打出来**（类型 / 长度 / 每个元素的类型），
再与两份各自的计数对照 —— 不猜，看数。
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as c_  # noqa: E402
from scripts.sw_connect import get_com_member, open_doc_count  # noqa: E402
from scripts.sw_connect import try_call as _try  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 诊断）
# 文件:   tools/probe_doc_count_crosscheck.py
# 定位:   `open_doc_count` 与 `probe_list_open_docs` 对同一会话给出不同计数
#          （2 vs 0）。而 `open_doc_count` 是「关闭成功」的判据 ⇒ 必须核定谁对。
# 官方依据: ISldWorks.GetDocuments（签名与返回形状见 C:\swapi）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


def main() -> int:
    ev: dict = {"probe": "doc-count-crosscheck"}
    conn = c_.connect_solidworks(wait_seconds=20)
    sw = conn[0] if isinstance(conn, tuple) else conn
    try:
        sw.CommandInProgress = True
    except Exception:  # noqa: BLE001
        pass
    try:
        ok, raw = _try(get_com_member, sw, "GetDocuments")
        ev["get_documents"] = {
            "ok": ok,
            "python_type": type(raw).__name__,
            "repr_head": repr(raw)[:200],
        }
        print("GetDocuments: ok=%s · 类型=%s" % (ok, type(raw).__name__))
        print("  原样：%r" % (raw, )[:200])
        if ok and raw is not None:
            try:
                items = list(raw)
                ev["len"] = len(items)
                print("  len() = %d" % len(items))
                for i, d in enumerate(items):
                    t = None
                    p = None
                    try:
                        t = get_com_member(d, "GetTitle")
                    except Exception as exc:  # noqa: BLE001
                        t = "err: %s" % str(exc)[:50]
                    try:
                        p = get_com_member(d, "GetPathName")
                    except Exception as exc:  # noqa: BLE001
                        p = "err: %s" % str(exc)[:50]
                    print("    [%d] type=%s title=%r path=%r"
                          % (i, type(d).__name__, t, p))
            except TypeError as exc:
                ev["len"] = "不可迭代：%s" % str(exc)[:80]
                print("  ★ 不可迭代：%s" % str(exc)[:80])
        ev["open_doc_count_ours"] = open_doc_count(sw)
        print("open_doc_count(本仓实现) = %s" % ev["open_doc_count_ours"])
        ev["verdict"] = {
            "get_documents_none": raw is None,
            "our_count": ev["open_doc_count_ours"],
            "raw_len": ev.get("len"),
        }
        #: ★ 若 raw 是 None，正确计数应为 0；若 ours 不是 0，就是我们的错
        if raw is None and ev["open_doc_count_ours"] != 0:
            ev["found_bug"] = (
                "★ GetDocuments 回 None，而 open_doc_count 回 %s ⇒ 我们的实现数错了"
                % ev["open_doc_count_ours"]
            )
        print("核对结论：%s" % json.dumps(ev["verdict"], ensure_ascii=False))
        return 0
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        ev["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        dest = R / "output" / "doc-count-crosscheck.json"
        dest.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("证据已写：%s" % dest)


if __name__ == "__main__":
    raise SystemExit(main())
