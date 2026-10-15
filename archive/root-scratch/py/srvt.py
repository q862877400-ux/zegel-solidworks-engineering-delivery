import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
warnings.filterwarnings("ignore")
for m in ("mcp","pydantic","win32com","comtypes","jsonschema"):
    try:
        __import__(m); print("  ✓ %s" % m)
    except Exception as e:
        print("  ✗ %s  %s" % (m, str(e)[:40]))
print()
try:
    import importlib.util as iu
    spec = iu.spec_from_file_location("srv", r"C:\swprojects\sw-skill-fork\mcp-server\server.py")
    mod = iu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print("  ✓ server.py 载入成功")
    tools = [n for n in dir(mod) if not n.startswith("_")]
    print("  顶层符号 %d 个" % len(tools))
except Exception as e:
    print("  ✗ server.py 载入失败: %s" % str(e)[:120])