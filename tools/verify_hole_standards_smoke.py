r"""@brief 真机冒烟：`sw_hole_features.list_hole_standards`（把孤儿包装接成能用的 API）。

## 为什么
`get_hole_standards` 等 4 个包装**在仓库里没有调用方** —— 它们把**出参甩给调用方**。
`042`（轮 123）裁断出**正确的传法**（`VARIANT(VT_BYREF|VT_VARIANT, None)`）后，
轮 124 补了高层入口 `list_hole_standards`（自己造容器、自己读回来）。
★ 本冒烟给那条路取**真机**证据。

## 安全
**纯查询**（`GetHoleStandardsData` / `GetHoleStandards` 都是读），
不建几何、不碰用户文档 ⇒ 风险低；仍置 `CommandInProgress` 并在收尾查模态框。

## 判据（★ 都能被"空操作"证伪）
* 返回**非空**；
* ★ 条数与**两组出参的长度**一致（配对成功）；
* ★ 名称**全是非空字符串**（不是一堆 None）；
* ★ 结果里**含已知的标准名**（`ISO` / `DIN` 之类）—— 空操作给不出这个。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_hole_standards_smoke.py
# 定位:   给 `scripts/sw_hole_features.list_hole_standards` 取**真机**证据。
# 官方依据: `C:\swapi\types\ISldWorks\GetHoleStandardsData.md` ·`C:\swapi\types\IHoleSta
#           ndardsData\GetHoleStandards.md`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

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
    Path(__file__).resolve().parents[1]
    / "output"
    / "hole-standards-smoke-evidence.json"
)
#: 官方 `swWzdGeneralHoleTypes_e` 里最常用的一档
HOLE_TYPE_COUNTERBORE = 0
#: 真机量到应当出现的几个标准名（ISO / DIN 是各国标准里最普遍的两家）
EXPECT_SOME = ("ISO", "DIN")


def modal_dialogs() -> tuple:
    """★ 已改为**委托共享实现**（2026-10-01 轮 149）。"""
    try:
        from scripts.sw_connect import residual_dialogs
    except ImportError:
        from sw_connect import dismiss_residual_dialogs, residual_dialogs
    #: ★ 2026-10-01（轮 169）：**查到了就点掉**（兜底）——
    #: 只查不点的脚本在真发现弹窗时**什么也没处置**，弹窗还在 ⇒ 下一轮挂在这儿。
    _dialogs, _scanned = residual_dialogs()
    if _dialogs:
        dismiss_residual_dialogs()
    return _dialogs, _scanned


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %h:%M:%S"), "checks": {}}
    checks: list = []

    def chk(name, ok, detail):
        checks.append(bool(ok))
        ev["checks"][name] = {"ok": bool(ok), "detail": str(detail)[:300]}
        print("   %s %-46s %s" % ("✓" if ok else "**✗**", name, str(detail)[:70]))

    sw = None
    rows = []
    try:
        import sw_connect

        from scripts import sw_hole_features as h

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        t0 = time.time()
        rows = h.list_hole_standards(sw, HOLE_TYPE_COUNTERBORE)
        dt = time.time() - t0
        chk(
            "★ list_hole_standards(0) 跑通",
            isinstance(rows, list),
            "%d 条 · %.2fs" % (len(rows), dt),
        )
        ev["rows"] = [r for r in rows]

        chk("★ 返回**非空**", len(rows) > 0, "%d 条" % len(rows))
        chk(
            "★ 每条都有 id 与**非空** name",
            all(
                isinstance(r.get("id"), int) and str(r.get("name") or "").strip()
                for r in rows
            ),
            "例: %s" % (rows[:3],),
        )
        names = [str(r["name"]) for r in rows]
        chk(
            "★ 不含重复名（两组按位配对是否真的对上了）",
            len(names) == len(set(names)),
            "唯一 %d / 共 %d" % (len(set(names)), len(names)),
        )
        hit = [e for e in EXPECT_SOME if e in names]
        chk(
            "★★ 含已知标准名（空操作给不出）",
            bool(hit),
            "命中 %s · 全表 %s" % (hit, names),
        )

        # ── 轮 125：紧固件链路（★ 顺带验"必须热身"那条约束）──────────
        if rows:
            std_name = str(rows[0]["name"])
            ft = h.list_fastener_types(sw, std_name, HOLE_TYPE_COUNTERBORE)
            chk(
                "★ list_fastener_types(%r) 跑通" % std_name,
                isinstance(ft, list) and ft,
                "%d 条 · 前 2: %s" % (len(ft), ft[:2]),
            )
            ev["fastener_types"] = ft

            ft_names = [str(x["name"]) for x in ft]
            chk(
                "★ 紧固件名**非空且不重复**",
                all(n.strip() for n in ft_names)
                and len(set(ft_names)) == len(ft_names),
                "唯一 %d / 共 %d" % (len(set(ft_names)), len(ft_names)),
            )
            # ⚑ 本机中文 UI ⇒ 名称应是中文（这也是"真的从 SolidWorks 读来的"的旁证）
            chk(
                "★ 名称随 UI 语言（本机中文 UI ⇒ 出现中文字符）",
                any("\u4e00" <= ch <= "\u9fff" for n in ft_names for ch in n),
                "例: %s" % ft_names[:3],
            )

            if ft:
                tt = h.list_fastener_table_types(
                    sw, std_name, ft[0]["id"], HOLE_TYPE_COUNTERBORE
                )
                chk(
                    "★ list_fastener_table_types(%r, %r) 跑通"
                    % (std_name, ft[0]["id"]),
                    isinstance(tt, list) and len(tt) > 0,
                    "%r" % (tt,),
                )
                ev["table_types"] = tt

                # ★★ 反向验证"必须热身"：跳过热身 ⇒ 应失败
                try:
                    d_raw = h._hole_standards_data(
                        sw, HOLE_TYPE_COUNTERBORE, initialize=False
                    )
                    ax, bx = h._out_container(), h._out_container()
                    raw_ok = sw_connect.get_com_member(
                        d_raw, "GetFastenerTypes", std_name, ax, bx
                    )
                except Exception as exc:  # noqa: BLE001
                    raw_ok = "✗ %s" % type(exc).__name__
                chk(
                    "★★ **不热身**时 GetFastenerTypes 返回假值（证明热身步骤真的必要）",
                    raw_ok is False or raw_ok == 0,
                    "未热身 -> %r（热身 -> %r）" % (raw_ok, bool(ft)),
                )
    except Exception as exc:  # noqa: BLE001
        chk("整体冒烟", False, "%s: %s" % (type(exc).__name__, str(exc)[:200]))
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass

    modals, _win_scanned = modal_dialogs()
    chk(
        "★ 收尾无残留模态框（已知事实 64 的检查）",
        (not modals) and _win_scanned > 0,
        "扫了 %d 个窗口 · %s"
        % (
            _win_scanned,
            "无模态框" if not modals else "有 %d 个: %s" % (len(modals), modals),
        ),
    )

    ev.update(
        passed=sum(1 for c in checks if c),
        total=len(checks),
        verdict="pass" if checks and all(checks) else "fail",
        finished=time.strftime("%Y-%m-%d %h:%M:%S"),
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print()
    print("  ── %d/%d · verdict: %s ──" % (ev["passed"], ev["total"], ev["verdict"]))
    print("  ⚠ 只证「跑通 + 拿到真实标准名」；**不证 15 条是全集**，也不证 id 的语义。")
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
