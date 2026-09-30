import numpy as np, matplotlib, math
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

fig=plt.figure(figsize=(7,6)); ax=fig.add_subplot(111,projection='3d')
def box(x0,x1,y0,y1,z0,z1,c):
    # vertices
    v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
       (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    E=[(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
    for i,j in E:
        ax.plot(*zip(v[i],v[j]),color=c,lw=1.2)

mm=1e-3  # mm -> m for plotting only (visual)
# vertical plate x[-32.5,32.5] y[0,68] z[0,3]
box(-32.5*mm,32.5*mm,0,68*mm,0,3*mm,'#1f77b4')
# base x[-32.5,32.5] y[0,3] z[0,68]
box(-32.5*mm,32.5*mm,0,3*mm,0,68*mm,'#2ca02c')
# pilot hole O38.2 on vertical face z=3, center y=40
th=np.linspace(0,2*np.pi,80)
ax.plot(19.1*mm*np.cos(th),40*mm+19.1*mm*np.sin(th),3*mm,'r-',lw=1.4)
# 4 mounting holes O5.2 on 47x47
for sx in (-23.5,23.5):
  for sy in (-23.5,23.5):
    ax.plot(2.6*mm*np.cos(th)+sx*mm,40*mm+2.6*mm*np.sin(th)+sy*mm,3*mm,'r-',lw=1)
# 2 slots on base top y=3, centers x=+-20, z 12..58
for cx in (-20,20):
    # slot long axis = z (global z 12..58), width x (+-2.1)
    pz=np.linspace(12*mm,58*mm,40)
    ax.plot((-2.1*mm+cx*mm)+0*pz,3*mm*np.ones_like(pz),pz,'m-',lw=1.2)
    ax.plot((2.1*mm+cx*mm)+0*pz,3*mm*np.ones_like(pz),pz,'m-',lw=1.2)
    arcz=np.linspace(0,np.pi,30)
    ax.plot(cx*mm+2.1*mm*np.cos(arcz),3*mm+0*pz[:30],(12*mm+2.1*mm)+2.1*mm*np.sin(arcz),'m-',lw=1.2)
    ax.plot(cx*mm+2.1*mm*np.cos(arcz),3*mm+0*pz[:30],(58*mm-2.1*mm)+2.1*mm*np.sin(arcz),'m-',lw=1.2)

ax.set_box_aspect((1,1,1)); ax.set_xlabel('X (mm->m)');ax.set_ylabel('Y');ax.set_zlabel('Z')
ax.set_title('57 motor L-bracket  (blue=vertical flange, green=base, red=holes, magenta=slots)')
ax.view_init(elev=25,azim=-60)
plt.tight_layout(); plt.savefig('C:/Users/Zegel/57_motor_bracket_preview.png',dpi=120)
print('saved')
