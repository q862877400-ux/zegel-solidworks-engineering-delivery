"""不变量：**`scripts/` 与 `tools/` 里没有裸传的标量 by-ref 出参**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   `scripts/audit_byref_args.py`（被本测试调用的审计器）
# 定位:   把「裸 by-ref 标量出参」这条**静默失败**类做成可执行的不变量。
#         记忆里记着「AST 审计发现 18 个裸出参，`fix_bare_outparams.py` 可修」——
#         而那个工具**不存在**，所以这条一直悬着。本测试把它收口。
# 官方签名依据: 不适用（静态检查；`out_i4()` 的契约由 `sw_connect.py` 的来源块背书）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本测试**不连 SolidWorks**：只跑静态审计（AST + 反射文本比对）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT = REPO_ROOT / "scripts" / "audit_byref_args.py"

#: 反射清单（`reflect-interop.ps1` 生成的纯元数据转储）
RAW = Path(Path(__file__).resolve().parents[1] / "_raw")


def _load_audit():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("audit_byref_args_under_test", AUDIT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["audit_byref_args_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def audit():
    if not AUDIT.is_file():
        pytest.skip("audit_byref_args.py 不在")
    return _load_audit()


@pytest.fixture(scope="module")
def sig_paths():
    if not RAW.is_dir():
        pytest.skip("反射转储不在（D:\\AI\\SW\\_raw）—— 缺数据源不算违规")
    paths = [str(p) for p in sorted(RAW.rglob("iface_*.txt"))]
    if not paths:
        pytest.skip("反射转储里没有 iface_*.txt")
    return paths


# ── ① 核心不变量：0 处裸传 ────────────────────────────────────────
def test_no_bare_byref_scalar_out_params(audit, sig_paths):
    """`scripts/` + `tools/` 里**不得**出现裸传的标量 by-ref 出参。

    ⚠ 为什么这是不变量而不是「有空再查」：裸传**有的直接抛错、有的静默无效**，
    而静默无效是本项目反复踩的头号敌人（已知事实 8 / 30）。
    """
    table = audit.load_full_signatures(sig_paths)
    targets = (sorted((REPO_ROOT / "scripts").glob("*.py"))
               + sorted((REPO_ROOT / "tools").glob("*.py")))
    bad: list[dict] = []
    checked = 0
    for t in targets:
        if not t.is_file():
            continue
        rows, n = audit.scan(t, table)
        bad.extend(rows)
        checked += n
    # 检查量太小说明审计器坏了（不是「很干净」）—— 这条防的是**假绿**
    assert checked >= 300, (
        "只检查了 %d 个调用点（应 ≥300）⇒ 审计器可能坏了，**这个绿不可信**" % checked
    )
    assert bad == [], "标量出参裸传 %d 处：\n  %s" % (
        len(bad),
        "\n  ".join("%s:%d %s 第 %d 位应为 %s，实参 `%s`"
                    % (b["file"], b["line"], b["member"], b["position"],
                       b["type"], b["actual"][:40]) for b in bad[:20]),
    )


# ── ② 审计器自己的「防假绿」能力（负例）──────────────────────────
def test_audit_catches_a_planted_bare_outparam(audit, sig_paths, tmp_path):
    """**种一个违规进去，审计器必须报出来** —— 否则这个绿等于没查。

    ⚠ 这条比上面那条更重要：一个「永远返回 0」的审计器也能让上面那条通过。
    """
    table = audit.load_full_signatures(sig_paths)
    # 找一条**真有标量出参**的签名来种
    victim = None
    for member, variants in table.items():
        for sig_name, plist in variants:
            counted = audit.counted_positions(plist)
            if any(p.strip().endswith("&") and audit.SCALAR_OUT.match(p.strip())
                   for _i, p in counted):
                victim = (member, sig_name, counted)
                break
        if victim:
            break
    if victim is None:
        pytest.skip("反射里找不到带标量出参的签名，无法种负例")
    member, sig_name, counted = victim
    # 按「调用方要传的实参」摆一个裸值
    args = ["0" for _ in counted]
    for pos, (raw_i, ptype) in enumerate(counted):
        if ptype.strip().endswith("&") and audit.SCALAR_OUT.match(ptype.strip()):
            args[pos] = "0"          # ← **裸传**（应为 out_i4()）
            break
    src = tmp_path / "planted.py"
    src.write_text(
        "def f(get_com_member, obj):\n"
        "    return get_com_member(obj, %r, %s)\n" % (member, ", ".join(args)),
        encoding="utf-8",
    )
    rows, checked = audit.scan(src, table)
    assert checked >= 1, "审计器连这个种下的调用点都没看到"
    assert rows, "**审计器漏掉了种下的裸 by-ref 出参** ⇒ 它的绿不可信"


# ── ③ 命令行入口可用（人能一行跑到）─────────────────────────────
def test_cli_is_runnable(audit, sig_paths):
    proc = subprocess.run(
        [sys.executable, str(AUDIT), "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=120, cwd=str(REPO_ROOT), stdin=subprocess.DEVNULL,
    )
    assert proc.returncode == 0, proc.stderr[-300:]
    assert "by-ref" in (proc.stdout or "")
