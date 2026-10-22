"""★ 真机试：`FeatureLinearPattern4`（20 参）在前置成立时能不能建成线性阵列。

★★ 官方依据（三源里的 `C:\\swapi`）：
  · `types/IFeatureManager/FeatureLinearPattern3.md`（10 参）⇒ 逐字
    「Obsolete. Superseded by [[IFeatureManager::FeatureLinearPattern4]].」
  · `types/IFeatureManager/FeatureLinearPattern4.md`（**20 参**）`## Parameters` 逐字：
    ```
    Num1, Spacing1, Num2, Spacing2          ← 与旧同名
    FlipDir1, FlipDir2                      ← 与旧同名
    ★★ DName1, DName2   ← 官方逐字「**Name of the dimension defining Direction 1**」
                          ⇒ ★★★ **那是**尺寸名**，不是方向向量字符串！**
    GeometryPattern
    ★ VaryInstance      ← 第 10 个（**新**）
    HasOffset1/2 · CtrlByNum1/2 · FromCentroid1/2 · RevOffset1/2 · Offset1/2   ← 后 10 个（**新**）
    ```
  ⇒ ★★★★ **与旧入口的**关键差异**：★ 旧的第 7/8 参是**方向向量字符串**（★ 我们传 `"1 0 0"`），
    ★★ 新的第 7/8 参是**尺寸名** ⇒ ★ **语义**换了一个东西**** ✓

★★★ 前置（★ 上一版已验证成立）：★ **选中一个要阵列的特征** ⇒ 回读选中数 = **1** ✓
  ★★ 而**新入口**还需要一件我们没有的东西：★ **一个定义方向的**尺寸名**
    （★ 旧的用向量字符串绕开了它）⇒ ★★★ 所以本探针**同时试两种**：
    ★ `DName=""`（★ 空）· ★ `DName=<那个件上真实存在的尺寸名>`

★★★ 判据（★ 跑之前写死）：★ **特征树出现新特征**才算"建成"（★ 事实 40 那一族）✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。
# 文件:   tools/probe_linearpattern4.py
# 定位:   ★ 阶段 2：`scripts/sw_part.py::linear_pattern` 的 `FeatureLinearPattern3`。
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts import sw_connect as C                                       # noqa: E402
from scripts import sw_part as P                                          # noqa: E402

OUT = REPO / "output" / "linearpattern4-evidence.json"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def _try(fn, *a):
    try:
        return {"ok": True, "ret": repr(fn(*a))[:90]}
    except Exception as exc:                                              # noqa: BLE001
        return {"ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:180])}


def _names(doc) -> list:
    try:
        return [str(x) for x in (P.feature_names(doc) or [])]
    except Exception:                                                     # noqa: BLE001
        return []


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "试法": []}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    #: ★ 新入口要"定义方向的尺寸名" ⇒ ★ 用**带尺寸的现成件**（★ 上一轮验证过它带 `D1@凸
    #: 台-拉伸1`）
    EXIST = REPO / "output" / "_probe_drawing_part.SLDPRT"
    R["带尺寸的件存在"] = EXIST.exists()
    doc = None
    try:
        if not EXIST.exists():
            R["skip"] = "★ 没有带尺寸的件"
            raise SystemExit(0)
        doc = C.open_document(sw, str(EXIST), read_only=False, silent=True)
        R["打开"] = repr(doc)[:60] if doc is not None else "None"
        if doc is None:
            raise SystemExit(0)
        names = _names(doc)
        R["特征"] = names[:12]
        #: ★ 前置：★ 选一个要阵列的特征（★ 上一版验证过这条路成立）
        target = None
        for n in names:
            if "拉伸" in n or "凸台" in n or "Extrude" in n:
                target = n
                break
        R["被阵列特征"] = target
        if target:
            try:
                _g(_g(doc, "Extension"), "SelectByID2", target, "BODYFEATURE",
                   0, 0, 0, False, 0, None, 0)
            except Exception:                                             # noqa: BLE001
                pass
        try:
            R["回读选中数"] = int(_g(_g(doc, "SelectionManager"),
                                    "GetSelectedObjectCount2", -1) or 0)
        except Exception:                                                 # noqa: BLE001
            R["回读选中数"] = -1
        fm = _g(doc, "FeatureManager")

        #: ★★ 两种 `DName`：★ 空 · ★ 那个件上真实的尺寸名
        for dname in ("", "D1@凸台-拉伸1@_probe_drawing_part.Part"):
            n0 = len(_names(doc))
            case = {"DName": dname or "（空）"}
            case["调"] = _try(_g, fm, "FeatureLinearPattern4",
                              2, 0.03, 1, 0.0,
                              False, False,
                              dname, dname,
                              False, False,
                              False, False, False, False,
                              False, False, False, False,
                              0.0, 0.0)
            n1 = len(_names(doc))
            case["后特征数"] = n1
            case["建成"] = "★ 是（+%d）" % (n1 - n0) if n1 > n0 else "★★ 否"
            R["试法"].append(case)
            #: ★ 每次试完清选择（★ 免得第二次的前置被污染）
            try:
                _g(doc, "ClearSelection2", True)
                if target:
                    _g(_g(doc, "Extension"), "SelectByID2", target, "BODYFEATURE",
                       0, 0, 0, False, 0, None, 0)
            except Exception:                                             # noqa: BLE001
                pass
    except SystemExit:
        pass
    except Exception as exc:                                              # noqa: BLE001
        R["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:                                                 # noqa: BLE001
            pass
    ok = [c for c in R["试法"] if str(c.get("建成", "")).startswith("★ 是")]
    R["★★_结论"] = ("★ 有建成的一种 ⇒ 新入口可用" if ok
                    else "★★ 两种都没建成 ⇒ **如实记「前置未打通」**（不硬换）")
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
