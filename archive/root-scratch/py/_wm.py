import sys, types, io, importlib.util, inspect
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = r"C:\swprojects\sw-skill-fork"
c = types.ModuleType("sw_connect"); c.get_com_member = lambda o,n,*a,**k: getattr(o,n,None); c.save_document = lambda *a,**k: None
sys.modules["sw_connect"] = c
d = types.ModuleType("sw_document_data"); d.set_custom_properties = lambda *a,**k: None
sys.modules["sw_document_data"] = d
p = types.ModuleType("sw_part"); p._ensure_sketch_selected = lambda *a,**k: None
sys.modules["sw_part"] = p
pf = types.ModuleType("sw_preflight"); pf.import_com_dependencies = lambda: (None,None,None)
sys.modules["sw_preflight"] = pf
spec = importlib.util.spec_from_file_location("sw", R + r"\scripts\sw_weldment.py")
m = importlib.util.module_from_spec(spec); sys.modules["sw"] = m
spec.loader.exec_module(m)
print("  SW_FM_PROFILE_FEATURE=%d SW_FM_WELD_MEMBER_FEAT=%d SW_FM_MATE_PROFILE_CENTER=%d"
      % (m.SW_FM_PROFILE_FEATURE, m.SW_FM_WELD_MEMBER_FEAT, m.SW_FM_MATE_PROFILE_CENTER))
for f in ("configure_member_profile","create_weld_member","create_profile_center_mate",
          "configure_split_member","create_cut_list","create_sub_weld_folder"):
    print("  %-28s %s" % (f, inspect.signature(getattr(m, f))))
