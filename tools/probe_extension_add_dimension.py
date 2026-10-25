"""★ 试一条**没试过**的建尺寸路径：`IModelDocExtension.AddDimension`。

## 为什么试它（不是"再试一次"）

事实 560 记录：`IModelDoc2.AddDimension2` / `AddHorizontalDimension2` 在本机
**连对照组都崩**（`RPC 服务器不可用` = 进程死了），前后共 4 次。
⇒ 那两个成员**不能再去撞**。

但把官方源里所有建尺寸的成员枚举一遍（口径：`C:\\swapi\\types\\*\\*Dimension*.md`
且名字含 Add/Insert/Create），发现**没试过的另一条实现路径**：

| 成员 | 所属接口 | 试过吗 |
|---|---|---|
| `AddDimension2` / `AddHorizontalDimension2` / `AddVerticalDimension2` | `IModelDoc2` | ✅ 试过，**崩** |
| **`AddDimension`** | **`IModelDocExtension`** | ❌ **没试过** |
| `AddSpecificDimension` / `AddSymmetricDimension` | `IModelDocExtension` | ❌ 没试过 |
| `AddAlongX/Y/ZDimension` | `ISketchManager` | ❌ 但 Remarks 说**只适用 3D 草图** ⇒ 不适用 |

## 官方依据（逐字）

`C:\\swapi\\types\\IModelDocExtension\\AddDimension.md`
- 签名：`System.object AddDimension( System.double X, System.double Y, System.double Z, System.int Direction )`
- Remarks：「Before calling this method, you must select the entities for which to add a display dimension」
- Remarks：「The X, Y, and Z coordinates of the display dimension text must be appropriate for the
  specified Direction, or this method **fails to add** the display dimension」
  ★ 这一句很关键：**它会失败返回，而不是崩** —— 与那两个崩掉的方法行为不同。

`C:\\swapi\\enums\\swSmartDimensionDirection_e.md`
- `swSmartDimensionDirection_Right = 0` · `Up = 1` · `Left = 2` · `Down = 3`

官方例子 `C:\\swapi\\examples\\Create_Angular_Dimension_Example_CSharp.md` 的实际调用：
```
myDisplayDim = (DisplayDimension)Part.Extension.AddDimension(
    -0.0456250220540824, 0, 0.00150965590938767, (int)swSmartDimensionDirection_Right);
```
★ 它的前置也是「先选中实体」。

## 实验设计（**只改方法这一个变量**）

设置与事实 560 那个崩掉的探针**完全一致**：
草图画一条水平线段 → 选中该线段 → 建水平方向尺寸。
唯一的差别是这次调 `Extension.AddDimension` 而不是 `AddDimension2`。

⇒ 若成：说明尺寸能力**没退化**，退化的是 `IModelDoc2` 那两个入口 ⇒ E2 联动有救。
⇒ 若也崩：**不再试第三个入口**，坐实「本机尺寸能力整体退化」。

## 证据先落盘再冒险

`sv`（safeguard）在执行**会崩的那一句之前**就把 `pre` 写进 JSON ——
第 43 轮实测过：进程被杀时 `finally` 不执行，一份证据都留不下。
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
# 仓库:   本项目自身（工具 · 建尺寸入口探针）
# 文件:   tools/probe_extension_add_dimension.py
# 定位:   试 `IModelDocExtension.AddDimension`（未经试过的另一条实现路径）。
#          事实 560：`IModelDoc2.AddDimension2` / `AddHorizontalDimension2` 本机连对照组都崩，
#          前后 4 次 ⇒ 那两个不能再撞；本探针只换**方法入口**，设置与那次完全一致。
# 官方依据: C:\swapi\types\IModelDocExtension\AddDimension.md（4 参 + 两条 Remarks）·
#          enums\swSmartDimensionDirection_e.md（Right=0/Up=1/Left=2/Down=3）·
#          examples\Create_Angular_Dimension_Example_CSharp.md（实际调用形态）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

SRC = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
DEST = R / "output" / "extension-add-dimension.json"
SW_DIR_RIGHT = 0

import sw_connect as c_  # noqa: E402
from probe_hv_dimension_with_selection import (  # noqa: E402
    _dim_count,
    _mk_sketch_with_line,
    _segments_and_points,
)


def _save(ev: dict) -> None:
    DEST.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    ev: dict = {"probe": "extension-add-dimension"}
    sw = doc = None
    try:
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        import shutil

        work = R / "output" / "extdim"
        work.mkdir(parents=True, exist_ok=True)
        copy = work / "板1_extdim.SLDPRT"
        if SRC.is_file():
            shutil.copy2(SRC, copy)
            ok_o, doc = c_.try_call(c_.open_document, sw, str(copy))
        else:
            #: ★ 交付件不在就直接退出 —— 不自己造一个零件（那会引入第二个变量）
            ev["err"] = "交付件不存在：%s" % SRC
            print("★ " + ev["err"])
            return 2
        ev["open"] = {"ok": bool(ok_o), "doc": bool(doc)}

        #: ① 与前一个崩掉的探针**完全相同的设置**
        _mk_sketch_with_line(doc)  #: 只为了把草图画出来并保持编辑态，返回值不用
        before = _dim_count(doc)
        ev["before"] = before

        #: ② 选中那条线段（按对象选 —— 草图段没有名字，事实 32）
        #: ★ GetSketchSegments 在 **ISketch** 上，不在 ISketchManager 上
        #:   （第一版写错，实测 AttributeError: <unknown>.GetSketchSegments）
        #:   ⇒ 复用既有探针的 _segments_and_points
        segs, _pts = _segments_and_points(doc)
        #: ★ 定位「为什么选不中」：草稿是否为 None · 段数 · 点数
        try:
            sk_now = c_.get_com_member(doc, "GetActiveSketch2")
        except Exception:  # noqa: BLE001
            sk_now = None
        ev["sketch"] = {
            "active_is_none": sk_now is None,
            "segments": len(segs),
            "points": len(_pts),
        }
        print("   草图：active_is_none=%s · 段 %d · 点 %d"
              % (sk_now is None, len(segs), len(_pts)))

        #: ★★★ 三条选法都试，各自报告 —— 只信读数，不信"应该能选"
        picked = 0
        how = ""
        seg = segs[0] if segs else None
        if seg is not None:
            doc.ClearSelection2(True)
            for name, fn in (
                ("Select4", lambda s: s.Select4(False, None)),
                ("Select2", lambda s: s.Select2(False, 0)),
                ("Select", lambda s: s.Select(False)),
            ):
                try:
                    r = fn(seg)
                except Exception as exc:  # noqa: BLE001
                    ev["select_" + name] = {"err": "%s" % (type(exc).__name__,)}
                    continue
                try:
                    n = int(
                        c_.get_com_member(
                            c_.get_com_member(doc, "SelectionManager"),
                            "GetSelectedObjectCount2", -1,
                        ) or 0
                    )
                except Exception:  # noqa: BLE001
                    n = -1
                ev["select_" + name] = {"ret": bool(r), "selected": n}
                print("   %-8s ret=%s · 选中 %s" % (name, bool(r), n))
                if n >= 1:
                    picked, how = n, name
                    break
                doc.ClearSelection2(True)
        ev["selected"] = picked
        ev["select_method"] = how
        ev["selected"] = picked

        #: ③ ★★★ 冒险那一句之前**先落盘**
        ev["about_to_call"] = "IModelDocExtension.AddDimension"
        _save(ev)
        print("① 设置就绪：尺寸 %s 个 · 选中 %d 个 · 即将调 Extension.AddDimension"
              % (before, picked))

        if picked < 1:
            ev["ok"] = False
            ev["conclusion"] = (
                "★ 停在「没选到实体」这一步：**设置无效** ⇒ 不调 AddDimension"
                "（那样得到的「建不出尺寸」不算结论）"
            )
            print(ev["conclusion"])
            return 1

        #: ★★ 第 53 轮：`SetAddToDB(True)` —— 官方 Remarks 说它「绕过交互、直接进数据库」。
        #:   假设：尺寸创建因此不再弹「修改」框（那样就不必每个尺寸都外部 ESC）。
        addtodb = "--addtodb" in sys.argv
        if addtodb:
            try:
                c_.get_com_member(doc, "SetAddToDB", True)
                ev["addtodb"] = True
                print("   SetAddToDB(True) 已设")
            except Exception as exc:  # noqa: BLE001
                ev["addtodb_err"] = "%s" % (type(exc).__name__,)
                print("   ★ SetAddToDB 失败：%s" % ev["addtodb_err"])

        ext = c_.get_com_member(doc, "Extension")
        ok_d, dim = c_.try_call(
            c_.get_com_member, ext, "AddDimension",
            -0.02, 0.0, 0.005, SW_DIR_RIGHT,
        )
        if addtodb:
            try:
                #: ★ 官方逐字：「you must set it back to false to restore SOLIDWORKS to its normal operating mode」
                c_.get_com_member(doc, "SetAddToDB", False)
                ev["addtodb_restored"] = True
            except Exception:  # noqa: BLE001
                pass

        after = _dim_count(doc)
        ev["call"] = {"ok": bool(ok_d), "dim_none": dim is None}
        ev["after"] = after
        print("② 返回 ok=%s dim=%s · 尺寸 %s → %s" % (ok_d, dim is None, before, after))

        ev["ok"] = bool(after > before)
        ev["conclusion"] = (
            "★ `Extension.AddDimension` **可用**（尺寸 %s → %s）⇒ 退化的只是 IModelDoc2 那两个入口"
            % (before, after)
            if ev["ok"]
            else "★ `Extension.AddDimension` 也没建成（%s → %s），但**进程没崩** ⇒ "
            "与那两个崩掉的入口行为不同" % (before, after)
        )
        print(ev["conclusion"])
        return 0 if ev["ok"] else 1
    except Exception as exc:  # noqa: BLE001
        import traceback

        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        ev["traceback"] = traceback.format_exc()[-900:]
        print("★ 异常：", ev["err"])
        return 1
    finally:
        if doc is not None:
            try:
                c_.get_com_member(doc, "SketchManager").InsertSketch(True)
            except Exception:  # noqa: BLE001
                pass
            try:
                ttl = str(c_.get_com_member(doc, "GetTitle") or "")
                if ttl:
                    sw.CloseDoc(ttl)
            except Exception:  # noqa: BLE001
                pass
        if sw is not None:
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
            try:
                ev["docs_left"] = c_.open_doc_count(sw)
            except Exception:  # noqa: BLE001
                pass
        _save(ev)
        print("   证据已写：%s" % DEST)


if __name__ == "__main__":
    raise SystemExit(main())
