"""★ 真机试 `IFeature.GetErrorCode2(out bool IsWarning)` —— ★ 它到底调不调得动。

★★ 背景（★ `workflow-15` 的 **B-3** · ★ 也是阶段 2 生产第 **15** 条）：
  · ★ 官方 `C:\\swapi\\types\\IFeature\\GetErrorCode.md` 逐字
    「**Obsolete. Superseded by [[IFeature::GetErrorCode2]].**」
  · ★★ 而本仓 `scripts/sw_weldment.py:500` **调用的是旧的 `GetErrorCode()`**、★ **且没有换用后继的说明** ✓
  · ★★★ 后继签名逐字：`System.int GetErrorCode2( **out** System.bool IsWarning )` ⇒ ★ **含 `out`** ✓

★★★ 判据（★ 跑之前写死）：★ **能调通（不抛异常）就算"可换"**；
  ★ **报「类型不匹配」/「无效的参数数目」/`0x80010105` 等 ⇒ 记"后端到不了"** ✓
  ★★ 依据：★ **事实 47** —— 含 by-ref 的成员在 pywin32 迟到绑定下**到不了**；
    ★ **但那要实测，不许凭签名就下结论**（★ 铁律 2）✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。
# 文件:   tools/probe_geterrorcode2.py
# 定位:   ★ 阶段 2：生产第 15 条 `sw_weldment.py::GetErrorCode` 的处置依据。
#   官方依据: `C:\\swapi\\types\\IFeature\\GetErrorCode.md` · `GetErrorCode2.md`
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

from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402

OUT = REPO / "output" / "geterrorcode2-evidence.json"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def _try(fn, *a):
    try:
        return {"ok": True, "ret": repr(fn(*a))[:100]}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:190])}


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S")}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        _g(
            _g(doc, "SketchManager"),
            "CreateCornerRectangle",
            -0.02,
            -0.015,
            0.0,
            0.02,
            0.015,
            0.0,
        )
        P.end_sketch(doc)
        nm = [n for n in (P.feature_names(doc) or []) if n.startswith("草图")]
        P.extrude_boss(doc, (nm[-1] if nm else "草图1"), 10.0)
        #: ★ 取一个真实特征
        feat = None
        try:
            f = _g(doc, "FirstFeature")
            for _ in range(40):
                if f is None:
                    break
                if str(_g(f, "GetTypeName2") or "") in ("Extrusion", "Boss", "Extrude"):
                    feat = f
                    break
                f = _g(f, "GetNextFeature")
        except Exception:  # noqa: BLE001
            pass
        R["取到特征"] = repr(feat)[:60] if feat is not None else "None"
        if feat is None:
            R["skip"] = "★ 没取到特征"
            raise SystemExit(0)

        #: ★★ ① 旧的（★ 本仓在用的）—— ★ 作为基线
        R["旧_GetErrorCode()"] = _try(_g, feat, "GetErrorCode")
        #: ★★ ② 新的（★ 带 out）—— ★ 各试几种形态（★ 因为 by-ref 的传法有讲究）
        R["新_GetErrorCode2()__0参"] = _try(_g, feat, "GetErrorCode2")
        try:
            out = C.out_i4()
            R["新_GetErrorCode2(out_i4)"] = _try(_g, feat, "GetErrorCode2", out)
        except Exception as exc:  # noqa: BLE001
            R["新_GetErrorCode2(out_i4)"] = {
                "ok": False,
                "err": "out_i4 建不出来: %s" % str(exc)[:90],
            }
        #: ★ 直接取成员（★ 看它是不是 bound method —— ★ 事实：`get_com_member` 失败时会
        #: 原样回成员）
        try:
            v = _g(feat, "GetErrorCode2")
            R["★_GetErrorCode2_取到的类型"] = "%s · 是成员本身=%s" % (
                type(v).__name__,
                not hasattr(v, "_oleobj_"),
            )
        except Exception as exc:  # noqa: BLE001
            R["★_GetErrorCode2_取到的类型"] = "取不到: %s" % str(exc)[:90]
    except SystemExit:
        pass
    except Exception as exc:  # noqa: BLE001
        R["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:  # noqa: BLE001
            pass
    new_ok = [
        k
        for k, v in R.items()
        if k.startswith("新_") and isinstance(v, dict) and v.get("ok")
    ]
    R["★★_结论"] = (
        "★ 新入口**能调**（%s）⇒ 可换" % new_ok
        if new_ok
        else "★★ 新入口**三种形态全不通** ⇒ ★ **记「后端到不了」并保留旧的** ✓"
    )
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(
        json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
