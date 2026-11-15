"""打印齿轮方法层 v0 的两份真实输出：一份有解、一份无解。"""
from __future__ import annotations

from gear_method import GearRequest, derive, render

print("=" * 78)
print("客户：减速 3 倍，两轴中心距 40 mm")
print("=" * 78)
print(render(derive(GearRequest(ratio=3.0, center_mm=40.0))))

print()
print("=" * 78)
print("工程师：减速 2.5，中心距 43 mm，锁定 z1=20")
print("=" * 78)
print(render(derive(GearRequest(ratio=2.5, center_mm=43.0, pin_z1=20))))

print()
print("=" * 78)
print("客户：减速 3 倍，但中心距只有 30 mm")
print("=" * 78)
print(render(derive(GearRequest(ratio=3.0, center_mm=30.0))))

print()
print("=" * 78)
print("口径对照：同样的需求，z_min 取 17（知识库） vs 18（归档实现）")
print("=" * 78)
for pol in ("kb", "strict"):
    d = derive(GearRequest(ratio=3.0, center_mm=40.0, z_min_policy=pol))
    zmin = next(r for r in d.rows if r.key == "z_min")
    print(f"  口径={pol:6s} z_min={zmin.value}  →  {zmin.evidence}")
