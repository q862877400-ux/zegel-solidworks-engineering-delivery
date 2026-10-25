"""把 PSR 的 `.mht` / `.zip` 里的截图按步骤顺序拆成图片（用标准库 `email` 解析）。

## 为什么改成解析库（根因 H）

我手写过 MHT 解析，连栽两次：

1. boundary 硬写成 `"------=_NextPart"`，而真实 boundary 是
   `--=_NextPart_SMP_xxx_NNN` ⇒ 只切出 1 段，**提取 0 张**；
2. 用 `partition("\\n\\n")` 找头部结束，而 zip 里是 **CRLF**（`\\r\\n\\r\\n`）
   ⇒ 匹配不到，把 `Content-Location: xxx.JPEG` 的字母当成 base64 ⇒ 又 0 张。

⇒ 根因不是「这两处写错了」，而是**手写格式解析**。MHTML 就是 MIME，
   标准库 `email` 早就能正确处理 boundary、CRLF、base64、编码。
   **不再手写解析。**

## 用法

```bash
python -B tools/extract_psr_shots.py <psr.zip 或 .mht> <输出目录>
python -B tools/extract_psr_shots.py <psr.zip> <输出目录> --renumber
```

产物：`shot_001.jpg` … + `index.tsv`（序号 / 原始名 / 字节 / 输出文件）。
`--renumber` 时把 PSR 原始文件名里的步号（`screenshot0066.JPEG` → 66）写进索引，
便于把截图和 `steps.md` 的步骤号对应起来。
"""
from __future__ import annotations

import email
import re
import sys
import zipfile
from email import policy
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（示教器 · PSR 截图提取）
# 文件:   tools/extract_psr_shots.py
# 定位:   从 PSR 产出的 .mht/.zip 提取内嵌截图，供「看图核对记录是否与实际操作一致」。
#          起因：2026-10-26 手写 MHT 解析（boundary/CRLF）两次提取 0 张（根因 H）。
# 官方依据: RFC 2045/2046（MIME）· Python 标准库 `email`（policy.default）；
#          PSR 由 Windows 问题步骤记录器生成，图片为 `image/jpeg`。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


def _load_text(src: Path) -> bytes:
    """读 MHT 原始字节（zip 里就取第一个 `.mht`）。"""
    if src.suffix.lower() == ".zip":
        with zipfile.ZipFile(src) as z:
            mhts = [n for n in z.namelist() if n.lower().endswith(".mht")]
            if not mhts:
                raise SystemExit(f"zip 里没有 .mht：{src}")
            return z.read(mhts[0])
    return src.read_bytes()


def extract(src: Path, out: Path, renumber: bool = False) -> list:
    """提取全部图片，回 `[(序号, 原始名, 字节数, 输出文件名, 步号)]`。"""
    out.mkdir(parents=True, exist_ok=True)
    msg = email.message_from_bytes(_load_text(src), policy=policy.default)
    rows = []
    n = 0
    if not msg.is_multipart():
        return rows
    for part in msg.walk():
        ctype = part.get_content_type()
        if not ctype.startswith("image/"):
            continue
        loc = part.get("Content-Location") or ""
        try:
            data = part.get_payload(decode=True)
        except Exception:  # noqa: BLE001
            continue
        if not data:
            continue
        #: 只认真图片：JPEG/PNG 的字节签名
        if not (data.startswith(b"\xff\xd8") or data.startswith(b"\x89PNG")):
            continue
        n += 1
        ext = ".png" if data.startswith(b"\x89PNG") else ".jpg"
        name = f"shot_{n:03d}{ext}"
        (out / name).write_bytes(data)
        m = re.search(r"(\d+)", Path(loc).stem or "")
        step = int(m.group(1)) if m else None
        rows.append((n, Path(loc).name or "(无名)", len(data), name, step))

    lines = ["#\t步号\t原始名\t字节\t输出文件"]
    for r in rows:
        step = r[4] if r[4] is not None else "-"
        lines.append(f"{r[0]}\t{step}\t{r[1]}\t{r[2]}\t{r[3]}")
    (out / "index.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rows


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        print(__doc__)
        return 2
    src, dst = Path(args[0]), Path(args[1])
    rows = extract(src, dst, renumber="--renumber" in sys.argv)
    if not rows:
        print("★ 没提取到图片 —— 确认输入确实是 PSR 的 .mht / .zip")
        return 1
    print(f"提取 {len(rows)} 张截图 → {dst}")
    for r in rows[:5]:
        print(f"   {r[3]}  步号 {r[4]}  {r[2]} 字节")
    if len(rows) > 5:
        print("   …（其余见 index.tsv）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
