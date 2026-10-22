"""★ 真机普查：`IModelDocExtension` 的 396 个成员，**哪些这个对象真的能用**。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_member_availability.py
# 定位:   ★ 2026-10-03（轮 447）承**事实 361** 那条判据（★ "能不能用，看 `getattr`"）。
#   ★★★ **为什么要普查**：★ 事实 361 发现 `IModelDocExtension` 上
#     ★ **`CreateStructureSystemMemberData` 能用、而 `CreateStructureSystem` 取不到** ——
#     ★★ **同一接口、相邻两个名字、结果相反** ⚠
#     ⇒ ★ 故要问的不是"这个接口行不行"，★ 而是"**这个接口上**哪些成员行**" ✓
#   ★★ 判据（★ 三态，★ 与 `tools/com_member_probe.py` 同一口径）：
#     ```
#     ★ `getattr(obj, 名, None)` 回 None ⇒ **取不到**（★ 而它**不**等于"接口里没有"）
#     ★ 可调 ⇒ 方法 · ★ 其它 ⇒ 属性
#     ```
#   ⚠ **只 `getattr`、不调用**（★ "取或调"的坑见事实 227）。
# 官方依据: 出厂程序集 `SolidWorks.Interop.sldworks.dll` 的 `IModelDocExtension`（★ 396 
#           个成员）·
#   pywin32 迟到绑定只认 `DispInterface`（★ `IDispatch::GetIDsOfNames`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 报**三组**（★ 能用 / 取不到 / 按类分）—— ★ 而**先报查了多少**（★ 事实 357 那
# 条纪律）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "member-availability-evidence.json")


def main() -> int:
    import sw_connect
    from com_member_probe import interface_members, probe_members
    from sw_connect import get_com_member, safe_get_com_member

    ev: dict = {"at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        ext = get_com_member(doc, "Extension")
        names = sorted(interface_members("IModelDocExtension"))
        ev["probed"] = len(names)                                   # ★ 先报查了多少
        got = probe_members(ext, names)
        usable = sorted(n for n, v in got.items() if v != "missing")
        missing = sorted(n for n, v in got.items() if v == "missing")
        #: ★ 按**名字形态**分类（★ 因为 `get_X`/`set_X` 是属性访问器、★ 迟到绑定下叫 `X`
        #: ）
        def bucket(n: str) -> str:
            if n.startswith("get_") or n.startswith("set_"):
                return "property_accessor"
            if n.startswith("I") and n[1:2].isupper() and "_" not in n[:2]:
                return "i_prefixed"
            return "plain"
        from collections import Counter
        ev["counts"] = {"probed": len(names), "usable": len(usable), "missing": len(missing)}
        ev["by_bucket_missing"] = dict(Counter(bucket(n) for n in missing))
        ev["by_bucket_usable"] = dict(Counter(bucket(n) for n in usable))
        #: ★★ **本阶段关心的那两条**（★ 同接口、相邻、结果相反）
        for k in ("CreateStructureSystem", "CreateStructureSystemMemberData", "SelectByID2"):
            ev["spot_%s" % k] = got.get(k, "?")
        ev["usable_sample"] = usable[:20]
        ev["missing_sample"] = missing[:20]
        ev["verdict"] = "pass" if (ev["counts"]["usable"] > 0 and ev["counts"]["missing"] > 0) else "partial"
        ev["note"] = ("★ 普查 `IModelDocExtension` 的成员在**这个真机对象**上能不能取到。"
                      "★ 判据三态：可调 / 属性 / 取不到。★ 而 `get_*` / `set_*` 是属性访问器 —— "
                      "★ 迟到绑定下它们叫 `X`，故正常会落进 `missing`。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1, default=str)[:1500])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        if doc is not None:
            try:
                t = str(safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
            except Exception:                                  # noqa: BLE001
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
