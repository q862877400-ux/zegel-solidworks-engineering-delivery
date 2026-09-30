// 纯原生 IDispatch::Invoke 探针 —— 完全绕开 CLR 封送
// 目标：ICWLoadsAndRestraintsManager::AddRestraint (DispId=3)
using System;
using System.Runtime.InteropServices;
using System.Reflection;
using System.Text;

public static class RawInvoke
{
    // ---- IDispatch vtable ----
    // QueryInterface(0) AddRef(1) Release(2) GetTypeInfoCount(3) GetTypeInfo(4) GetIDsOfNames(5) Invoke(6)
    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    delegate uint QI([MarshalAs(UnmanagedType.Interface)] object self, ref Guid iid, out IntPtr ppv);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    delegate uint AddRef([MarshalAs(UnmanagedType.Interface)] object self);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    delegate uint Release([MarshalAs(UnmanagedType.Interface)] object self);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    delegate uint GetTypeInfoCount([MarshalAs(UnmanagedType.Interface)] object self, out uint n);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    delegate uint GetTypeInfo([MarshalAs(UnmanagedType.Interface)] object self, uint iTInfo, uint lcid, [MarshalAs(UnmanagedType.Interface)] out object ppTI);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    delegate uint GetIDsOfNames([MarshalAs(UnmanagedType.Interface)] object self, [MarshalAs(UnmanagedType.LPArray, ArraySubType = UnmanagedType.LPStr)] string[] rgszNames,
                                uint cNames, int lcid, out int[] rgDispId);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    delegate uint Invoke([MarshalAs(UnmanagedType.Interface)] object self, int dispIdMember, ref Guid riid,
                         int lcid, int wFlags, IntPtr pDispParams, IntPtr pVarResult,
                         IntPtr pExcepInfo, out int puArgErr);

    // ---- oleaut32 ----
    [DllImport("oleaut32.dll")]
    static extern IntPtr SafeArrayCreateVector(ushort vt, ulong l, ulong ulElems);
    [DllImport("oleaut32.dll")]
    static extern uint SafeArrayPutElement(IntPtr psa, IntPtr rgk, IntPtr pv);
    [DllImport("oleaut32.dll")]
    static extern int SafeArrayAccessData(IntPtr psa, out int ppvData);
    [DllImport("oleaut32.dll")]
    static extern void SafeArrayUnaccessData(IntPtr psa);
    [DllImport("oleaut32.dll")]
    static extern uint SafeArrayDestroy(IntPtr psa);
    [DllImport("oleaut32.dll")]
    static extern void VariantInit(IntPtr pvarg);
    [DllImport("oleaut32.dll")]
    static extern void VariantClear(IntPtr pvarg);
    [DllImport("oleaut32.dll")]
    static extern void VariantCopy(IntPtr pvDest, IntPtr pvSrc);
    [DllImport("oleaut32.dll")]
    static extern int VariantCopyInd(IntPtr pvarg, IntPtr pvarSrc);

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
    static extern IntPtr LoadLibraryW(string f);

    public const ushort VT_EMPTY = 0, VT_NULL = 1, VT_I2 = 2, VT_I4 = 3, VT_R4 = 4, VT_R8 = 5,
                      VT_BSTR = 8, VT_DISPATCH = 9, VT_BOOL = 11, VT_VARIANT = 12, VT_UNKNOWN = 13, VT_UI1 = 17;
    public const ushort VT_ARRAY = 0x2000, VT_BYREF = 0x4000;

    public static void AddDllDir(string dir) { LoadLibraryW(dir); }

    /// <summary>取 IDispatch* 指针（真正的裸指针，绕开所有 RCW 类型信息）</summary>
    public static IntPtr GetIDispatch(object comObject)
    {
        IntPtr pUnk = Marshal.GetIUnknownForObject(comObject);
        if (pUnk == IntPtr.Zero) return IntPtr.Zero;
        Guid iid = new Guid("00020400-0000-0000-C000-000000000046");
        IntPtr p;
        // 不用 Marshal.QueryInterface：它的 ref/in 重载在不同编译器下签名不同
        // （.NET Framework 的 csc 要 ref，Core 的 csc 要 in；本项目里
        //  #if NETCOREAPP 不生效）。直接走 vtable[0] 手工 QI。
        int hr = ManualQI(pUnk, iid, out p);
        Marshal.Release(pUnk);
        return hr == 0 ? p : IntPtr.Zero;
    }

    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    delegate int QIraw(IntPtr self, IntPtr riid, out IntPtr ppv);

    static int ManualQI(IntPtr self, Guid iid, out IntPtr ppv)
    {
        IntPtr vtbl = Marshal.ReadIntPtr(self);
        IntPtr fn = Marshal.ReadIntPtr(vtbl, 0);
        var f = (QIraw)Marshal.GetDelegateForFunctionPointer(fn, typeof(QIraw));
        IntPtr pIid = Marshal.AllocHGlobal(16);
        try
        {
            Marshal.Copy(iid.ToByteArray(), 0, pIid, 16);
            return f(self, pIid, out ppv);
        }
        finally { Marshal.FreeHGlobal(pIid); }
    }

    static Delegate GetVtbl(IntPtr self, int index, Type t)
    {
        IntPtr vtbl = Marshal.ReadIntPtr(self);                 // vtable 指针
        IntPtr fn = Marshal.ReadIntPtr(vtbl, index * IntPtr.Size);
        return Marshal.GetDelegateForFunctionPointer(fn, t);
    }

    /// <summary>只做只读侦察：取 DispId、验证 vtable 指针，不发任何 Invoke。
    /// 用来在可能崩进程的路径上先确认前提成立。</summary>
    public static string Recon(object lrm, object faceComObject)
    {
        var sb = new StringBuilder();
        // 第一步只做最安全的事：取 IDispatch*。
        // 读 vtable / GetIDsOfNames 都会 dereference 裸指针，一旦对象不是标准
        // COM 对象就会直接 AccessViolation（已实测崩服务），所以分步来。
        IntPtr pUnkLrm = Marshal.GetIUnknownForObject(lrm);
        IntPtr pUnkFace = Marshal.GetIUnknownForObject(faceComObject);
        sb.Append("IUnknown*(lrm)=").Append(pUnkLrm)
          .Append(" IUnknown*(face)=").Append(pUnkFace);
        if (pUnkLrm == IntPtr.Zero || pUnkFace == IntPtr.Zero) return sb.ToString();

        IntPtr pDispLrm = GetIDispatch(lrm);
        IntPtr pDispFace = GetIDispatch(faceComObject);
        sb.Append(" IDispatch*(lrm)=").Append(pDispLrm)
          .Append(" IDispatch*(face)=").Append(pDispFace);
        if (pDispLrm == IntPtr.Zero) { sb.Append(" lrm QI->IDispatch 失败"); return sb.ToString(); }

        // vtable 读取：只比对指针是否非零，不调任何函数
        IntPtr vtbl = Marshal.ReadIntPtr(pDispLrm);
        sb.Append(" vtable=").Append(vtbl);
        if (vtbl != IntPtr.Zero)
        {
            IntPtr f0 = Marshal.ReadIntPtr(vtbl, 0);
            IntPtr f6 = Marshal.ReadIntPtr(vtbl, 6 * IntPtr.Size);
            sb.Append(" vtbl[0](QI)=").Append(f0).Append(" vtbl[6](Invoke)=").Append(f6);
        }
        return sb.ToString();
    }

    /// <summary>用名字拿 DispId（比硬编码 3 更稳）</summary>
    public static int GetDispId(object comObject, string name, out uint hrOut)
    {
        IntPtr p = GetIDispatch(comObject);
        if (p == IntPtr.Zero) { hrOut = 0x80004005; return -1; }
        var f = (GetIDsOfNames)GetVtbl(p, 5, typeof(GetIDsOfNames));
        int[] ids = new int[1];
        uint hr = f(comObject, new string[] { name }, 1, 0, out ids);
        hrOut = hr;
        return ids[0];
    }

    /// <summary>建 SAFEARRAY(VT_DISPATCH) 变体</summary>
    public static IntPtr MakeArrayVariant(IntPtr[] dispPtrs, out IntPtr psaOut)
    {
        psaOut = IntPtr.Zero;
        if (dispPtrs == null || dispPtrs.Length == 0) return IntPtr.Zero;
        IntPtr psa = SafeArrayCreateVector(VT_DISPATCH, 0, (ulong)dispPtrs.Length);
        if (psa == IntPtr.Zero) return IntPtr.Zero;
        for (int i = 0; i < dispPtrs.Length; i++)
        {
            IntPtr idx = Marshal.AllocHGlobal(sizeof(int));
            try
            {
                Marshal.WriteInt32(idx, 0, i);
                uint hr = SafeArrayPutElement(psa, idx, dispPtrs[i]);
                if (hr != 0) { SafeArrayDestroy(psa); return IntPtr.Zero; }
            }
            finally { Marshal.FreeHGlobal(idx); }
        }
        psaOut = psa;
        IntPtr pv = Marshal.AllocCoTaskMem(24);
        VariantInit(pv);
        Marshal.WriteInt16(pv, 0, (short)(VT_ARRAY | VT_DISPATCH));
        Marshal.WriteIntPtr(pv, 8, psa);
        return pv;
    }

    public static IntPtr MakeEmptyVariant()
    {
        IntPtr pv = Marshal.AllocCoTaskMem(24);
        VariantInit(pv);
        Marshal.WriteInt16(pv, 0, (short)VT_EMPTY);
        return pv;
    }

    /// <summary>24 字节 VARIANT 按位复制（x64 布局 vt@0 / union@8）。不 AddRef。</summary>
    static void CopyVariant(IntPtr dest, IntPtr src)
    {
        for (int off = 0; off < 24; off += 8)
            Marshal.WriteInt64(dest + off, Marshal.ReadInt64(src + off));
    }

    public static IntPtr MakeI4Variant(int v)
    {
        IntPtr pv = Marshal.AllocCoTaskMem(24);
        VariantInit(pv);
        Marshal.WriteInt16(pv, 0, (short)VT_I4);
        Marshal.WriteInt32(pv, 8, v);
        return pv;
    }

    /// <summary>AddRestraint 的完整手工调用。数组元素类型 elemVt 可选 VT_DISPATCH(9) / VT_UNKNOWN(13) / VT_VARIANT(12)</summary>
    public static string CallAddRestraint(object lrm, object[] faces, int restraintType, ushort elemVt, string mode, int wFlagsParam)
    {
        var sb = new StringBuilder();
        IntPtr pLrm = GetIDispatch(lrm);
        sb.AppendLine("  IDispatch*(lrm) = " + pLrm);
        if (pLrm == IntPtr.Zero) return sb.AppendLine("  lrm QI 失败").ToString();
        if (faces == null || faces.Length == 0) return sb.AppendLine("  没有几何").ToString();

        // 先把所有面转成 IDispatch*（任何一个失败就停下，不送半个数组进去）
        IntPtr[] dispPtrs = new IntPtr[faces.Length];
        for (int i = 0; i < faces.Length; i++)
        {
            dispPtrs[i] = GetIDispatch(faces[i]);
            sb.AppendLine("  IDispatch*(face[" + i + "]) = " + dispPtrs[i]);
            if (dispPtrs[i] == IntPtr.Zero) return sb.AppendLine("  face[" + i + "] QI 失败").ToString();
        }

        // 1) 元素指针按 elemVt 摆进 SAFEARRAY
        IntPtr psa = IntPtr.Zero;
        IntPtr vArray = IntPtr.Zero;

        if (elemVt == VT_VARIANT)
        {
            // SAFEARRAY(VT_VARIANT)：每个元素是【24 字节的 VARIANT】（x64），
            // 不是 8 字节指针 —— 之前按 8 字节布局写就是这个分支崩掉的原因。
            // VB 的 `Dim myArray()` 就是 Variant 数组，VB 运行时封的正是这个。
            // 元素 VARIANT 布局：vt@0(2) rsv@2(6) union@8(16)，pdispVal 在 @8
            IntPtr psaV = SafeArrayCreateVector(VT_VARIANT, 0, (ulong)dispPtrs.Length);
            if (psaV == IntPtr.Zero) return sb.AppendLine("  SAFEARRAY(VT_VARIANT) 创建失败").ToString();
            int pvD;
            int hrA2 = SafeArrayAccessData(psaV, out pvD);
            if (hrA2 < 0 || pvD == 0) { SafeArrayDestroy(psaV); return sb.AppendLine("  AccessData 失败").ToString(); }
            IntPtr pvD2 = new IntPtr(pvD);
            const int ELEM = 24;                       // 每个元素 24 字节 VARIANT (x64)
            for (int i = 0; i < dispPtrs.Length; i++)
            {
                IntPtr el = pvD2 + i * ELEM;
                VariantInit(el);
                Marshal.WriteInt16(el, 0, (short)VT_DISPATCH);
                Marshal.WriteIntPtr(el + 8, dispPtrs[i]);
            }
            sb.AppendLine("  SAFEARRAY(VT_VARIANT) n=" + dispPtrs.Length
                        + " 元素=24B VARIANT(vt=VT_DISPATCH) pvData=" + pvD2);
            psa = psaV;
            vArray = Marshal.AllocCoTaskMem(24);
            VariantInit(vArray);
            Marshal.WriteInt16(vArray, 0, (short)(VT_ARRAY | VT_VARIANT));   // 0x200C
            Marshal.WriteIntPtr(vArray, 8, psa);
        }
        else
        {
            // SAFEARRAY(VT_DISPATCH) 或 (VT_UNKNOWN)
            ushort outer = elemVt == VT_DISPATCH ? VT_DISPATCH : VT_UNKNOWN;
            // ⚠ SafeArrayCreateVector 建的是【惰性】数组：此时 pvData 可能还是 NULL
            // （实测本机就是这样），必须 SafeArrayAccessData 把它真正分配出来。
            psa = SafeArrayCreateVector(outer, 0, (ulong)dispPtrs.Length);
            if (psa == IntPtr.Zero) return sb.AppendLine("  SafeArrayCreateVector 失败").ToString();
            int pvDataRaw;
            int hrA = SafeArrayAccessData(psa, out pvDataRaw);
            IntPtr pvDataPtr = new IntPtr(pvDataRaw);
            sb.AppendLine("  SafeArrayCreateVector(0x" + outer.ToString("X") + ", n=" + dispPtrs.Length
                          + ") + AccessData hr=" + hrA + " pvData=" + pvDataPtr);
            if (hrA < 0 || pvDataPtr == IntPtr.Zero) { SafeArrayDestroy(psa); return sb.ToString(); }
            // 元素是 8 字节指针，布局已知，直接写，避开 PutElement 的解引用风险
            for (int i = 0; i < dispPtrs.Length; i++)
                Marshal.WriteInt64(pvDataPtr + i * 8, dispPtrs[i].ToInt64());
            vArray = Marshal.AllocCoTaskMem(24);
            VariantInit(vArray);
            Marshal.WriteInt16(vArray, 0, (short)(VT_ARRAY | outer));
            Marshal.WriteIntPtr(vArray, 8, psa);
        }

        // 2) RefGeom：Nothing(VT_EMPTY) 或 NULL(VT_NULL)，取决于 mode
        IntPtr vRef = Marshal.AllocCoTaskMem(24);
        VariantInit(vRef);
        Marshal.WriteInt16(vRef, 0, (short)(mode == "null" ? VT_NULL : VT_EMPTY));

        // 3) ErrorCode：先按【普通 VT_I4】传（不是 byref）。
        //    byref 结果参数在 COM 里走 pVarResult / 或需要 VT_I4|VT_BYREF 指向调用方缓冲区，
        //    （下方已改用正确的 VT_I4|VT_BYREF）

        IntPtr vType = MakeI4Variant(restraintType);

        // ErrorCode 反射确认是 Int32&[out] ⇒ COM 里必须是 VT_I4|VT_BYREF，
        // 指向调用方缓冲区。之前为避崩改成了普通 VT_I4（按值），那本身就是错的形态 ——
        // cosworks 收到的是"值"而不是"可写回的引用"，E_INVALIDARG 完全说得通。
        // 之前 byref 版本崩的原因是 SAFEARRAY 惰性分配（pvData=NULL），现已用
        // AccessData 修掉，可以安全用 byref 了。
        IntPtr errCell = Marshal.AllocHGlobal(sizeof(int));
        Marshal.WriteInt32(errCell, 0, 0x7FFFFFFF);      // 哨兵：调用后若被写回，说明 byref 生效
        IntPtr vErr = Marshal.AllocCoTaskMem(24);
        VariantInit(vErr);
        Marshal.WriteInt16(vErr, 0, (short)(VT_I4 | VT_BYREF));
        Marshal.WriteIntPtr(vErr, 8, errCell);

        // 4) DISPPARAMS —— 【按声明顺序】填：rgvarg[0] = 第一个参数
        //    VARIANT x64 = 24 字节：vt@0(2) + rsv@2(6) + union@8(16)
        //    用 Marshal.Copy 而不是 VariantCopy —— 后者会 AddRef 源里的指针元素，
        //    在我们手工构造的数组上可能触发意料外的解引用。
        IntPtr rgvarg = Marshal.AllocCoTaskMem(4 * 24);
        CopyVariant(rgvarg + 0, vType);      // NRestraintType
        CopyVariant(rgvarg + 24, vArray);    // DispArray
        CopyVariant(rgvarg + 48, vRef);      // RefGeom
        CopyVariant(rgvarg + 72, vErr);      // ErrorCode

        IntPtr pars = Marshal.AllocCoTaskMem(20);
        Marshal.WriteIntPtr(pars, 0, rgvarg);
        Marshal.WriteIntPtr(pars, 8, IntPtr.Zero);
        Marshal.WriteInt32(pars, 16, 4);

        IntPtr pVarResult = Marshal.AllocCoTaskMem(24);
        VariantInit(pVarResult);
        IntPtr pExcep = IntPtr.Zero;
        int argErr = 0;

        var inv = (Invoke)GetVtbl(pLrm, 6, typeof(Invoke));
        Guid iidNull = Guid.Empty;                 // riid = IID_NULL ⇒ 取返回值
        // wFlags：DISPATCH_METHOD = 1（标准方法调用）。之前用 0(INVOKE_FUNC) 也拿到过
        // E_INVALIDARG，但 cosworks 可能严格检查标志位，所以做成可调。
        int wFlags = wFlagsParam;
        uint hr = inv(lrm, 3, ref iidNull, 0, wFlags, pars, pVarResult, pExcep, out argErr);

        sb.AppendLine("  Invoke(DispId=3, wFlags=" + wFlags + ") hr=0x" + hr.ToString("X8")
                    + " argErr=" + argErr);
        sb.AppendLine("  ErrorCode(byref 写回) = " + Marshal.ReadInt32(errCell, 0)
                    + (Marshal.ReadInt32(errCell, 0) != 0x7FFFFFFF ? "   *** 被写回 ⇒ byref 生效 ***" : "   (未被写回)"));
        short rvt = Marshal.ReadInt16(pVarResult, 0);
        sb.AppendLine("  pVarResult.vt = 0x" + rvt.ToString("X4")
                    + (rvt == VT_DISPATCH ? "  *** 返回了 COM 对象 ⇒ 调用成功 ***"
                     : rvt == VT_EMPTY ? " (无返回值)" : " (其它)"));
        if (hr == 0 && rvt == VT_DISPATCH)
            sb.AppendLine("  返回指针 = " + Marshal.ReadIntPtr(pVarResult, 8));

        // 清理：⚠ 不用 VariantClear(rgvarg) —— 里面的指针是我们 memcpy 进去的
        // （没有 AddRef），VariantClear 会 Release 它们 ⇒ 二次释放 ⇒ 崩。
        // 直接释放内存；psa 由 SafeArrayDestroy 负责（它会 Release 元素）。
        Marshal.FreeCoTaskMem(rgvarg); Marshal.FreeCoTaskMem(pars);
        VariantClear(pVarResult);
        Marshal.FreeCoTaskMem(pVarResult);
        Marshal.FreeCoTaskMem(vType); Marshal.FreeCoTaskMem(vArray);
        Marshal.FreeCoTaskMem(vRef); Marshal.FreeCoTaskMem(vErr);
        Marshal.FreeHGlobal(errCell);
        SafeArrayUnaccessData(psa);
        SafeArrayDestroy(psa);
        return sb.ToString();
    }
}

