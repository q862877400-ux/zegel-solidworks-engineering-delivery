r"""@brief 审计：**数组类形参的 `[in,out]` 方向** —— 用**类型库方法表**（第 4 套签名源）。

## 为什么（轮 189）
项目的 byref 规则（`scripts/audit_byref_args.py` 的 L19）写的是：
```
`Int32&` **算**一个（必须传），`Object&` / `Variant&` / `Dispatch&` **不算**（纯出参，不用传）
```
★ 这条规则**来自反射文本** —— 而反射里的 `&` **只说明"按引用"，不区分方向**。
★★★ 轮 188 用 comtypes 读**类型库方法表**时发现：它**直接给 `[in]` / `[out]` / `[in,out]`**，
    而实测的 `PutDouble(VariantArray = **in,out**)` 是一个**必须传**的数组形参 ——
    ⇒ ★ **按上面那条规则，它会被当成"纯出参、不用传"** ⇒ **那是一条会漏掉 `in,out` 的规则**。

## 判据
```
① 从 `sldworks.tlb` 取**全部**接口的方法表；挑出**含数组类形参且方向是 `in,out`(flag=3)** 的成员
   （数组类 = VARIANT / LP_tagVARIANT / POINTER(IDispatch) / POINTER(IUnknown)）
② 逐个看**本仓库代码里有没有**以字面量调用同名成员（`get_com_member(x, "Name")` / `call_com_member`）
③ ★ 对命中的，**报告它有没有真的传那个数组** —— 按本项目现有规则它**会被跳过** ⇒ **候选缺陷**
④ **不做结论**（只在有真机证据时下结论）：本审计产出**候选清单**，注明"待逐个真机核"
```

## ⚠ 安全
**纯静态**：只读类型库与源码；**不连 SolidWorks、不改任何文件**。

# ── 来源 ──
# 仓库:   本项目自身
# 文件:   tools/audit_inout_array_params.py
# 定位:   给 Spec Kit `109` 用**新发现的方向信息**复核既有 byref 规则。
# 官方依据: `D:/Program Files/SOLIDWORKS Corp/SOLIDWORKS/sldworks.tlb` 的方法表
#          （`comtypes.client.GetModule(...)` → `<Iface>._methods_`）
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
sys.stdout.reconfigure(encoding="utf-8")
OUT = Path(Path(__file__).resolve().parents[1] / "output" / "inout-array-params.json")
SWDIR = Path(r"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS")
#: ⚠⚠ **2026-10-01（轮 190）从「单个 tlb」泛化成「多个」** ——
#: 理由：轮 189 只扫了 `sldworks.tlb`，而**仿真域**（`ICW*`）是我们**真正大量调用**的那
#: 一块，
#: 它在**另一个类型库**里。★ 只扫 sldworks 就报「0 命中」，覆盖面是**不够的**（轮 189 的
#: 限度①）。
#:   列的是**我们确实镜像的 12 个程序集**（`scripts/sw_api_*.py` 与之同名）+ 主库。
TLBS = [
    SWDIR / "sldworks.tlb",
    SWDIR / "Simulation" / "cosworks.tlb",
    SWDIR / "swpublished.tlb",
    SWDIR / "swdimxpert.tlb",
    SWDIR / "sldcostingapi.tlb",
    SWDIR / "SWRoutingLib.tlb",
    SWDIR / "swmotionstudy.tlb",
    SWDIR / "fworks" / "FWorks.tlb",
    SWDIR / "dsgnchk" / "Dsgnchk.tlb",
    SWDIR / "sldutils" / "gtswUtilities.tlb",
    SWDIR / "swdocumentmgr.dll",
]
SCAN = [ROOT / "scripts", ROOT / "mcp-server", ROOT / "tools"]
CALLS = ("get_com_member", "call_com_member", "safe_get_com_member", "get_com_member_raw")

ARRAYISH = ("VARIANT", "LP_tagVARIANT", "POINTER(IDispatch)", "POINTER(IUnknown)")


def scan_tlb(cc, path: Path) -> tuple:
    """扫一个类型库 ⇒ (含 in,out 数组形参的记录, 接口数, 无方向信息的条目数, 无方向信息的成员名)。"""
    mod = cc.GetModule(str(path))
    found, n_iface, no_flags = [], 0, 0
    noflag_names: set = set()
    noflag_array_names: set = set()
    for name in dir(mod):
        cls = getattr(mod, name)
        ms = getattr(cls, "_methods_", None)
        if not ms:
            continue
        n_iface += 1
        for m in ms:
            try:
                mname, argtypes, flags = m[1], m[2], m[3]
            except Exception:      # noqa: BLE001
                continue
            #: ⚠⚠ **2026-10-01（轮 189）：`flags` 可能是 `None`**（有些方法条目没有方向
            #: 信息）
            #: ⇒ 不能直接迭代；**且要如实统计有多少条没有方向信息**（否则"扫了多少"是虚
            #: 的）。
            if not flags:
                no_flags += 1
                noflag_names.add(mname)
                #: ⚠⚠⚠ **2026-10-01（轮 190）收窄「未判」这一档**：
                #: `flags` 没有 ⇒ **方向未知**；但 **`argtypes` 还在** ⇒ **能判"有没有数
                #: 组类形参"**。
                #:   ★ 本判据只关心「**数组类形参** + in,out」⇒
                #: 连**数组类形参都没有**的成员 ⇒ **与本判据无关**（**正当排除**，不是"
                #: 未判"）。
                if any((getattr(t, "__name__", str(t)) in ARRAYISH) for t in (argtypes or ())):
                    noflag_array_names.add(mname)
                continue
            for idx, fl in enumerate(flags):
                #: ⚠⚠ **2026-10-01（轮 189）第一版这里崩了**：`flags` 的元组**不总是 2 
                #: 元素** ——
                #: 出参那条常带第 3 个字段（comtypes 的 faketype 标记）⇒ 必须**按下标取*
                #: *，不能解包。
                #: 实测到的方向码：`1`=in · `3`=in,out · `10`=out（= 2 | 8）
                if not fl:
                    continue
                flag = fl[0]
                pname = fl[1] if len(fl) > 1 else "?"
                if flag != 3:      #: 只要 **in,out**
                    continue
                tn = getattr(argtypes[idx], "__name__", str(argtypes[idx]))
                if tn in ARRAYISH:
                    found.append({"tlb": path.name, "iface": name, "member": mname,
                                  "param": pname, "argtype": tn, "index": idx})
    return found, n_iface, no_flags, noflag_names, noflag_array_names


def main() -> int:
    import comtypes.client as cc

    all_found: list = []
    per_tlb: dict = {}
    tot_iface = tot_noflags = 0
    noflag_all: set = set()
    noflag_array_all: set = set()
    for p in TLBS:
        if not p.is_file():
            print("  ⚠ 类型库不在 ⇒ 跳过: %s" % p.name)
            continue
        try:
            f, ni, nf, nfn, nfa = scan_tlb(cc, p)
        except Exception as exc:      # noqa: BLE001
            print("  ⚠ %s ⇒ 载入失败: %s: %s" % (p.name, type(exc).__name__, str(exc)[:60]))
            continue
        per_tlb[p.name] = {"interfaces": ni, "inout_array": len(f), "no_flags": nf}
        all_found += f
        tot_iface += ni
        tot_noflags += nf
        noflag_all |= nfn
        noflag_array_all |= nfa
        print("  %-24s 接口 %-5d · `in,out` 数组形参 **%d** 条 · 无方向信息 %d 条"
              % (p.name, ni, len(f), nf))

    found = all_found
    print()
    print("  ── 合计：扫了 **%d** 个接口 · `in,out` 数组形参 **%d** 条 · 无方向信息 %d 条 ──"
          % (tot_iface, len(found), tot_noflags))

    #: ② 本仓库代码里按字面量调用了哪些（成员名维度）
    called: dict = {}
    for base in SCAN:
        if not base.is_dir():
            continue
        for f in sorted(base.glob("*.py")):
            t = f.read_text(encoding="utf-8", errors="replace")
            for mm in re.finditer(r"(?:get_com_member|call_com_member|safe_get_com_member"
                                  r"|get_com_member_raw)\s*\([^,()]+,\s*[\"']([A-Za-z_]\w*)[\"']", t):
                called.setdefault(mm.group(1), set()).add(f.name)
    hits = [r for r in found if r["member"] in called]
    #: ⚠⚠⚠ **2026-10-01（轮 190）补一道**覆盖面自检** —— 没有它，"0 命中"是不完整的：**
    #:   本轮发现「无方向信息」的条目有 **1008** 条（远多于 62 条有方向的）⇒
    #:   ★ **那 1008 条里若也有我们调用的成员，则它们**根本没被这条判据覆盖****。
    #: ⇒ 如实报出「无方向信息 ∩ 本仓库调用过」的成员名 —— 那是**未判**的部分，不是"没问
    #: 题"。
    unjudged_all = sorted(noflag_all & set(called))
    unjudged_arr = sorted(noflag_array_all & set(called))
    print("  ★ 其中**本仓库按字面量调用过**的: **%d** 个" % len(hits))
    print("  ⚠ 无方向信息 ∩ 调用过的 = **%d** 个（其中**有数组类形参**的 = **%d** 个）"
          % (len(unjudged_all), len(unjudged_arr)))
    print("  ⇒ ★★ **真未判**（方向未知 **且** 有数组类形参）: **%d** 个 ⇒ %s"
          % (len(unjudged_arr), unjudged_arr[:8] if unjudged_arr else "（无 ⇒ 这一类已判完）"))
    print("  ⇒ 其余 **%d** 个**没有数组类形参** ⇒ 与本判据无关（**正当排除**，不算未判）"
          % (len(unjudged_all) - len(unjudged_arr)))
    print()
    print("  ── 命中清单（成员 · 形参 · 类型库 · 出现在哪个文件）──")
    seen = set()
    for r in sorted(hits, key=lambda x: (x["tlb"], x["member"])):
        k = (r["tlb"], r["member"], r["param"])
        if k in seen:
            continue
        seen.add(k)
        print("    %-32s %-20s %-16s %s"
              % (r["member"], r["param"], r["tlb"], sorted(called[r["member"]])[:2]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"per_tlb": per_tlb, "interfaces": tot_iface,
                               "no_flags": tot_noflags, "inout_array_params": found,
                               "called_hits": hits, "called_members": len(called)},
                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print("  证据: %s" % OUT)
    print("  ⚠ **本审计只出候选清单** —— 「代码有没有真的传那个数组」要逐个回代码/真机核，")
    print("     ★ 不在此下结论（本项目纪律：静态候选 ≠ 缺陷）。")
    if tot_iface == 0:
        print("  ✗ 接口数为 0 ⇒ 判据没生效（事实 46 的假绿）⇒ 非 0 退出")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
