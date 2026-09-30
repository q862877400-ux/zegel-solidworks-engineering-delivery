// 直接 P/Invoke oleaut32 构造 SAFEARRAY + VARIANT，绕开 CLR 全部封送规则。
// 用途：ICWLoadsAndRestraintsManager.AddRestraint 的 DispArray 参数
//       interop 声明为 [MarshalAs(UnmanagedType.Struct)]，托管 object[] 无法满足。
using System;
using System.Runtime.InteropServices;

public static class RawDispatch
{
    // ---- oleaut32 ----
    [DllImport("oleaut32.dll", CharSet = CharSet.Unicode)]
    public static extern IntPtr SysAllocStringLen(string s, uint len);
    [DllImport("oleaut32.dll")]
    public static extern void SysFreeString(IntPtr bstr);
    [DllImport("oleaut32.dll")]
    public static extern IntPtr SafeArrayCreate(ushort vt, ushort cDims, IntPtr rgsafearray);
    [DllImport("oleaut32.dll")]
    public static extern IntPtr SafeArrayCreateVector(ushort vt, ulong l, ulong ulElems);
    [DllImport("oleaut32.dll")]
    public static extern uint SafeArrayPutElement(IntPtr psa, IntPtr rgk, IntPtr pv);
    [DllImport("oleaut32.dll")]
    public static extern uint SafeArrayGetElement(IntPtr psa, IntPtr rgk, IntPtr pv);
    [DllImport("oleaut32.dll")]
    public static extern uint SafeArrayGetUBound(IntPtr psa, int lBound, out uint pUBound);
    [DllImport("oleaut32.dll")]
    public static extern uint SafeArrayGetLBound(IntPtr psa, int lBound, out int pLBound);
    [DllImport("oleaut32.dll")]
    public static extern uint SafeArrayDestroy(IntPtr psa);
    [DllImport("oleaut32.dll")]
    public static extern void VariantInit(IntPtr pvarg);
    [DllImport("oleaut32.dll")]
    public static extern void VariantClear(IntPtr pvarg);
    [DllImport("oleaut32.dll")]
    public static extern void VariantCopy(IntPtr pvDest, IntPtr pvSrc);
    [DllImport("oleaut32.dll")]
    public static extern void SafeArrayDestroyData(IntPtr psa);
    [DllImport("oleaut32.dll")]
    public static extern void SafeArrayDestroyDescriptor(IntPtr psa);

    // ---- VARIANT constants ----
    public const ushort VT_EMPTY = 0, VT_NULL = 1, VT_I2 = 2, VT_I4 = 3,
                      VT_R4 = 4, VT_R8 = 5, VT_BSTR = 8, VT_DISPATCH = 9,
                      VT_BOOL = 11, VT_VARIANT = 12, VT_UNKNOWN = 13, VT_I8 = 20;
    public const ushort VT_ARRAY = 0x2000;
    public const ushort VT_BYREF = 0x4000;

    // 分配一块 x64 大小的 VARIANT
    public static IntPtr NewVariant() => Marshal.AllocCoTaskMem(24);

    // 写 VT_I4
    public static void SetVariantI4(IntPtr pVar, int v)
    {
        VariantInit(pVar);
        Marshal.WriteInt16(pVar, 0, (short)VT_I4);
        Marshal.WriteInt32(pVar, 8, v);
    }

    // 写 VT_DISPATCH / VT_UNKNOWN
    public static void SetVariantPtr(IntPtr pVar, ushort vt, IntPtr p)
    {
        VariantInit(pVar);
        Marshal.WriteInt16(pVar, 0, (short)vt);
        Marshal.WriteIntPtr(pVar, 8, p);
    }

    // 把一个 SAFEARRAY* 塞进 VARIANT（VARIANT union 在 x64 偏移 8）
    // ⚠ 元素是 VT_DISPATCH ⇒ 外层必须是 VT_ARRAY|VT_DISPATCH = 0x2009（不是 0x200C）
    public static void SetVariantSafeArray(IntPtr pVar, IntPtr psa)
    {
        VariantInit(pVar);
        Marshal.WriteInt16(pVar, 0, (short)(VT_ARRAY | VT_DISPATCH));
        Marshal.WriteIntPtr(pVar, 8, psa);
    }

    // VT_EMPTY —— 对应 VB 的 Nothing。C# 的 null 会被 CLR 封成 VT_DISPATCH，
    // 而且实测会让服务永久阻塞，所以 RefGeom 必须手工构造这个。
    public static void SetVariantEmpty(IntPtr pVar)
    {
        VariantInit(pVar);
        Marshal.WriteInt16(pVar, 0, (short)VT_EMPTY);
    }

    /// <summary>按【声明顺序】打包 AddRestraint 的 4 个参数成 DISPPARAMS。
    ///
    /// ⚠⚠ 顺序是声明顺序，不是逆序！COM 内部用 rgvarg 反向索引取参，
    ///    但调用方按声明顺序填 rgvarg[0..n] 即可（CLR 自己也是这么做的）。
    ///    按逆序填会变成 AddRestraint(ErrorCode, RefGeom, DispArray, NRestraintType)，
    ///    症状与当前失败完全一样，但会把排查方向带偏。
    ///
    /// 调用方用完必须 FreeDispParams(pars)。</summary>
    public static IntPtr BuildAddRestraintParams(int restraintType, IntPtr dispArrayVariant, out IntPtr errorCodeCell)
    {
        IntPtr rgvarg = Marshal.AllocCoTaskMem(4 * 24);   // 每个 VARIANT 24 字节（x64）
        IntPtr vType  = rgvarg;          // [0] NRestraintType
        IntPtr vArray = rgvarg + 24;     // [1] DispArray
        IntPtr vRef   = rgvarg + 48;     // [2] RefGeom
        IntPtr vErr   = rgvarg + 72;     // [3] ErrorCode (out int)

        SetVariantI4(vType, restraintType);               // 0 = swsRestraintTypeFixed
        if (dispArrayVariant != IntPtr.Zero)
            Marshal.WriteInt64(vArray, 0, Marshal.ReadInt64(dispArrayVariant, 0));
        else
            SetVariantEmpty(vArray);
        SetVariantEmpty(vRef);                            // VB 的 Nothing

        // out int：VARIANT 里放 VT_I4|VT_BYREF，union 指向调用方缓冲区
        IntPtr cell = Marshal.AllocHGlobal(sizeof(int));
        errorCodeCell = cell;
        Marshal.WriteInt32(cell, 0, 0);
        VariantInit(vErr);
        Marshal.WriteInt16(vErr, 0, (short)(VT_I4 | VT_BYREF));
        Marshal.WriteIntPtr(vErr, 8, cell);

        IntPtr pars = Marshal.AllocCoTaskMem(20);         // DISPPARAMS 20 字节
        Marshal.WriteIntPtr(pars, 0, rgvarg);
        Marshal.WriteIntPtr(pars, 8, IntPtr.Zero);         // rgdispidNamedArgs
        Marshal.WriteInt32(pars, 16, 4);                  // cArgs
        return pars;                                       // DispId=3 → Invoke 时传 -1 走 GetIDsOfNames
    }

    public static void FreeDispParams(IntPtr pars)
    {
        if (pars == IntPtr.Zero) return;
        IntPtr rgvarg = Marshal.ReadIntPtr(pars, 0);
        if (rgvarg != IntPtr.Zero) Marshal.FreeCoTaskMem(rgvarg);
        Marshal.FreeCoTaskMem(pars);
    }

    public static int ReadErrorCode(IntPtr cell)    {
        if (cell == IntPtr.Zero) return -999;
        int v = Marshal.ReadInt32(cell, 0);
        Marshal.FreeHGlobal(cell);
        return v;
    }

    /// <summary>用 IUnknown 指针数组构造 SAFEARRAY(VT_UNKNOWN)。
    /// 返回 SAFEARRAY*，失败返回 IntPtr.Zero。</summary>
    public static IntPtr MakeSafeArrayOfUnknown(IntPtr[] unkPtrs)
    {
        if (unkPtrs == null || unkPtrs.Length == 0) return IntPtr.Zero;
        IntPtr psa = SafeArrayCreateVector(VT_UNKNOWN, 0, (ulong)unkPtrs.Length);
        if (psa == IntPtr.Zero) return IntPtr.Zero;
        for (int i = 0; i < unkPtrs.Length; i++)
        {
            IntPtr idx = Marshal.AllocHGlobal(sizeof(int));
            try
            {
                Marshal.WriteInt32(idx, 0, i);                       // 0-based
                uint hr = SafeArrayPutElement(psa, idx, unkPtrs[i]);
                if (hr != 0) { SafeArrayDestroy(psa); return IntPtr.Zero; }
            }
            finally { Marshal.FreeHGlobal(idx); }
        }
        return psa;
    }

    /// <summary>用 IDispatch 指针数组构造 SAFEARRAY(VT_DISPATCH)。
    /// 元素类型用 VT_DISPATCH（不是 VT_UNKNOWN）——官方 VB 示例里 varArray 的元素
    /// 就是 Face2/IDispatch，VB 运行时封成 SAFEARRAY(VT_DISPATCH)。
    /// 返回 SAFEARRAY*，失败返回 IntPtr.Zero。
    /// ⚠ 元素会被 AddRef：只能传真实 COM 对象的 IDispatch*，传假指针直接
    ///   AccessViolation(0xC0000005) 崩进程（已实测）。</summary>
    public static IntPtr MakeSafeArrayOfDispatch(IntPtr[] dispPtrs)
    {
        if (dispPtrs == null || dispPtrs.Length == 0) return IntPtr.Zero;
        IntPtr psa = SafeArrayCreateVector(VT_DISPATCH, 0, (ulong)dispPtrs.Length);
        if (psa == IntPtr.Zero) return IntPtr.Zero;
        for (int i = 0; i < dispPtrs.Length; i++)
        {
            IntPtr idx = Marshal.AllocHGlobal(sizeof(int));
            try
            {
                Marshal.WriteInt32(idx, 0, i);                       // 0-based
                uint hr = SafeArrayPutElement(psa, idx, dispPtrs[i]);
                if (hr != 0) { SafeArrayDestroy(psa); return IntPtr.Zero; }
            }
            finally { Marshal.FreeHGlobal(idx); }
        }
        return psa;
    }

    /// <summary>取 IDispatch*（cosworks 在 VB 示例里收的是 IDispatch，不是 IUnknown）。</summary>
    public static IntPtr GetDispatchPtr(object comObject)
    {
        if (comObject == null) return IntPtr.Zero;
        IntPtr pUnk = Marshal.GetIUnknownForObject(comObject);
        if (pUnk == IntPtr.Zero) return IntPtr.Zero;
        Guid iid = new Guid("00020400-0000-0000-C000-000000000046");   // IID_IDispatch
        IntPtr pDisp;
        int hr = Marshal.QueryInterface(pUnk, in iid, out pDisp);
        Marshal.Release(pUnk);
        return hr == 0 ? pDisp : IntPtr.Zero;
    }

    /// <summary>把 SAFEARRAY(VT_DISPATCH) 塞进一个 VARIANT。
    /// 外层 vt 必须是 VT_ARRAY|VT_DISPATCH = 0x2009，与元素类型一致
    /// （不是 0x200C，那是 VT_ARRAY|VT_VARIANT）。
    /// 返回 VARIANT 指针（调用方负责 VariantClear + Free）。</summary>
    public static IntPtr MakeVariantWithArray(IntPtr psa)
    {
        IntPtr pv = NewVariant();
        SetVariantSafeArray(pv, psa);
        return pv;
    }

    public static void Describe(IntPtr psa, System.Text.StringBuilder sb)
    {
        if (psa == IntPtr.Zero) { sb.AppendLine("psa = NULL"); return; }
        uint ub = 0; int lb = 0;
        uint h1 = SafeArrayGetUBound(psa, 1, out ub);
        uint h2 = SafeArrayGetLBound(psa, 1, out lb);
        short cDims = Marshal.ReadInt16(psa, 0);
        short fFeat = Marshal.ReadInt16(psa, 2);
        long pvData = Marshal.ReadInt64(psa, 8);
        sb.AppendLine("SAFEARRAY: cDims=" + cDims + " fFeatures=0x" + fFeat.ToString("X4")
                    + " LBound=" + lb + " UBound=" + ub + " pvData=" + new IntPtr(pvData)
                    + "  (hrUB=" + h1 + " hrLB=" + h2 + ")");
    }
}

