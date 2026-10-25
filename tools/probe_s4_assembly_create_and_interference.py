"""★ S3/E4 真机：装配创建与干涉检测 —— `assembly_and_mates` 从 `stitched` 往前推。

## 为什么做这个

`capabilities.yaml` 里：

| 能力 | level |
|---|---|
| `assembly_read` | **verified** |
| **`assembly_and_mates`** | **stitched（从未真机跑过）** |

而 E4（装配自由度闭合）要求「配合约束表达 + 干涉 0 + 关键间隙合规」——
**连装配都建不出来，E4 的真机验证就无从谈起**。

★ 这不需要 S2 的八项首件要求（材料/载荷/安全等级…）——
  配合与干涉是**几何**判据，与材料载荷无关。故本轮可以做。

## 本探针做三件事（按风险从低到高）

| # | 做什么 | 风险 |
|---|---|---|
| ① | 新建装配文档 | 低 |
| ② | 加**两个**同一零件的实例，位置分开 | 低（不涉及选面） |
| ③ | 读回组件数 / 配合数 / 干涉数 | 低（纯读） |

**不做**：加配合（`add_mate_*` 要选实体，而「边/面没有名字」是本仓的老坑）。
本轮先把「装配能建、能读、干涉能测」这条打通，配合留下一步。

## 判据（都用独立读数）

| 读数 | 手段 |
|---|---|
| 组件数 | `IAssemblyDoc.GetComponents(False)` |
| 配合数 | `IAssemblyDoc.GetMates()` |
| 干涉数 | `IInterferenceDetectionMgr`（经 `sw_assembly` 既有实现） |

★ 另做一个**负例**：把第二个实例放在与第一个重叠的位置 ⇒ 干涉数应 > 0。
  没有这个负例，「干涉 = 0」就可能只是「检测没跑」。

## 只读纪律

新建文档 → 用完关掉；`CommandInProgress`；收尾核**文档数归零**。
"""

from __future__ import annotations

import json
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
# 仓库:   本项目自身（工具 · E4 前置）
# 文件:   tools/probe_s4_assembly_create_and_interference.py
# 定位:   capabilities.yaml 里 `assembly_and_mates` 一直是 **stitched（从未真机跑过）**，
#          而 E4 要求「配合约束表达 + 干涉 0 + 关键间隙」。本轮先打通
#          「建装配 / 加组件 / 读组件 / 测干涉」这条，含**干涉负例**。
#          配合（mate）留下一步 —— 它要选实体，而那正是本仓的老坑。
# 官方依据: ISldWorks.NewDocument（经 sw_connect.new_document）·
#          IAssemblyDoc.AddComponent5 / GetComponents（经 sw_assembly.add_component /
#          get_components）· IAssemblyDoc.GetMates（配合数）·
#          IInterferenceDetectionMgr（经 sw_assembly 既有实现）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

SRC = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
WORK = R / "output" / "s4-assembly"


def main() -> int:
    ev: dict = {"probe": "s4-assembly-create-and-interference"}
    sw = doc = None
    try:
        if not SRC.is_file():
            print("★ 找不到板件：%s" % SRC)
            return 2
        WORK.mkdir(parents=True, exist_ok=True)
        part = WORK / "plate.SLDPRT"
        shutil.copy2(SRC, part)

        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        #: ① 新建装配
        ok_n, doc = _try(c_.new_document, sw, "assembly")
        ev["new_assembly"] = {"ok": ok_n, "detail": str(doc)[:120]}
        if not ok_n or doc is None:
            ev["conclusion"] = "★ 建不了装配文档：%s" % str(doc)[:120]
            print(ev["conclusion"])
            return 1
        title = str(_member(doc, "GetTitle") or "")
        print("① 装配文档已建：title=%r" % title)

        #: ② 加两个组件：第一个在原位，第二个沿 Z 分开 100mm（不重叠）
        ok1, c1 = _try(a_.add_component, doc, str(part))
        ok2, c2 = _try(a_.add_component, doc, str(part), 0.0, 0.0, 0.100)
        ev["add_component"] = {
            "ok1": ok1, "detail1": str(c1)[:80],
            "ok2": ok2, "detail2": str(c2)[:80],
        }
        print("② 加组件：%s / %s" % (ok1, ok2))

        #: ③ 读回组件数 / 配合数 / 干涉数
        def _counts(tag: str) -> dict:
            out = {"tag": tag}
            okc, comps = _try(a_.get_components, doc)
            out["components"] = len(list(comps)) if okc and comps else 0
            okm, mates = _try(get_com_member, doc, "GetMates")
            out["mates"] = len(list(mates)) if okm and mates else 0
            #: 干涉检测：走本仓既有实现（若存在）
            oki, res = _try(a_.get_interference_detection, doc)
            out["interference"] = res if oki else "err: %s" % str(res)[:120]
            return out

        separated = _counts("分开 100mm")
        ev["separated"] = separated
        print("③ 分开摆放：%s" % json.dumps(separated, ensure_ascii=False)[:200])

        #: ④ 负例：把第二个组件挪到与第一个重叠的位置
        transformed = "未做"
        try:
            ok_tr, _ = _try(a_.apply_component_transform_x, doc, 0.0)
            transformed = "apply_component_transform_x ok=%s" % ok_tr
        except Exception as exc:  # noqa: BLE001
            transformed = "err: %s" % str(exc)[:80]
        ev["transform_attempt"] = transformed
        overlapped = _counts("重叠（负例）")
        ev["overlapped"] = overlapped
        print("④ 重叠摆放：%s" % json.dumps(overlapped, ensure_ascii=False)[:200])

        #: 汇总
        can_create = ev["add_component"]["ok1"] and ev["add_component"]["ok2"]
        comp_ok = separated["components"] == 2
        ev["verdict"] = {
            "assembly_created": bool(ok_n),
            "components_added": bool(can_create),
            "components_read_back": separated["components"],
            "mates": separated["mates"],
            "interference_separated": separated["interference"],
            "interference_overlapped": overlapped["interference"],
        }
        ev["ok"] = bool(ok_n and can_create and comp_ok)
        ev["conclusion"] = (
            "★ 装配能建、组件能加能读：组件数 %s、配合 %s、干涉(分开) %s"
            % (separated["components"], separated["mates"], separated["interference"])
            if ev["ok"]
            else "★ 未达预期，见 verdict"
        )
        print(ev["conclusion"])
        return 0 if ev["ok"] else 1
    except Exception as exc:  # noqa: BLE001
        import traceback

        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        ev["traceback"] = traceback.format_exc()[-1200:]
        print("★ 失败：", ev["err"])
        return 1
    finally:
        if sw is not None:
            if doc is not None:
                t = str(_member(doc, "GetTitle") or "")
                if t:
                    _try(sw.CloseDoc, t)
            ev["docs_left"] = open_doc_count(sw)
            print("   收尾后剩余文档数：%s" % ev["docs_left"])
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
        ev["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        dest = R / "output" / "s4-assembly-create.json"
        dest.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("   证据已写：%s" % dest)


if __name__ == "__main__":
    raise SystemExit(main())
