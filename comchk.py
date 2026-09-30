import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
warnings.filterwarnings("ignore")
import win32com.client as wc
try:
    sw = wc.GetActiveObject("SldWorks.Application")
    print("✓ 连上 SolidWorks COM")
    print("  版本:", sw.RevisionNumber)
    # 只读几个成员
    try:
        print("  活动文档:", sw.ActiveDoc.GetTitle() if sw.ActiveDoc else "无")
    except Exception as e:
        print("  ActiveDoc 读取失败:", str(e)[:50])
    # 测试 12 个索引模块里的几个"应该能用"的成员
    import sw_api_sldworks as A
    print("  sldworks 索引: %d 族" % len(A.FAMILIES))
    # 试一个复杂点的：FeatureManager 是否存在
    doc = sw.ActiveDoc
    if doc:
        try:
            fm = doc.FeatureManager
            print("  FeatureManager:", "✓ 可访问" if fm else "✗ None")
        except Exception as e:
            print("  FeatureManager 异常:", str(e)[:50])
except Exception as e:
    print("✗ COM 连接失败:", str(e)[:80])