r"""@brief 探针：`mold_evidence` 在真机上**全 None** —— 是"空件没有"还是"**读法不对**"？

## 为什么（轮 172）
`sw_mold.mold_evidence()` 在**新零件**上返回**全 None**（连 `parting_type` / `core_cavity_split` 都是）。
⚠ 但"没有分型面"应当是 **0**，不是 `None` ⇒ ★ 可疑：**读法**可能不对。
★ 本仓库有**两种**取成员的方式（轮 145 的命名迁移正是为此）：
```
get_com_member(...)   —— 取**值**（属性）
call_com_member(...)  —— **调用**（方法）
```
⇒ 本探针**两种都试**，并**分辨**「返回 None」与「返回 0」。

## 判据（能被空操作证伪）
```
① 同一成员，`get_` 与 `call_` 两种取法**分别**记录结果与异常
② 若 `call_` 拿到 **0**（int）而 `get_` 拿到 None ⇒ ★★ **说明 `mold_evidence` 读法不对**（真 bug）
③ 若两者都 None / 都异常 ⇒ 说明**这些入口在空件上确实取不到**（另当别论，需换对象验证）
```

## ⚠ 安全
只在新零件上；`CommandInProgress` 复位；收尾**轮询点掉**；关件不保存。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_mold_evidence_readers.py
# 定位:   给 Spec Kit `092` 判定 `mold_evidence` 的读法是否正确。
# 官方依据: `sw_mold.py::mold_evidence` 的 docstring（GetPartingLinesCount / … /
#          PartingType / CoreCavitySplit）；`sw_connect` 的 get_com_member / call_com_member 分工
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(r"D:\AI\SW\output\mold-evidence-readers.json")

#: (持有者, 成员名, 是不是"方法"（名字看着像动词/复数计数）)
TARGETS = [
    ("fm", "GetPartingLinesCount", True),
    ("fm", "GetPartingSurfacesCount", True),
    ("fm", "GetCavitySurfacesCount", True),
    ("fm", "GetCoreSurfacesCount", True),
    ("fm", "GetPartingLineCount", True),      #: 单数形态（对照）
    ("model", "PartingType", False),
    ("model", "CoreCavitySplit", False),
]


def main() -> int:
    ev: dict = {"rows": []}
    sw = None
    doc = None
    try:
        import sw_connect
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:      # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")
        fm = sw_connect.get_com_member(doc, "FeatureManager")
        holders = {"fm": fm, "model": doc}

        for who, name, is_method in TARGETS:
            owner = holders[who]
            row = {"who": who, "member": name}
            for label, fn in (("get_", sw_connect.get_com_member),
                              ("call_", sw_connect.call_com_member)):
                try:
                    v = fn(owner, name)
                    row[label] = "%s:%r" % (type(v).__name__, v)
                except TypeError:
                    try:
                        v = fn(owner, name)
                        row[label] = "%s:%r" % (type(v).__name__, v)
                    except Exception as exc:      # noqa: BLE001
                        row[label] = "EXC:%s" % type(exc).__name__
                except Exception as exc:      # noqa: BLE001
                    row[label] = "EXC:%s:%s" % (type(exc).__name__, str(exc)[:30])
            ev["rows"].append(row)
            print("  %-8s %-26s get_=%-24s call_=%s"
                  % (who, name, row["get_"][:24], row["call_"][:30]))
    except Exception as exc:      # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        print("  ⚠ 探针出错: %s" % ev["error"])
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:      # noqa: BLE001
            pass

    import sw_connect as _sc
    found, dismissed, scanned = _sc.settle_residual_dialogs(settle_seconds=1.0)
    print("  收尾：发现 %d · 点掉 %d · 扫了 %d 个窗口" % (found, dismissed, scanned))
    ev["cleanup"] = {"found": found, "scanned": scanned}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
