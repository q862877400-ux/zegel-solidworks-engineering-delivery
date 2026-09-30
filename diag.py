import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L
warnings.filterwarnings("ignore")
h, w = L.connect()
print("已连接")
# 1) container_rect 单独耗时
for i in range(2):
    t=time.time(); cr = L.container_rect(w); print("container_rect: %.2fs -> %s" % (time.time()-t, cr))
# 2) descendants() 一次耗时 + 节点数
for i in range(2):
    t=time.time()
    try:
        allc = list(w.descendants())
        n=len(allc)
    except Exception as e:
        n=str(e)[:40]
    print("descendants(): %.2fs  节点 %s" % (time.time()-t, n))
# 3) 瓶颈拆解：只读前 50 个 vs 全部
t=time.time()
n=0
for c in w.descendants():
    n+=1
    if n>=50: break
print("只取前 50 个: %.2fs" % (time.time()-t))