r"""@brief 审计：`tools/` 下探针里「**负例输入**」是否**自证**。

## 为什么（2026-10-01 轮 85，Spec Kit `009`）
轮 84 撞见一个**假用例**：`probe_skip_semantics.py` 里用一条正则把「逐模块表」删掉来造"坏文档"，
⚠ **那条正则根本没匹配上** ⇒ 产出的"坏文档"**仍带完整的表** ⇒ 门禁照常 `[PASS]`，
**而我把它当成了"修好了"的证据**。

★ **教训：假用例比没有用例更糟** —— 它给出一份**看起来验过的**证据。

## 本审计判的**一类**（不是全部）
> **凡「用变换（`re.sub` / `replace`）造出来的负例输入」，必须自证变换确实生效**
> —— 即：比对变换前后**不相等**，或**打印前后差异/字节数**。

那正是轮 84 那个 bug 的**可直接机器判**的特征：**变换没生效 ⇒ "坏输入" 等于真输入 ⇒ 用例空转**。

## ⚠ 本审计**抓不到**的（如实声明，不夸大覆盖面）
* **类型 2 · 坏的理由不对**：输入确实"坏"了，但**不是**该用例声称的那一点
  （轮 83 的 DFM 用例就是这类：我造的文档缺的是表，却声称在测"篡改 sha256"）；
* **类型 3 · 负例与正例结果相同**：用例跑了，但**没区分出任何东西**；
* **类型 4 · 断言打在了恒定字段上**。
⇒ 这三类需要**语义**判断，本审计**明确不假装**能判 —— 只把类型 1 钉住。

# ── 来源 ──
# 仓库:   本项目自身（只读审计）
# 文件:   scripts/check_negative_input_selfproof.py
# 定位:   **硬门禁** —— 把「假用例」中**可机器判的那一类**（变换没生效）钉住。
# ⚠ 它扫的是 `tools/` 下的探针（不是本目录）—— 因为假用例的危害正是发生在**探针**里。
# 官方依据: 不适用（本项目内部工具）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.stdout.reconfigure(encoding="utf-8")

#: 「负例输入」的文件名特征
NEG_NAME = re.compile(r"(bad|broken|tamper|invalid|wrong|corrupt|no_?table|missing)", re.I)
#: 变换调用
TRANSFORM = re.compile(r"\bre\.sub\(|\.replace\(|\bre\.subn\(")
#: 「自证」的证据：比对不等 / 打印字节数或长度 / 打印前后
SELF_PROOF = re.compile(
    r"!=\s*\w+|\w+\s*!=\s*\w+"          # 比对不等
    r"|len\([^)]*\)\s*-\s*len\("        # 前后长度差
    r"|->\s*%d|%d\s*->\s*%d"            # 「A -> B 字节」
    r"|assert\s+.*!="                   # 断言
)

WINDOW = 10          # 在「变换」前后多少行内找自证


def scan(path: Path) -> list:
    """⇒ `[(行号, 说明, 是否自证)]`。"""
    lines = path.read_text(encoding="utf-8").splitlines()
    out = []
    for i, line in enumerate(lines):
        if not TRANSFORM.search(line):
            continue
        # 这个变换是否服务于一个「负例输入」？
        window = lines[max(0, i - 4): i + WINDOW]
        blob = "\n".join(window)
        if not NEG_NAME.search(blob):
            continue
        proved = bool(SELF_PROOF.search(blob))
        out.append((i + 1, line.strip()[:74], proved))
    return out


def main() -> int:
    files = sorted(TOOLS.glob("*.py"))
    total = bad = 0
    #: ⚑ **首行必须自带分母**（轮 192）：读者（与人写的 review 脚本）**只看首行** ——
    #:   本项目实测过一次：因为只看首行，我把"分母在第二行"误判成"这道门禁没分母"。
    print("负例输入自证审计 · 扫 %s（**%d** 个 .py）" % (TOOLS, len(files)))
    print("  判据：凡「用变换造负例输入」的地方，必须在前后 %d 行内**自证变换生效**" % WINDOW)
    print("  （比对不等 / 打印前后字节数 / 断言）")
    print()
    for f in files:
        hits = scan(f)
        if not hits:
            continue
        print("── %s" % f.name)
        for ln, txt, proved in hits:
            total += 1
            if not proved:
                bad += 1
            print("   L%-4d %-76s [%s]" % (ln, txt, "自证✓" if proved else "**未自证**"))
    print()
    if bad:
        print("[FAIL] **%d/%d** 处「造负例输入」的变换**没有自证**：" % (bad, total))
        print("  ⚠ 变换可能**根本没生效** ⇒ 那个负例输入**等于真输入** ⇒ **用例空转却显示通过**")
        print("     （2026-10-01 轮 84 就是这么撞见的：删表的正则没匹配上）")
        print("  修法：在变换后加一句**自证** ——")
        print("        `assert new != old` 或 `print('坏输入: %d -> %d 字节' % (len(old), len(new)))`")
        return 1
    print("[PASS] %d 处「造负例输入」的变换**全部自证**（比对/字节数/断言）" % total)
    print("  ⚠ **覆盖面声明**：本审计只判「**变换没生效**」这一类（类型 1）；")
    print("     类型 2/3/4（坏的理由不对 / 负例与正例同结果 / 断言打在恒定字段）**需要语义判断，未判**。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
