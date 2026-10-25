"""★ 证据指纹与失效判定（规格 350 · FR-014 / T029）。

## 义务原文

> **FR-014**：规则/方法升级必须能**识别受影响交付**并使**旧证据失效**。

## 为什么需要指纹

本仓的验收证据（`output/s3-acceptance.json`）是**某一时刻**在**某一版产物**上用
**某一版判定器**跑出来的。三者任一变了，旧证据就不再代表现在：

| 变的什么 | 后果 |
|---|---|
| 判定器（`CHECKER_VERSION`）升级 | 旧结论是按旧判据得出的 ⇒ 可能由 pass 变 fail |
| 支持域（`support-domain.yaml` 的 `declared_at`）改了 | 参数域变了 ⇒ 旧证据不覆盖新域 |
| 交付件（`.SLDPRT` 内容）改了 | 证据不是这一版产物的 ⇒ 失效 |

★ 没有指纹时，这三件事**全都看不出来** —— 报告会一直显示旧的 pass。

## 指纹怎么取（都可复算，不靠记忆）

```python
CHECKER_VERSION × 5 个判定器   → 任何一条判据升级都会让指纹变
support-domain.declared_at     → 域变更
sha256(交付件)                  → 产物变更
```

★ 时间戳**不进指纹**：时间变了不代表证据失效，用它会让指纹天天变（那就没人看了）。

## 用法

```
python -B scripts/check_evidence_freshness.py            # 判当前证据新不新
python -B scripts/check_evidence_freshness.py --write    # 把当前指纹写进证据
```
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

EVIDENCE = R / "output" / "s3-acceptance.json"
DOMAIN = R / "docs" / "support-domain.yaml"
DELIVERABLE = R / "output" / "stage2" / "板1_rev-1.SLDPRT"


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（证据失效判定 · 规格 350 FR-014）
# 文件:   scripts/check_evidence_freshness.py
# 定位:   给验收证据算「判定器版本 × 支持域版本 × 交付件内容」指纹；
#          任一变化即判旧证据失效，必须重跑验收。
# 官方依据: 不适用（本仓自定口径）；哈希用标准库 hashlib
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

#: 参与指纹的判定器（升级任何一个都会让旧证据失效）
CHECKERS = (
    "e1_sketch",
    "e2_e3_solid",
    "e4_assembly",
    "e5_e6_drawing",
    "e7_provenance",
)


def _checker_versions() -> dict:
    out = {}
    for name in CHECKERS:
        mod = __import__("engineering.acceptance.%s" % name, fromlist=["CHECKER_VERSION"])
        out[name] = str(getattr(mod, "CHECKER_VERSION", ""))
    return out


def _domain_stamp() -> str:
    try:
        import yaml

        d = yaml.safe_load(DOMAIN.read_text(encoding="utf-8")) or {}
        return str(d.get("declared_at") or "")
    except Exception:  # noqa: BLE001
        return ""


def _file_sha256(p: Path) -> str:
    if not p.is_file():
        return ""
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_fingerprint() -> dict:
    """当前指纹（可复算）。"""
    return {
        "checkers": _checker_versions(),
        "domain_declared_at": _domain_stamp(),
        "deliverable_sha256": _file_sha256(DELIVERABLE),
    }


def compare(recorded: dict, current: dict) -> list:
    """回差异列表；空表示证据仍新鲜。"""
    diffs: list = []
    rec_checkers = recorded.get("checkers") or {}
    for name, cur in (current.get("checkers") or {}).items():
        old = rec_checkers.get(name)
        if old != cur:
            diffs.append(
                "判定器 %s 由 %r 升到 %r ⇒ 旧结论按旧判据得出，必须重跑"
                % (name, old, cur)
            )
    if recorded.get("domain_declared_at") != current.get("domain_declared_at"):
        diffs.append(
            "支持域版本 %r → %r ⇒ 参数域变了，旧证据不覆盖新域"
            % (recorded.get("domain_declared_at"), current.get("domain_declared_at"))
        )
    if recorded.get("deliverable_sha256") != current.get("deliverable_sha256"):
        diffs.append("交付件内容变了（sha256 不同）⇒ 证据不是这一版产物的")
    return diffs


def read_recorded() -> dict:
    if not EVIDENCE.is_file():
        return {}
    try:
        return (json.loads(EVIDENCE.read_text(encoding="utf-8")) or {}).get(
            "fingerprint"
        ) or {}
    except Exception:  # noqa: BLE001
        return {}


def write_fingerprint(fp: dict) -> bool:
    if not EVIDENCE.is_file():
        return False
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    data["fingerprint"] = fp
    EVIDENCE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return True


def main() -> int:
    current = compute_fingerprint()
    if "--write" in sys.argv:
        ok = write_fingerprint(current)
        print("★ 已写入指纹：%s" % ("成功" if ok else "失败（证据文件不存在）"))
        return 0 if ok else 1

    recorded = read_recorded()
    if not recorded:
        print("★ [STALE] 证据里没有指纹 ⇒ 无法证明它对应现在这一版")
        print("   修法：重跑验收后 `--write`")
        return 1

    diffs = compare(recorded, current)
    if diffs:
        print("★ [STALE] 旧证据已失效（%d 处）：" % len(diffs))
        for d in diffs:
            print("   -", d)
        return 1

    print(
        "★ [FRESH] 证据与当前一致（判定器 %d 个 · 域 %s · 交付件 %s…）"
        % (
            len(current["checkers"]),
            current["domain_declared_at"],
            (current["deliverable_sha256"] or "")[:12],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
