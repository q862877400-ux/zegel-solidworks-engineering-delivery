r"""@brief 探针：把「文档在、但逐模块表读不出来」当输入，看 `check_signature_audit_freshness` 怎么走。

## 为什么探（2026-10-01 轮 83，Spec Kit `007`）
轮 82 修掉一个**假绿**（`check_report_freshness`：报告那行读不出 ⇒ 曾 SKIP ⇒ 实际是 exit 0 全绿）。
轮 83 系统排查**其它门禁**的 SKIP 分支，发现 `check_signature_audit_freshness.py` 有一处**同型**：
```
L235  if not claimed:  →  print("**SKIP** —— 文档里找不到逐模块表")  →  return 0
```
⚠ 「**文档里找不到表**」是**输入坏了**还是**数据源不可用**？—— **前者**（文档是本仓库的文件）。
⇒ 本探针**实测**它当前怎么走（**不推理**）。

# ── 来源 ──
# 仓库:   本项目自身（只读探针）
# 文件:   tools/probe_skip_semantics.py
# 定位:   系统排查门禁 SKIP 分支的语义 —— 为 Spec Kit `007`（「数据源不可用 vs 输入坏了」）取证。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(r"" + _ROOT_S + r"")
sys.stdout.reconfigure(encoding="utf-8")

CHECKS = {
    "check_signature_audit_freshness.py": ["--doc"],
    "check_report_freshness.py": ["--report"],
    "check_digest_freshness.py": [],
    "check_license_redlines.py": [],
    "check_provenance.py": [],
    "check_env_pitfalls.py": [],
}


def _args_of(script: Path) -> list:
    """从源码里抽 argparse 参数名（**读实现，不猜**）。"""
    out = []
    try:
        text = script.read_text(encoding="utf-8")
    except OSError:
        return out
    for m in re.finditer(r"add_argument\(\s*[\"'](--[\w-]+)", text):
        out.append(m.group(1))
    return out


def main() -> int:
    print("══ 各门禁的 argparse 参数（读源码得到）══")
    for name in CHECKS:
        s = REPO / "scripts" / name
        print("  %-42s %s" % (name, _args_of(s) or "（无）"))

    print()
    print("══ ① 正常输入 ⇒ 各门禁退出码（基线）══")
    for name in CHECKS:
        s = REPO / "scripts" / name
        p = subprocess.run([sys.executable, str(s)], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", cwd=str(REPO),
                           stdin=subprocess.DEVNULL)
        print("  %-42s exit=%d" % (name, p.returncode))

    print()
    print("══ ② ★ 「文档在、但内容读不出来」⇒ 各「新鲜度」门禁的退出码 ══")
    # ⚠⚠ **第一版这个用例本身有 bug**（2026-10-01 轮 84 发现）：
    #   我用正则去「删掉逐模块表」，但那条正则**没匹配上** ⇒ 产出的"坏文档"**仍带着完整的表**
    #   ⇒ 门禁照常 `[PASS]`，而我把它当成「修好了」的证据。★ **假用例比没有用例更糟**。
    # ⇒ 正解：**直接造一份"只有标题、根本没有表"的文档** —— 那才是「文档在、表读不出」的定义。
    bad = Path(tempfile.gettempdir()) / "bad-signature-audit.md"
    bad.write_text(
        "# 签名审计\n\n"
        "> ⚠ 本文件**故意不含**「逐模块」表 —— 用于验证门禁在「产物坏了」时的行为。\n",
        encoding="utf-8",
    )
    print("  坏文档: 只有标题，**不含逐模块表**（%d 字节）" % bad.stat().st_size)
    p = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "check_signature_audit_freshness.py"),
         "--doc", str(bad)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO), stdin=subprocess.DEVNULL,
    )
    print("  ★ check_signature_audit_freshness --doc <坏文档> ⇒ **exit=%d**（应为 1）"
          % p.returncode)
    for l in (p.stdout or "").splitlines()[-3:]:
        if l.strip():
            print("       %s" % l.strip()[:100])

    real_rep = REPO / "docs" / "harvest-report.md"
    ro = real_rep.read_text(encoding="utf-8")
    # ⚠ **变换必须自证生效**（2026-10-01 轮 85，`tools/audit_negative_input_selfproof.py` 抓出来的）：
    #   轮 84 那个假用例就是「**变换没匹配上 ⇒ "坏输入" 等于真输入 ⇒ 用例空转却显示通过**」。
    #   ⇒ 这里**先算、再断言、再打印前后字节数**，让用例自己证明输入真的坏了。
    bad2_text = re.sub(r"> 偏离上游：.+? · 工作区 clean", "> 偏离上游： · 工作区 clean", ro, count=1)
    assert bad2_text != ro, "**变换没生效** —— 那个「坏报告」其实等于真报告，用例不成立"
    bad2 = Path(tempfile.gettempdir()) / "bad-harvest-report.md"
    bad2.write_text(bad2_text, encoding="utf-8")
    print("  坏报告: %d -> %d 字节（数字被抹掉，自证 ✓）" % (len(ro.encode()), len(bad2_text.encode())))
    p2 = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "check_report_freshness.py"),
         "--report", str(bad2)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO), stdin=subprocess.DEVNULL,
    )
    print("  ★ check_report_freshness --report <坏报告> ⇒ **exit=%d**（轮 82 已修，应为 1）"
          % p2.returncode)

    print()
    print("══ ③ 仓库自身文件缺失（`server.py`）⇒ 遮蔽门禁怎么走 ══")
    src = REPO / "scripts" / "check_workspace_shadowing.py"
    txt = src.read_text(encoding="utf-8")
    m = re.search(r"SERVER\s*=\s*(.+)", txt)
    print("  SERVER = %s" % (m.group(1).strip() if m else "?"))
    p3 = subprocess.run([sys.executable, str(src)], capture_output=True, text=True,
                        encoding="utf-8", errors="replace", cwd=str(REPO),
                        stdin=subprocess.DEVNULL)
    print("  正常跑 ⇒ exit=%d" % p3.returncode)
    print("  ⚠ 它 `if not SERVER.is_file(): print('[SKIP] 找不到 …'); return 0` ——")
    print("    而 SERVER 是**本仓库的文件** ⇒ 不在 = **仓库坏了**，不是「数据源不可用」。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
