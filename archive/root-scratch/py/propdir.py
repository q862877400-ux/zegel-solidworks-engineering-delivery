# -*- coding: utf-8 -*-
"""只读元数据：SolidWorks interop 程序集里，属性方向能不能直接读出来？"""
import sys
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
import clr
from System.Reflection import Assembly
R = r"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist"
asm = Assembly.LoadFrom(R + r"\SolidWorks.Interop.sldworks.dll")
iface = asm.GetType("SolidWorks.Interop.sldworks.ISldWorks")
print("  接口:", iface.FullName)
props = [p for p in iface.GetProperties() if not p.Name.startswith("I")]
print("  属性总数(去 I 前缀):", len(props))
print()
print("  %-32s %-10s %-10s %s" % ("属性", "CanRead", "CanWrite", "类型"))
print("  " + "-"*66)
ro = rw = wo = 0
for p in sorted(props, key=lambda x: x.Name)[:14]:
    r, w = p.CanRead, p.CanWrite
    if r and w: rw += 1
    elif r: ro += 1
    else: wo += 1
    print("  %-32s %-10s %-10s %s" % (p.Name, r, w, p.PropertyType.Name))
# 全量统计
tot_ro = sum(1 for p in props if p.CanRead and not p.CanWrite)
tot_rw = sum(1 for p in props if p.CanRead and p.CanWrite)
tot_wo = sum(1 for p in props if p.CanWrite and not p.CanRead)
print()
print("  ISldWorks 属性方向分布: 只读 %d / 读写 %d / 只写 %d" % (tot_ro, tot_rw, tot_wo))
# EnumDocuments 在不在属性里？
p = iface.GetProperty("EnumDocuments")
if p is not None:
    print("  EnumDocuments: CanRead=%s CanWrite=%s" % (p.CanRead, p.CanWrite))