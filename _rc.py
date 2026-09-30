import sys, types, io, json, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = r"C:\swprojects\sw-skill-fork"
sbs = types.ModuleType("sync_bundled_skill")
sbs.collect_runtime_files = lambda root: []
sys.modules["sync_bundled_skill"] = sbs
spec = importlib.util.spec_from_file_location("rc", R + r"\scripts\release_check.py")
m = importlib.util.module_from_spec(spec); sys.modules["rc"] = m
spec.loader.exec_module(m)
print("  必需文件清单:", len(m.REQUIRED_ABILITY_FILES), "项")
print("  git 可用:", m._git_available())
r = m._run_provenance_gate()
print("  门禁结果: status=%s anchor=%s" % (r.get("status"), r.get("anchor")))
print("  输出尾:", (r.get("output") or r.get("reason") or "")[-120:].replace("\n"," | "))
