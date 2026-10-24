"""★ S3 真机负例：导入死实体能不能被 E3 判出来。

## 为什么要有这条

E3 的负例第一条逐字是「**导入死实体冒充原生特征**」
（`docs/ENGINEERING-PATH.md` 第四节）。

第 15 轮验的是**正面**（原生 15 个特征、零错误、前序可改且下游跟随）。
判定器侧也有离线测试（`native_features=0, imported_solids=1 ⇒ fail`）。

**但「离线测试说它会拒」与「真机能造出那种情形且它真拒了」是两件事。**
本轮把后者补上：

```
交付件副本 ──导出──> STEP ──作为新文档导入──> 导入体零件
                                              ↓
                                     量 GetTypeName2（不猜）
                                              ↓
                              collect_feature_tree + judge_feature_tree
                                              ↓
                                      期望：FAIL（导入死实体冒充原生）
```

## ★ 关键：导入体的类型名要**量出来**

第 15 轮已证明「凭印象写类型名会判错」—— 本机给「切除-拉伸」的类型名是 `ICE`。
同理，导入体的类型名也必须实测，不能预设成 `"Import"`。

⇒ 本探针把导入体的每个特征的 `GetTypeName2` 原样打出来。

## 只读纪律

- 只操作副本与新建的 STEP 文件（都在 `output/` 下）
- `CommandInProgress`（铁律 2）
- 收尾只关**自己开的**文档
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

from scripts import sw_connect as c_  # noqa: E402
from scripts.engineering.acceptance.e3_feature_types import tally as _tally  # noqa: E402
from scripts.sw_connect import get_com_member  # noqa: E402
from scripts.sw_connect import try_call as _try  # noqa: E402
from scripts.sw_export import export_step_report  # noqa: E402
from scripts.sw_feature_readback import feature_info, feature_names, whats_wrong  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_s3_e3_imported_solid_negative.py
# 定位:   specs/350-first-part-delivery T012 / E3 —— 真机造出「导入死实体冒充原生特征」
#           这个负例，验判定器在真数据上真的拒。第 15 轮只验了正面 + 离线负例。
# 官方依据: IModelDocExtension.SaveAs3 / ISldWorks.LoadFile4（经 sw_export.export_step_report
#           与 sw_connect.open_document）· IFeature.GetTypeName2（导入体类型名**实测**）
#           IModelDocExtension.GetWhatsWrongCount（经 sw_feature_readback.whats_wrong）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

SRC = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
WORK = R / "output" / "e3-negative"


def _tree(doc) -> list:
    rows = []
    for nm in feature_names(doc) or []:
        info = feature_info(doc, nm) or {}
        rows.append(
            {
                "name": nm,
                "type": info.get("GetTypeName2"),
                "faces": info.get("GetFaceCount"),
                "parents": info.get("GetParents"),
                "children": info.get("GetChildren"),
            }
        )
    return rows


def main() -> int:
    ev: dict = {"probe": "s3-e3-imported-solid-negative"}
    sw = doc = None
    try:
        if not SRC.is_file():
            print("★ 找不到交付件：%s" % SRC)
            return 2
        WORK.mkdir(parents=True, exist_ok=True)
        copy = WORK / "板1_rev-1_src.SLDPRT"
        shutil.copy2(SRC, copy)
        step_path = WORK / "板1_rev-1.step"

        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        #: ① 打开副本并导出 STEP
        ok_o, doc = _try(c_.open_document, sw, str(copy))
        if not ok_o or doc is None:
            print("★ 打不开交付件副本：%s" % str(doc)[:120])
            return 2
        ok_e, rep = _try(export_step_report, doc, str(step_path))
        ev["export"] = {"ok": ok_e, "report": str(rep)[:300]}
        print("① 导出 STEP：ok=%s" % ok_e)
        if not ok_e or not step_path.is_file():
            ev["conclusion"] = "★ STEP 没导出成功 ⇒ 负例造不出来"
            print(ev["conclusion"])
            return 1
        ev["step_size"] = step_path.stat().st_size
        print("   STEP 大小 %d 字节" % ev["step_size"])

        #: 关掉源文档（只关自己开的）
        ok_t, title = _try(get_com_member, doc, "GetTitle")
        if ok_t and title:
            _try(sw.CloseDoc, title)
        doc = None

        #: ② 把 STEP 作为**新文档**导入
        ok_i, doc = _try(c_.open_document, sw, str(step_path))
        ev["import"] = {"ok": ok_i, "detail": str(doc)[:160]}
        if not ok_i or doc is None:
            ev["conclusion"] = "★ STEP 导入失败：%s" % str(doc)[:160]
            print(ev["conclusion"])
            return 1
        print("② STEP 已导入为新文档")

        #: ③ 量导入体的特征树（类型名要**实测**）
        tree = _tree(doc)
        ev["imported_tree"] = tree
        ev["imported_types"] = sorted({r.get("type") for r in tree if r.get("type")})
        ww = whats_wrong(doc)
        ev["whats_wrong"] = ww
        print("③ 导入体特征 %d 个 · 类型词表 %s" % (len(tree), ev["imported_types"]))
        for r in tree:
            print("   %-18s type=%-18s faces=%s" % (
                str(r["name"])[:18], str(r["type"])[:18], r["faces"],
            ))
        print("   错误/警告：%s" % json.dumps(ww, ensure_ascii=False)[:120])

        #: 判定：按**实测词表**分类（`e3_feature_types`，单一真源）
        #: ★ 基准面/原点/Tables 归 `infra` —— 导入体**也带**这些，
        #:   若算成原生，「导入死实体」就会被判 pass（那正是 E3 要拒的伪造手法）。
        counts = _tally(tree)
        native_n = counts["native"]
        imported_n = counts["import"]
        ev["counts"] = {
            "feature_count": len(tree),
            "native_features": native_n,
            "imported_solids": imported_n,
            "infra": counts["infra"],
            "unknown": counts["unknown"],
            "unknown_types": counts["unknown_types"],
        }
        print("   分类：%s" % counts)
        if counts["unknown"]:
            print("   ⚠ 有未收录的类型名：%s ⇒ 判据有盲区，需实测后补词表"
                  % counts["unknown_types"])

        #: ④ 喂判定器
        from engineering.acceptance.e2_e3_solid import (  # noqa: E402
            collect_feature_tree,
            judge_feature_tree,
        )

        obs = collect_feature_tree(
            target="导入 STEP 的零件（E3 负例）",
            feature_count=len(tree),
            native_features=native_n,
            imported_solids=imported_n,
            dangling_refs=0,
            errors=int(ww.get("count") or 0),
            warnings=0,
            editable_prefix_verified=False,
            version="2026-10-25",
        )
        res = judge_feature_tree(obs, requirement_id="R-E3")
        ev["judge"] = {"status": res.status.value, "reason": res.reason}
        print("④ 判定器：%s（%s）" % (res.status.value, res.reason[:80]))

        ok = res.status.value == "fail"
        ev["ok"] = ok
        ev["conclusion"] = (
            "★ 负例成立：导入死实体被判 fail（原生 %d / 非原生 %d，类型 %s）"
            % (native_n, imported_n, ev["imported_types"])
            if ok
            else "★ 判定器没拒导入体 ⇒ E3 有洞（见 judge）"
        )
        print(ev["conclusion"])
        return 0 if ok else 1
    except Exception as exc:  # noqa: BLE001
        import traceback

        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        ev["traceback"] = traceback.format_exc()[-1200:]
        print("★ 失败：", ev["err"])
        return 1
    finally:
        if sw is not None and doc is not None:
            try:
                sw.CloseDoc(doc.GetTitle())
            except Exception:  # noqa: BLE001
                pass
        if sw is not None:
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
        ev["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        dest = R / "output" / "s3-e3-imported-solid-negative.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("证据已写：%s" % dest)


if __name__ == "__main__":
    raise SystemExit(main())
