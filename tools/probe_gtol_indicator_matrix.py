r"""@brief 探针：`IGtolFrame.AddIndicator` 的**可行组合矩阵**（border × tol 全试一遍）。

## 为什么（轮 166 的实况）
```
轮 165：帧路径通了（ConvertFormat → AddFrame → GetFrame **拿到对象**）
轮 166：改 `TolType` 为**官方允许清单里**的值（parallelism=22 / perpendicularity=21）
        ⇒ **仍返回 False** ⇒ ★ 类型不是唯一卡点
⚠ 已在这同一处试 2 次 ⇒ 本探针做**矩阵**（一次穷尽），试完无论成败都**停手**（事实 53）
```

## 要试的维度（都取自官方枚举，不猜）
```
BorderType : swGtolIndicatorBorderType_e = 0..3      ⇒ 4 种
TolType    : 官方 Remarks 只允许这 5 个 ⇒ 20 · 22 · 21 · 25 · 13
Datum      : "" 与 "A" 两种（官方：Datum 是"指向 BorderType 的基准符号"）
⇒ 逐个试，**每个组合都用新 Gtol**（避免状态污染）
```

## 判据
```
★ `AddIndicator` **返回 True**（唯一的成功信号；⚠ 若全 False ⇒ 如实报"20 组全不成"）
```

## ⚠ 安全
**只在新零件上跑**；收尾**关件不保存** + **查模态框**。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_gtol_indicator_matrix.py
# 定位:   给 Spec Kit `086` 判定 `AddIndicator` 是**参数组合没找对**还是**真到不了**。
# 官方依据: `C:/swapi/types/IGtolFrame/AddIndicator.md`（Remarks 列出允许的 5 个 TolType
#           ）·
#          `swGtolIndicatorBorderType_e` = 0..3 · `swGtolGeomCharSymbol_e`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import itertools
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "gtol-indicator-matrix.json"
)
TOL_TYPES = [20, 22, 21, 25, 13]  #: 官方 Remarks 允许的 5 个
BORDERS = [0, 1, 2, 3]  #: swGtolIndicatorBorderType_e


def main() -> int:
    ev: dict = {"trials": [], "success": None}
    sw = None
    try:
        import sw_connect
        from scripts import sw_gtol

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        found = None
        for border, tol in itertools.product(BORDERS, TOL_TYPES):
            doc = sw_connect.new_document(sw, "part")
            rec = {"border": border, "tol": tol}
            try:
                gtol = sw_gtol.insert_gtol(doc)
                if gtol is None:
                    rec["err"] = "insert_gtol 返回 None"
                else:
                    #: 帧：先转换再加帧（轮 165 的结论）
                    sw_gtol.ensure_gtol_frame(gtol, 1)
                    f = sw_connect.safe_get_com_member(gtol, "GetFrame", 1)
                    rec["frame"] = "有" if f is not None else "**None**"
                    if f is not None:
                        r = sw_connect.safe_get_com_member(
                            f, "AddIndicator", border, tol, ""
                        )
                        rec["ret"] = repr(r)
                        if r:
                            found = rec
            except Exception as exc:  # noqa: BLE001
                rec["exc"] = "%s: %s" % (type(exc).__name__, str(exc)[:50])
            ev["trials"].append(rec)
            try:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
            except Exception:  # noqa: BLE001
                pass
            if found:
                break

        n_true = sum(1 for r in ev["trials"] if str(r.get("ret")) == "True")
        print(
            "  试了 **%d** 组（border × tol）· 返回 True 的 **%d** 组"
            % (len(ev["trials"]), n_true)
        )
        for r in ev["trials"][:24]:
            print(
                "    border=%s tol=%-3s 帧=%-6s 返回=%-6s %s"
                % (
                    r["border"],
                    r["tol"],
                    r.get("frame", "—"),
                    str(r.get("ret", r.get("exc", "—")))[:6],
                    r.get("err", ""),
                )
            )
        if found:
            print()
            print(
                "  ★★ **可行组合：border=%s · tol=%s**"
                % (found["border"], found["tol"])
            )
            ev["success"] = {"border": found["border"], "tol": found["tol"]}
        else:
            print()
            print(
                "  ⚠ **%d 组全不成** ⇒ 如实报，不再换写法（事实 53）"
                % len(ev["trials"])
            )
    except Exception as exc:  # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        print("  ⚠ 探针出错: %s" % ev["error"])
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass

    import sw_connect as _sc

    dialogs, _点掉, scanned = _sc.settle_residual_dialogs()
    print(
        "  收尾：扫了 %d 个窗口 · %s"
        % (scanned, "无模态框" if not dialogs else dialogs)
    )
    ev["modal_dialogs"] = dialogs
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
