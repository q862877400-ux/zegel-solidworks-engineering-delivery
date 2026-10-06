from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(r"D:\AI\SW")


def main() -> int:
    entry = json.loads((ROOT / "_s209_b4f_caps.json").read_text(encoding="utf-8"))
    caps_path = ROOT / "capabilities.yaml"
    data = json.loads(caps_path.read_text(encoding="utf-8"))
    caps = data["capabilities"]
    if any(c.get("id") == entry["id"] for c in caps):
        print("已存在，跳过")
    else:
        caps.append(entry)
        print("追加 %s (%s)" % (entry["id"], entry["level"]))
    out = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(out)
    caps_path.write_text(out, encoding="utf-8")
    print("capabilities 共 %d 条" % len(caps))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
