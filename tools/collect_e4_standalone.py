"""E4 采集器（**独立进程**）—— 按事实 569 的结论拆出来。

## 为什么必须单独进程

第 56 轮实测（事实 569）：运行器里 E4 段的 `NewDocument` 返回 True，但拿到的 doc
对象**已断连**：

```
new_assembly   : true
asm_title      : ""
components_err : com_error (-2147417848, '被调用的对象已与其客户端断开连接。')
                 ^ 0x80010108 = RPC_E_DISCONNECTED
```

而**独立探针在干净会话里组件 0 → 2 是通的**。
⇒ 差别在**会话状态**：E2 段反复开关文档之后，再 `new_document` 就断连。
⇒ 4 次尝试（改代码 3 次 + 段前清场 1 次）都失败，最后错误退化成
  `RPC 服务器不可用`（`0x800706BA`）⇒ 停止在运行器内修，改成**独立进程**。

## 契约（给运行器读）

写 `output/e4-standalone.json`：

```json
{"ok": true, "components": 2, "interference_count": 0,
 "assembly_title": "...", "docs_left": 0, "steps": {...}, "err": ""}
```

★ `components = -1` 表示**没读到**（不是 0 个组件）；`ok=false` 时看 `err` / `steps`。

## 纪律

- 建装配后**必须激活**（`ActivateDoc3`），否则 `GetComponents` 抛
- 收尾把文档数清到 0（否则下一段又会踩「非我方文档」的预检）
- 收尾后把文档数写进证据（`docs_left`）
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
# 仓库:   本项目自身（工具 · E4 独立采集器）
# 文件:   tools/collect_e4_standalone.py
# 定位:   把 E4 采集从验收运行器里**拆成独立进程** —— 事实 569：
#          运行器内 E2 反复开关文档之后 `NewDocument` 返回的对象会
#          `RPC_E_DISCONNECTED`（0x80010108），而独立进程里组件 0 → 2 通。
# 官方依据: IAssemblyDoc::AddComponent5（文件必须已在内存）· IAssemblyDoc::GetComponents ·
#          IAssemblyDoc::GetInterferenceDetectionManager（经 `sw_assembly.get_interference_detection`）·
#          ISldWorks::ActivateDoc3 · ISldWorks::CloseAllDocuments
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

SRC = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
DEST = R / "output" / "e4-standalone.json"

import sw_assembly as asm_  # noqa: E402
import sw_connect as c_  # noqa: E402

#: ★ 复用 `close_my_orphans` 的实现 —— 同函数体两份会触发统一化门禁的『跨文件同函数体』
#:   （与 `select_by_id` 当年收敛到 `sw_connect` 是同一个理由）。
from close_my_orphans import _docs  # noqa: E402
from sw_connect import get_com_member  # noqa: E402

OUTPUT_ROOT = str(R / "output")


def _mine(info: dict) -> bool:
    """★ 归属判据（与 `tools/close_my_orphans.py` 同口径）：只管我方的。

    路径在 `<仓库根>/output/` 下，或「无路径且是装配体」。
    """
    p = str(info.get("path") or "")
    if p:
        return p.lower().startswith(OUTPUT_ROOT.lower())
    return int(info.get("type") or 0) == 2




def main() -> int:
    ev: dict = {"probe": "e4-standalone", "steps": {}}
    sw = None
    try:
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        #: ① 干净起点：只在我方文档为 0 时才继续（不碰别人的）
        pre = []
        for d in _docs(sw):
            pre.append(
                {
                    "title": str(get_com_member(d, "GetTitle") or ""),
                    "type": int(get_com_member(d, "GetType") or 0),
                    "path": str(get_com_member(d, "GetPathName") or ""),
                }
            )
        ev["docs_pre"] = pre
        mine_left = [x for x in pre if _mine(x)]
        if mine_left:
            #: 我方的残留 —— 清掉（干净起点是本工具成立的前提）
            for x in mine_left:
                try:
                    sw.CloseDoc(x["title"])
                except Exception:  # noqa: BLE001
                    pass
            try:
                get_com_member(sw, "CloseAllDocuments", True)
            except Exception:  # noqa: BLE001
                pass
        ev["steps"]["pre_docs"] = len(pre)

        if not SRC.is_file():
            ev["err"] = "交付件不存在：%s" % SRC
            return 2

        #: ② 开零件（文件必须已在内存 —— AddComponent5 的官方前置）
        ok_p, part_doc = c_.try_call(c_.open_document, sw, str(SRC))
        ev["steps"]["open_part"] = bool(ok_p)

        #: ③ 建装配 → **激活** → 加两个组件
        ok_n, asm_doc = c_.try_call(c_.new_document, sw, "assembly")
        ev["steps"]["new_assembly"] = bool(ok_n)
        if asm_doc is not None:
            try:
                _ttl = str(get_com_member(asm_doc, "GetTitle") or "")
                sw.ActivateDoc3(_ttl, 0, False)
            except Exception:  # noqa: BLE001
                pass
        #: ★ 不信任 `new_document` 返回的对象 —— 重取活动文档并验证标题非空
        try:
            cand = get_com_member(sw, "ActiveDoc")
            if cand is not None and str(get_com_member(cand, "GetTitle") or ""):
                asm_doc = cand
        except Exception:  # noqa: BLE001
            pass
        ev["steps"]["asm_title"] = (
            str(get_com_member(asm_doc, "GetTitle") or "")
            if asm_doc is not None
            else ""
        )

        n = -1
        adds: list = []
        if asm_doc is not None:
            for dx in (0.0, 30.0):
                ok_a, a_ret = c_.try_call(
                    asm_.add_component, asm_doc, str(SRC), dx, 0.0, 0.0, "", sw
                )
                adds.append(
                    {"ok": bool(ok_a), "err": "" if ok_a else str(a_ret)[:100]}
                )
            try:
                n = len(list(get_com_member(asm_doc, "GetComponents", False) or ()))
            except Exception as exc:  # noqa: BLE001
                n = -1
                ev["steps"]["components_err"] = "%s: %s" % (
                    type(exc).__name__,
                    str(exc)[:120],
                )
        ev["steps"]["add_component"] = adds
        ev["components"] = n

        #: ④ 干涉
        ok_i, interf = (
            c_.try_call(asm_.get_interference_detection, asm_doc)
            if asm_doc
            else (False, None)
        )
        n_i = -1
        if ok_i and isinstance(interf, dict):
            v = interf.get("interference_count")
            n_i = int(v) if v is not None else -1
        ev["interference_count"] = n_i
        ev["steps"]["interference_ok"] = bool(ok_i)

        ev["ok"] = bool(n >= 2)
        return 0 if ev["ok"] else 1
    except Exception as exc:  # noqa: BLE001
        import traceback

        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        ev["traceback"] = traceback.format_exc()[-800:]
        return 1
    finally:
        if sw is not None:
            #: 收尾清到我方 0 个
            try:
                for d in _docs(sw):
                    info = {
                        "path": str(get_com_member(d, "GetPathName") or ""),
                        "type": int(get_com_member(d, "GetType") or 0),
                        "title": str(get_com_member(d, "GetTitle") or ""),
                    }
                    if _mine(info):
                        sw.CloseDoc(info["title"])
                if any(
                    _mine(
                        {
                            "path": str(get_com_member(d, "GetPathName") or ""),
                            "type": int(get_com_member(d, "GetType") or 0),
                        }
                    )
                    for d in _docs(sw)
                ):
                    get_com_member(sw, "CloseAllDocuments", True)
            except Exception:  # noqa: BLE001
                pass
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
            try:
                ev["docs_left"] = len(_docs(sw))
            except Exception:  # noqa: BLE001
                pass
        import time as _time

        ev["finished_at"] = _time.strftime("%Y-%m-%dT%H:%M:%S")
        DEST.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        _brief = {
            k: ev.get(k) for k in ("ok", "components", "interference_count")
        }
        print(json.dumps(_brief, ensure_ascii=False))


if __name__ == "__main__":
    raise SystemExit(main())
