"""摆好「人工做一个配合」的现场：装配里放两块板（第二块抬高 50mm），**保持打开**。

## 为什么要摆这个

配合那条已排除 12 个 API 候选、第 13 个（`PickPoints`）写不进去。
用户同意**人工做一次配合**，我在旁边截图 + 读特征树 —— 这能直接看出
SolidWorks 期待什么（哪类实体、什么选择标记、要不要配合参考）。

## 现场长什么样

```
装配：两块板（板1_rev-1.SLDPRT）
  组件1 放在 (0, 0, 0)      → 占 z 0..20mm，顶面 z=20mm
  组件2 放在 (30, 0, 50)    → 占 z 50..70mm，底面 z=50mm
```

⇒ 两块板**不接触**，要建一个重合配合把组件2 拉下来贴住组件1。
  这样人工做的配合有明确意图，也便于事后读它的特征属性。

## 收尾

★ **不关文档、不关 SolidWorks** —— 现场要留给用户点。
  所以运行时必须带 `sw_guard --skip-doc-cleanup`（否则护栏跑完会替我关掉）。
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
# 仓库:   本项目自身（工具 · 人工配合现场）
# 文件:   tools/setup_mate_demo.py
# 定位:   摆好两块板的装配并**保持打开**，供用户人工做一次重合配合；
#          之后由 `tools/observe_mate_demo.py` 读它建出来的特征，反推 API 该给什么。
# 官方依据: IAssemblyDoc::AddComponent5（文件必须已在内存）· IAssemblyDoc::GetComponents ·
#          ISldWorks::ActivateDoc3 · IModelDoc2::Save3（经 `save_document`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

PART = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
ASM_OUT = R / "output" / "coop" / "mate_demo.SLDASM"
DEST = R / "output" / "mate-demo-setup.json"

import sw_assembly as asm_  # noqa: E402
import sw_connect as c_  # noqa: E402
from sw_connect import get_com_member  # noqa: E402


def main() -> int:
    ev: dict = {"probe": "setup-mate-demo"}
    conn = c_.connect_solidworks(wait_seconds=30)
    sw = conn[0] if isinstance(conn, tuple) else conn
    try:
        sw.Visible = True
    except Exception:  # noqa: BLE001
        pass
    try:
        sw.CommandInProgress = False
    except Exception:  # noqa: BLE001
        pass

    try:
        ok_p, _part = c_.try_call(c_.open_document, sw, str(PART))
        ev["open_part"] = bool(ok_p)
        ok_n, asm_doc = c_.try_call(c_.new_document, sw, "assembly")
        ev["new_assembly"] = bool(ok_n)
        if asm_doc is not None:
            try:
                sw.ActivateDoc3(str(get_com_member(asm_doc, "GetTitle") or ""), 0, False)
            except Exception:  # noqa: BLE001
                pass

        #: 组件1 在原点；组件2 抬高 50mm、右移 30mm ⇒ 两块不接触，配合才有事可做。
        #: ★★★ 2026-10-26（第 60 轮，用户看截图指出「两个零件距离太远」）：
        #:   dd_component 的 x/y/z 单位是**米**（仓库 docstring 逐字：x, y, z: 放置位置（米））。
        #:   我一路传的是**毫米数** ⇒ 组件2 跑到 50 **米**外、缩放全图后零件小成一个点
        #:   ⇒ 更严重的是：射线选中的两个面**其实都落在组件1 上**，
        #:     「两个组件之间的配合」这个前提**从来没成立**。这里改成米。
        for (dx, dz) in ((0.0, 0.0), (0.030, 0.050)):
            c_.try_call(
                asm_.add_component, asm_doc, str(PART), dx, 0.0, dz, "", sw
            )
        try:
            n = len(list(get_com_member(asm_doc, "GetComponents", False) or ()))
        except Exception:  # noqa: BLE001
            n = -1
        ev["components"] = n

        ASM_OUT.parent.mkdir(parents=True, exist_ok=True)
        ok_s, _ = c_.try_call(c_.save_document, asm_doc, str(ASM_OUT))
        ev["saved"] = bool(ok_s)
        ev["saved_path"] = str(get_com_member(asm_doc, "GetPathName") or "")

        ev["ok"] = bool(n >= 2)
        print("① 装配：组件 %s 个 · 保存 %s" % (n, ev["saved"]))
        print("② 现场路径：%s" % ev["saved_path"])
        print("★ 文档**保持打开**（不关），等用户人工做一次配合")
        return 0 if ev["ok"] else 1
    finally:
        DEST.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("   证据已写：%s" % DEST)


if __name__ == "__main__":
    raise SystemExit(main())
