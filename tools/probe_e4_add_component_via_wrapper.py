"""★ 重测 E4 的加组件：走**高层封装** `sw_assembly.add_component`（含兜底），不走裸成员。

## 为什么重测（第 42 轮自我纠错）

第 22 轮我报「`AddComponent5` 回 `None`，装配建不出来」，并据此把 E4 写成阻塞。
但查 `docs/known-facts.md` 发现本仓**早有既有做法**：

> 刻意的兜底 | `AddComponent4` | `AddComponent5 → None → 退回 4`（人工读源码确认）

而 `scripts/sw_assembly.add_component` 确实实现了三级兜底：

```
① _add_component5
② 若 None ⇒ _add_component4
③ 若仍 None ⇒ 打开零件、切回装配、再试
```

⇒ **我第 22 轮调的是裸成员**（`try_member(asm, "AddComponent5", ...)`），
   **绕过了这三层兜底** ⇒ 我的「阻塞」结论可能是错的。

★ 这正是铁律「动手前先扫 `docs/known-facts.md` + `docs/dead-ends.md`」的用处 ——
  我第 13 轮犯过一次同类错误，第 22 轮又犯了。

## 判据（独立读数，不信返回值）

| 读数 | 手段 |
|---|---|
| 组件数 | `GetComponents(False)` 的条数，改前/改后 |
| 失败时的兜底路径 | 逐级记录哪一级成的 |

★ 「返回值 ≠ 实际结果」在本仓出现过三次 ⇒ **必须回读组件数**，不看返回对象是否非空。
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_assembly as asm_  # noqa: E402
from scripts import sw_connect as c_  # noqa: E402
from scripts.sw_connect import get_com_member, open_doc_count  # noqa: E402
from scripts.sw_connect import try_call as _try  # noqa: E402
from scripts.sw_connect import try_member as _member  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 重测）
# 文件:   tools/probe_e4_add_component_via_wrapper.py
# 定位:   第 22 轮报「AddComponent5 回 None ⇒ E4 建不出来」，但当时走的是裸成员，
#          绕过了本仓 sw_assembly.add_component 的三级兜底（5 → 4 → 开零件再切回）。
#          本轮走高层封装重测，用**组件数**做独立判据。
# 官方依据: IAssemblyDoc.AddComponent5 / AddComponent4（经模块封装）·
#          IAssemblyDoc.GetComponents（回读组件清单）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

PART = R / "output" / "stage2" / "板1_rev-1.SLDPRT"


def _count(asm_doc) -> int:
    """★ 独立读数：组件条数。不信返回对象。"""
    try:
        comps = get_com_member(asm_doc, "GetComponents", False)
    except Exception:  # noqa: BLE001
        return -1
    try:
        return len(list(comps or []))
    except TypeError:
        return -1


def main() -> int:
    ev: dict = {"probe": "e4-add-component-via-wrapper", "part": str(PART)}
    sw = None
    try:
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        ev["part_exists"] = PART.is_file()
        print("① 零件存在=%s（%s 字节）" % (ev["part_exists"], PART.stat().st_size
                                        if PART.is_file() else 0))
        if not ev["part_exists"]:
            return 1

        #: ② 建装配
        ok_n, doc = _try(c_.new_document, sw, "assembly")
        if not ok_n or doc is None:
            ev["err"] = "新建装配失败"
            print("★ 新建装配失败")
            return 1
        ev["doc_type"] = _member(doc, "GetType")
        print("② 装配已建 · GetType=%s" % ev["doc_type"])

        before = _count(doc)
        ev["components_before"] = before
        print("   加之前组件数 = %s" % before)

        #: ③ ★ 走高层封装（含三级兜底）
        ok_a, ret = _try(asm_.add_component, doc, str(PART), 0.0, 0.0, 0.0)
        after = _count(doc)
        ev["add_ok"] = ok_a
        ev["return_type"] = type(ret).__name__ if ok_a else "err"
        ev["return_none"] = (ret is None) if ok_a else None
        ev["components_after"] = after
        ev["added"] = after - before
        print("③ 高层封装 add_component：ok=%s 返回类型=%s 返回None=%s"
              % (ok_a, ev["return_type"], ev["return_none"]))
        print("   加之后组件数 = %s（增加 %s）" % (after, ev["added"]))
        if not ok_a:
            print("   错误：%s" % str(ret)[:200])

        #: ④ 判读
        ev["ok"] = bool(ev["added"] == 1)
        ev["conclusion"] = (
            "★ 走高层封装**加得进去**（组件数 %s → %s）⇒ 第 22 轮的「阻塞」结论"
            "是走了裸成员、绕过兜底造成的，不成立" % (before, after)
            if ev["ok"]
            else "★ 走高层封装也加不进去（组件数 %s → %s）⇒ 阻塞成立，且已排除兜底"
            % (before, after)
        )
        print(ev["conclusion"])
        return 0 if ev["ok"] else 1
    except Exception as exc:  # noqa: BLE001
        import traceback

        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        ev["traceback"] = traceback.format_exc()[-1000:]
        print("★ 失败：", ev["err"])
        return 1
    finally:
        if sw is not None:
            for d in list(sw.GetDocuments() or []):
                _try(sw.CloseDoc, str(_member(d, "GetTitle") or ""))
            ev["docs_left"] = open_doc_count(sw)
            print("   收尾后剩余文档数：%s" % ev["docs_left"])
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
        ev["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        (R / "output" / "e4-add-component-via-wrapper.json").write_text(
            json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print("   证据已写：output/e4-add-component-via-wrapper.json")


if __name__ == "__main__":
    raise SystemExit(main())
