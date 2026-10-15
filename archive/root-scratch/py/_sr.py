import sys, types, io, importlib.util, inspect
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = r"C:\swprojects\sw-skill-fork"
c = types.ModuleType("sw_connect"); c.get_com_member = lambda o,n,*a,**k: getattr(o,n,None)
sys.modules["sw_connect"] = c
spec = importlib.util.spec_from_file_location("sr", R + r"\scripts\sketch_relations.py")
m = importlib.util.module_from_spec(spec); sys.modules["sr"] = m
spec.loader.exec_module(m)
print("  约束类型", len(m.SKETCH_CONSTRAINT_TYPES), "项；槽创建", len(m.SKETCH_SLOT_CREATION_TYPES),
      "项；槽长度", len(m.SKETCH_SLOT_LENGTH_TYPES), "项；关系实体", len(m.SKETCH_RELATION_ENTITY_TYPES), "项")
print("  关键约束:", {k: m.SKETCH_CONSTRAINT_TYPES[k] for k in ("coincident","horizontal","vertical","perpendicular","tangent","midpoint")})
for f in ("add_relation","list_relations","get_allowed_relations","suppress_relation",
          "create_spline","set_slot_length","set_slot_width","collect_relation_evidence"):
    print("  %-26s %s" % (f, inspect.signature(getattr(m, f))))
