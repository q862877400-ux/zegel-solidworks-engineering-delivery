r"""@brief 真机核 `MoldDraftAnalysis` 到底在不在 `IFeatureManager` 上（检查器 L197 那条新命中）。

## 为什么（轮 177）
静态检查器报：`sw_mold.py` L197 的 `get_com_member(fm, "MoldDraftAnalysis")` 里
`MoldDraftAnalysis` **不在 `IFeatureManager` 上**（反射里在 `IModelDoc2`）。
★ 这是轮 176 那 6 处之外的**新发现** ⇒ **必须真机核**（静态结论不能直接当真 —— 事实 113/116 的教训）。

## 判据（可证伪）
```
① `IFeatureManager.MoldDraftAnalysis` ⇒ **AttributeError**（若真机也报错 ⇒ 静态命中为真）
② `IModelDoc2.MoldDraftAnalysis`      ⇒ **能取到**（对照：证明它确实在那边）
⇒ ★ 两条合起来才叫"**读错了对象**"，只看①不够（可能是两处都没有）
```

## ⚠ 安全
只在新零件上；`CommandInProgress` 复位；收尾**轮询 + 查到就点掉**；关件不保存。

# ── 来源 ──
# 仓库:   本项目自身（真机核对静态结论）
# 文件:   tools/verify_mold_draft_analysis_owner.py
# 定位:   给 Spec Kit `097` 核对检查器的 L197 新命中。
# 官方依据: 反射 `D:/AI/SW/_raw/reflect_sldworks/iface_sldworks.txt`（`MoldDraftAnalysis
#           ` 出现在哪些段）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "mold-draft-analysis-owner.json"
)
REFLECT = Path(
    Path(__file__).resolve().parents[1]
    / "_raw"
    / "reflect_sldworks"
    / "iface_sldworks.txt"
)


def reflect_owners(member: str) -> list:
    """反射里 `member` 出现在哪些接口段。"""
    out, cur = [], None
    for line in REFLECT.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        m = re.match(r"^##\s+(\S+)", s)
        if m:
            cur = m.group(1)
            continue
        if cur and re.search(r"\b" + re.escape(member) + r"\b", s):
            out.append(cur)
    return sorted(set(out))


def main() -> int:
    ev: dict = {"reflect_owners": reflect_owners("MoldDraftAnalysis")}
    print("  反射里 `MoldDraftAnalysis` 出现在: %s" % ev["reflect_owners"])
    sw = None
    doc = None
    passed = total = 0

    def chk(name, ok, detail=""):
        nonlocal passed, total
        total += 1
        if ok:
            passed += 1
        print("   %s %-56s %s" % ("✓" if ok else "**✗**", name[:56], str(detail)[:60]))

    try:
        import sw_connect

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")
        fm = sw_connect.get_com_member(doc, "FeatureManager")

        #: ① `IFeatureManager.MoldDraftAnalysis` ⇒ 期望 AttributeError
        try:
            v = sw_connect.get_com_member(fm, "MoldDraftAnalysis")
            chk(
                "① IFeatureManager.MoldDraftAnalysis **取到了**",
                False,
                "取到 %s ⇒ 静态命中**是假的**" % type(v).__name__,
            )
            ev["on_feature_manager"] = "取到:%s" % type(v).__name__
        except AttributeError as exc:
            chk(
                "① IFeatureManager.MoldDraftAnalysis ⇒ **AttributeError**（静态命中为真）",
                True,
                str(exc)[:50],
            )
            ev["on_feature_manager"] = "AttributeError"
        except Exception as exc:  # noqa: BLE001
            chk(
                "① IFeatureManager.MoldDraftAnalysis ⇒ 其它异常",
                False,
                "%s:%s" % (type(exc).__name__, str(exc)[:40]),
            )
            ev["on_feature_manager"] = "EXC:%s" % type(exc).__name__

        #: ② 对照：`IModelDoc2` 那边
        try:
            v2 = sw_connect.get_com_member(doc, "MoldDraftAnalysis")
            chk(
                "② IModelDoc2.MoldDraftAnalysis ⇒ **能取到**（它确实在那边）",
                True,
                type(v2).__name__,
            )
            ev["on_model_doc2"] = "取到:%s" % type(v2).__name__
        except Exception as exc:  # noqa: BLE001
            chk(
                "② IModelDoc2.MoldDraftAnalysis ⇒ 能取到",
                False,
                "%s:%s" % (type(exc).__name__, str(exc)[:40]),
            )
            ev["on_model_doc2"] = "EXC:%s" % type(exc).__name__

        #: ③ ★★ 2026-10-01（轮 178）：**改后的 `mold_draft_analysis` 能不能真的调到**
        #: ⚠ 它可能像 `MoldUndercutDetect` 那样**弹模态框**（未定义拔模方向时）
        #: ⇒ 所以要**先看它抛不抛 AttributeError**（那是修复之前的症状）
        try:
            from scripts import sw_mold

            r = sw_mold.mold_draft_analysis(doc, draft_angle_deg=3.0)
            chk(
                "③ ★ 改后 `mold_draft_analysis` 可调用（不再 AttributeError）",
                True,
                "返回 %s" % type(r).__name__,
            )
            ev["after_fix"] = "ok:%s" % type(r).__name__
        except AttributeError as exc:
            chk("③ ★ 改后不再 AttributeError", False, str(exc)[:60])
            ev["after_fix"] = "AttributeError"
        except Exception as exc:  # noqa: BLE001
            #: ⚠ 别的异常（含 com_error）**不等于**"对象错" ⇒ 如实分档
            chk(
                "③ ★ 改后不再 AttributeError（其它异常另计）",
                "AttributeError" not in type(exc).__name__,
                "%s: %s" % (type(exc).__name__, str(exc)[:46]),
            )
            ev["after_fix"] = "EXC:%s" % type(exc).__name__
    except Exception as exc:  # noqa: BLE001
        chk("真机连接", False, "%s: %s" % (type(exc).__name__, str(exc)[:80]))
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:  # noqa: BLE001
            pass

    import sw_connect as _sc

    found, dismissed, scanned = _sc.settle_residual_dialogs(settle_seconds=1.0)
    chk(
        "收尾（轮询 + 查到就点掉）",
        found == 0,
        "发现 %d · 点掉 %d · 扫了 %d" % (found, dismissed, scanned),
    )

    print()
    print(
        "  ── %d/%d · verdict: %s ──"
        % (passed, total, "pass" if passed == total else "fail")
    )
    ev["passed"], ev["total"] = passed, total
    ev["verdict"] = "pass" if passed == total else "fail"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("  证据: %s" % OUT)
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
