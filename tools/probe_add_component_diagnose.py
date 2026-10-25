"""★ 诊断：为什么 `AddComponent5` 回 None。

## 已知

真机（第 22 轮）：装配文档**建成了**（title='装配体1'），但加组件失败：

```
添加组件失败: ...\\plate.SLDPRT (open_then_AddComponent5: 返回 None)
```

三条路（`AddComponent5` / `AddComponent4` / 先开零件再加）全回 `None`。
`ConfigOption` 传的 `0` 是**合法值**（`swAddComponentConfigOptions_CurrentSelectedConfig`），
所以不是枚举错。

## 本诊断逐项排除

| # | 查什么 | 判据 |
|---|---|---|
| 1 | 子进程能否看到零件路径 | `os.path.exists` + 大小 |
| 2 | 装配文档类型对不对 | `IModelDoc2.GetType()`（应 = 2 `swDocASSEMBLY`） |
| 3 | 装配是不是活动文档 | `ISldWorks.ActiveDoc` 的 title 对比 |
| 4 | `AddComponent5` 原始返回 | 原样打印，不加工 |
| 5 | 先开零件 + 激活装配后再加 | 换顺序再试一次 |

★ 只读 + 只在内存里建文档；收尾核文档数。
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_assembly as a_  # noqa: E402
from scripts import sw_connect as c_  # noqa: E402
from scripts.sw_connect import get_com_member, open_doc_count  # noqa: E402
from scripts.sw_connect import try_call as _try  # noqa: E402
from scripts.sw_connect import try_member as _member  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 诊断）
# 文件:   tools/probe_add_component_diagnose.py
# 定位:   查明 `assembly_and_mates` 卡在 `IAssemblyDoc.AddComponent5` 回 None 的原因。
#          逐项排除「路径看不到 / 文档类型不对 / 不是活动文档 / 参数取值非法」。
# 官方依据: IAssemblyDoc.AddComponent5（8 参）·
#          swAddComponentConfigOptions_e（swAddComponentConfigOptions_CurrentSelectedConfig = 0，
#          ★ 已核：0 是合法值，不是本 bug 的原因）· IModelDoc2.GetType / GetTitle ·
#          ISldWorks.ActiveDoc
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

SRC = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
WORK = R / "output" / "s4-assembly"


def main() -> int:
    ev: dict = {"probe": "add-component-diagnose"}
    sw = asm = part_doc = None
    try:
        WORK.mkdir(parents=True, exist_ok=True)
        part = WORK / "plate_diag.SLDPRT"
        shutil.copy2(SRC, part)

        #: ① 子进程视角下的路径
        ev["path"] = {
            "abs": str(part.resolve()),
            "exists": os.path.exists(str(part)),
            "size": os.path.getsize(str(part)) if part.is_file() else None,
        }
        print("① 路径可见性：exists=%s size=%s" % (ev["path"]["exists"], ev["path"]["size"]))

        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        ok_n, asm = _try(c_.new_document, sw, "assembly")
        if not ok_n or asm is None:
            print("★ 建不了装配")
            return 1
        #: ② 文档类型
        ev["asm_type"] = _member(asm, "GetType")
        ev["asm_title"] = str(_member(asm, "GetTitle") or "")
        ev["asm_path"] = str(_member(asm, "GetPathName") or "")
        print("② 装配：GetType=%s（应 2）title=%r path=%r"
              % (ev["asm_type"], ev["asm_title"], ev["asm_path"]))

        #: ③ 是不是活动文档
        active = _member(sw, "ActiveDoc")
        ev["active_title"] = str(_member(active, "GetTitle") or "") if active else None
        ev["is_active"] = ev["active_title"] == ev["asm_title"]
        print("③ 活动文档=%r · 是装配=%s" % (ev["active_title"], ev["is_active"]))

        #: ④ AddComponent5 原始返回
        ok5, raw5 = _try(
            lambda: get_com_member(
                asm, "AddComponent5", str(part), 0, "", False, "", 0.0, 0.0, 0.0
            )
        )
        ev["add5"] = {"ok": ok5, "type": type(raw5).__name__, "repr": repr(raw5)[:160]}
        print("④ AddComponent5 原始：ok=%s type=%s repr=%r"
              % (ok5, type(raw5).__name__, raw5))

        #: ⑤ 先开零件、再激活装配、再加
        ok_o, part_doc = _try(c_.open_document, sw, str(part))
        ev["open_part"] = {"ok": ok_o, "detail": str(part_doc)[:100]}
        if ok_o and part_doc is not None:
            ok_act, _ = _try(lambda: get_com_member(sw, "ActivateDoc3", ev["asm_title"],
                                                    False, 0, None, None))
            ev["activate_asm"] = ok_act
            active2 = _member(sw, "ActiveDoc")
            ev["active_after"] = str(_member(active2, "GetTitle") or "") if active2 else None
            ok5b, raw5b = _try(
                lambda: get_com_member(
                    asm, "AddComponent5", str(part), 0, "", False, "", 0.0, 0.0, 0.0
                )
            )
            ev["add5_after_open"] = {
                "ok": ok5b, "type": type(raw5b).__name__, "repr": repr(raw5b)[:160],
            }
            print("⑤ 开零件+激活装配后再加：activate=%s active=%r add5=%r"
                  % (ok_act, ev["active_after"], raw5b))

        #: ⑥ 假设：**装配未保存（path=''）⇒ 没有相对路径基准** ⇒ 先保存再加
        asm_path = str(WORK / "asm_diag.SLDASM")
        ok_sv, ret_sv = _try(c_.save_document, asm, asm_path)
        ev["save_asm"] = {"ok": ok_sv, "detail": str(ret_sv)[:100],
                          "path_after": str(_member(asm, "GetPathName") or "")}
        print("⑥ 保存装配：ok=%s path=%r" % (ok_sv, ev["save_asm"]["path_after"]))
        if ok_sv:
            ok5c, raw5c = _try(
                lambda: get_com_member(
                    asm, "AddComponent5", str(part), 0, "", False, "", 0.0, 0.0, 0.0
                )
            )
            ev["add5_after_save"] = {
                "ok": ok5c, "type": type(raw5c).__name__, "repr": repr(raw5c)[:160],
            }
            print("   保存后再加：add5=%r" % (raw5c,))

        #: ⑦ 组件数
        okc, comps = _try(a_.get_components, asm)
        ev["components"] = len(list(comps)) if okc and comps else 0
        print("⑦ 组件数=%s" % ev["components"])

        ev["conclusion"] = (
            "★ 加组件成功，组件数 %s" % ev["components"]
            if ev["components"] > 0
            else "★ 全部路径仍回 None —— 见 ④/⑤ 的 repr 与 ①②③ 的前置读数"
        )
        print(ev["conclusion"])
        return 0 if ev["components"] > 0 else 1
    except Exception as exc:  # noqa: BLE001
        import traceback

        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        ev["traceback"] = traceback.format_exc()[-1000:]
        print("★ 失败：", ev["err"])
        return 1
    finally:
        if sw is not None:
            for d in (part_doc, asm):
                if d is not None:
                    t = str(_member(d, "GetTitle") or "")
                    if t:
                        _try(sw.CloseDoc, t)
            ev["docs_left"] = open_doc_count(sw)
            print("   收尾后剩余文档数：%s" % ev["docs_left"])
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
        ev["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        dest = R / "output" / "add-component-diagnose.json"
        dest.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("   证据已写：%s" % dest)


if __name__ == "__main__":
    raise SystemExit(main())
