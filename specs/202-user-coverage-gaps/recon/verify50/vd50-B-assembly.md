# vd50-B-assembly · 04-assembly 域「置信度=高」条目的复核

- **范围**：只核 `recon/audit-vs-official/` 里与 **04-assembly** 有关、且置信度为「**高**」的条目。
- **口径**：每条核两件事 —— ① 官方原文是否真在 `C:/swapi`（及 CHM 解包 `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\`）里；② 我们的原文是否真在 `scripts/sw_assembly.py` 里。
- **范围外**：B 档 #2/#3/#4 与 C 档 #8（置信度为「中」）**未核**。
- **纪律**：只读；未改仓内任何文件（只新建本文件）；不写行号（写原文片段）；两段原文缺一的不写。
- **源文件清单**（只这三份引用了 `scripts/sw_assembly.py`，全仓已核）：`audit-04-assembly-A.md` · `audit-04-assembly-B.md` · `audit-04-assembly-C.md`。

---

## 汇总表

| 条目 | 文件 | 官方原文在不在 | 我们的原文在不在 | 判定 |
|---|---|---|---|---|
| A #1 | `audit-04-assembly-A.md` | 在（三源一致） | 在 | **成立**（计数有出入，见下） |
| B #1 | `audit-04-assembly-B.md` | 在（成员页 + 两处官方例子） | 在 | **成立** |
| C #1 | `audit-04-assembly-C.md` | 在（`C:/swapi` + CHM 两源） | 在 | **成立** |
| C #2 | `audit-04-assembly-C.md` | 在（`C:/swapi` + CHM 两源） | 在 | **成立** |
| C #3 | `audit-04-assembly-C.md` | 在（`C:/swapi` + CHM 两源） | 在 | **成立** |
| C #4 | `audit-04-assembly-C.md` | 在（`C:/swapi` + CHM 两源） | 在 | **成立** |
| C #5 | `audit-04-assembly-C.md` | 在（`C:/swapi` + CHM 两源） | 在 | **成立** |
| C #6 | `audit-04-assembly-C.md` | 在（`C:/swapi` + CHM 两源） | 在 | **成立** |
| C #7 | `audit-04-assembly-C.md` | 在（`C:/swapi` + CHM 两源） | 在 | **成立** |

**核了 9 处（高置信度条目），对不上 0 处。**

---

## A #1 · `mate.Name = name` 赋了一个官方 `IMate2` 没有的成员

- **我们的原文**（`scripts/sw_assembly.py`）：

  ```
  mate = asm_model.AddMate5(
      int(mate_type),
      int(align),
      ...
      error_status,
  )
  ...
  if name:
      try:
          mate.Name = name
      except Exception:
          pass
  ```

- **官方的原文**（三源，均**无** `Name`）：

  - `C:\swapi\types\IMate2\` 目录 34 个 `.md`，**没有 `Name.md`**；`C:\swapi\types\IMate\` 目录**整体不存在**。
  - `C:\swapi\index\members_by_type.md` 的 `## SolidWorks.Interop.sldworks.IMate2` 段共 **33 条**成员行（15 property + 18 method），逐行为
    `Alignment` · `CanBeFlipped` · `DisplayDimension` · `DisplayDimension2` · `DistanceFirstArcCondition` · `DistanceSecondArcCondition` · `Flipped` · `HasLoadBearingFaces` · `HasTreatInterferenceAsShrinkFit` · `IsLoadBearingFacesBonded` · `LockMagneticMate` · `MateLoadReference` · `MaximumVariation` · `MinimumVariation` · `Type` · `ForceMisalignment` · `GetConcentricAlignmentType` · `GetCurrentMisalignedDeviation` · `GetForce` · `GetLinkedMate` · `GetMateEntityCount` · `GetMaximumMisalignedDeviation` · `GetSupplementalFaces` · `GetTorque` · `GetUseMisalignedDeviationDocumentProperty` · `IGetSupplementalFaces` · `MateEntity` · `RemoveMisalignment` · `SetConcentricAlignmentType` · `SetForce` · `SetMaximumMisalignedDeviation` · `SetTorque` · `SetUseMisalignedDeviationDocumentProperty`
    —— 全段无 `Name`、无 `set_Name`。
  - CHM `SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IMate2_members.html` 的 **Public Properties** 共 15 个，逐个为
    `Alignment`、`CanBeFlipped`、`DisplayDimension`、`DisplayDimension2`、`DistanceFirstArcCondition`、`DistanceSecondArcCondition`、`Flipped`、`HasLoadBearingFaces`、`HasTreatInterferenceAsShrinkFit`、`IsLoadBearingFacesBonded`、`LockMagneticMate`、`MateLoadReference`、`MaximumVariation`、`MinimumVariation`、`Type`
    —— 无 `Name`（该页共引用 33 个 `IMate2~*.html` 成员页，无一个名为 `Name`）。
  - 出厂类型库反射 `D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt` 的 `## IMate2` 段 36 行，首行 `Boolean ForceMisalignment()`、末行 `Void SetUseMisalignedDeviationDocumentProperty(Boolean)` —— 段内无 `Name`、无 `set_Name`。
  - **补一条官方依据**（本次新查到，条目未引用）：CHM `…IMate2.html` 的 Remarks 写明
    `To get the IMate2 object, you must first get it as a IFeature object and then use IFeature::GetSpecificFeature2 or QueryInterface to return the IMate2 interface.`
    ⇒ **`IMate2` 并不继承 `IFeature`**，`Name` 只能经 `IFeature` 拿到。

- **判定：成立** —— 官方三源一致没有 `IMate2.Name`，而我们确实对 `AddMate5` 的返回值赋了这个成员。
- **一句话依据**：三处官方成员表逐行可数、全无 `Name`，而仓内 `mate.Name = name` 确在 `try/except` 里对着 `AddMate5` 的返回值赋值。
- ★ **偏差（不影响本条判定，须记录）**：
  ① 条目写的 `members_by_type.md` 「40 条成员行 · 15 property + 25 method」实测是 **33 条 · 15 property + 18 method**；
  ② 「CHM Public Properties 表 16 行」但它只列了 15 个名字（表头行被算进了行数）；
  ③ 「`C:\swapi\types\IMate2\` 目录下 40 个 `.md`」实测 **34 个**（同一批的 C 档文件又写成 37 个）；
  ④ 「反射 `## IMate2` 段 34 行」实测 **36 行**。
  ⇒ **引用的是原文片段，不是数字**；数字四处都不准，**但「无 `Name`」这个结论三源都成立**。
- ⚠ **实际后果未核**：CHM Remarks 表明 `Mate` 子特征本体同时支持 `IFeature`，Python 迟到绑定按名字找 `Name` 时**可能仍能命中 `IFeature::Name`**；仓内又用 `try/except Exception: pass` 兜住 ⇒ 这条是**形参表层面的成员缺席**，**不等于「运行时一定失败」**（未实测，不下断言）。

---

## B #1 · `interference.Done()` 排在取结果之前

- **我们的原文**（`scripts/sw_assembly.py`，`get_interference_detection()` 内）：

  ```
  interference = asm_model.InterferenceDetectionManager
  interference.TreatSubAssembliesAsComponents = False
  interference.TreatCoincidenceAsInterference = False
  interference.Done()
  count = int(safe_get_com_member(interference, "GetInterferenceCount") or 0)
  ...
      _got = call_com_member(interference, "GetInterferences")
  ```

- **官方的原文**：

  - `C:\swapi\types\IInterferenceDetectionMgr\Done.md` —— `Stops the interference detection.`
  - `C:\swapi\types\IInterferenceDetectionMgr\GetInterferences.md` —— `Calculates and gets the interferences.`
  - `C:\swapi\types\IInterferenceDetectionMgr\GetInterferenceCount.md` —— `Calculates and gets the number of interferences.`，其 Remarks：`Call this method before calling [[IInterferenceDetectionMgr::IGetInterferences]] to determine the size of the array for the interferences.`
  - CHM `SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IInterferenceDetectionMgr~Done.html` —— `Stops the interference detection.`
  - `C:\swapi\examples\Run_Interference_Detection_Example_VB.md` 的调用序：
    `'Run interference detection` / `vInts = pIntMgr.GetInterferences` / `Debug.Print "Number of interferences: " & pIntMgr.GetInterferenceCount`
    …… 例尾才 `'Stop interference detection and close Interference Detection pane` / `'pIntMgr.Done`
  - `C:\swapi\examples\Run_Interference_Detection_Example_CSharp.md` 同序：`vInts = (object[])pIntMgr.GetInterferences();` / `Debug.Print("Number of interferences: " + pIntMgr.GetInterferenceCount());` …… 例尾 `//Stop interference detection and close Inteference Detection pane` / `//pIntMgr.Done();`

- **判定：成立** —— 官方两处例子的调用序一致为「先取结果、`Done()` 最后」，我们把「停止」放在了取结果之前。
- **一句话依据**：官方成员说明里 `GetInterferences` / `GetInterferenceCount` 自称 "Calculates and gets…"，而 `Done` 自称 "Stops the interference detection."，两处官方例子也都把 `Done` 放在末尾，仓内顺序与之相反。

---

## C #1 · `AddComponent4` 已被官方标 Obsolete

- **我们的原文**（`scripts/sw_assembly.py`，`_add_component4()` 内）：

  ```
  def _add_component4(asm_model, component_path, config_name, x, y, z):
      """调用 AddComponent4。"""
      return asm_model.AddComponent4(
          component_path,
          config_name or "",
          float(x),
          float(y),
          float(z),
      )
  ```

- **官方的原文**：

  - `C:\swapi\types\IAssemblyDoc\AddComponent4.md` —— `Obsolete. Superseded by [[IAssemblyDoc::AddComponent5]].`
  - CHM `SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IAssemblyDoc~AddComponent4.html` —— `Obsolete. Superseded by IAssemblyDoc::AddComponent5 .`

- **判定：成立** —— 官方两源逐字一致，且我们确在回退路径里直调它。
- **一句话依据**：`C:/swapi` 与 CHM 同页同句 `Obsolete. Superseded by IAssemblyDoc::AddComponent5`，仓内 `return asm_model.AddComponent4(` 逐字可搜。

---

## C #2 · `AddMate5` 已被官方标 Obsolete

- **我们的原文**（`scripts/sw_assembly.py`，`add_mate5_checked()` 内）：

  ```
  mate = asm_model.AddMate5(
      int(mate_type),
      int(align),
      ...
      error_status,
  )
  ```

- **官方的原文**：

  - `C:\swapi\types\IAssemblyDoc\AddMate5.md` —— `Obsolete. Superseded by [[IAssemblyDoc::CreateMate.]]`
  - CHM `SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IAssemblyDoc~AddMate5.html` —— `Obsolete. Superseded by  IAssemblyDoc::CreateMate. `

- **判定：成立** —— 官方两源一致标 Obsolete。
- **一句话依据**：官方点名后继 `IAssemblyDoc::CreateMate`，而仓内建配的唯一入口就是 `mate = asm_model.AddMate5(`。

---

## C #3 · `IEntity.Select2` 已被官方标 Obsolete

- **我们的原文**（`scripts/sw_assembly.py`，`select_entities_for_mate()` 内）：

  ```
  model.ClearSelection2(True)
  if not entity1.Select2(False, mark):
      raise RuntimeError("选择第一个 Mate 实体失败")
  if not entity2.Select2(True, mark):
      raise RuntimeError("选择第二个 Mate 实体失败")
  ```

- **官方的原文**：

  - `C:\swapi\types\IEntity\Select2.md` —— `Obsolete. Superseded by [[IEntity::Select4]].`
  - CHM `SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IEntity~Select2.html` —— `Obsolete. Superseded by IEntity::Select4 .`

- **判定：成立** —— 官方两源一致标 Obsolete。
- **一句话依据**：官方点名后继 `IEntity::Select4`，仓内两处 `Select2(False, mark)` / `Select2(True, mark)` 逐字可搜。

---

## C #4 · `IComponent2.SetTransformAndSolve2` 已被官方标 Obsolete

- **我们的原文**（`scripts/sw_assembly.py`，`apply_component_transform_x()` 内）：

  ```
  try:
      if component.SetTransformAndSolve2(transform):
          return True
  except Exception:
      pass
  ```

- **官方的原文**：

  - `C:\swapi\types\IComponent2\SetTransformAndSolve2.md` —— `Obsolete. Superseded by [[IComponent2::SetTransformAndSolve3]].`
  - CHM `SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IComponent2~SetTransformAndSolve2.html` —— `Obsolete. Superseded by IComponent2::SetTransformAndSolve3 .`

- **判定：成立** —— 官方两源一致标 Obsolete（且我们下一分支已用 `Transform2` 兜底）。
- **一句话依据**：官方点名后继 `SetTransformAndSolve3`，仓内 `if component.SetTransformAndSolve2(transform):` 逐字可搜。

---

## C #5 · `IModelDoc2.EditSuppress` 已被官方标 Obsolete

- **我们的原文**（`scripts/sw_assembly.py`，`suppress_component()` 内）：

  ```
  def suppress_component(asm_model, component_name):
      """压缩（隐藏）组件"""
      _select_by_id(asm_model.Extension, component_name, "COMPONENT")
      asm_model.EditSuppress()
  ```

- **官方的原文**：

  - `C:\swapi\types\IModelDoc2\EditSuppress.md` —— `Obsolete. Superseded [[IModelDoc2::EditSuppress2]].`（★ 官方这句**本来就没有 "by"**，条目照抄正确）
  - CHM `SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IModelDoc2~EditSuppress.html` —— `Obsolete. Superseded IModelDoc2::EditSuppress2 .`

- **判定：成立** —— 官方两源一致标 Obsolete。
- **一句话依据**：官方点名后继 `EditSuppress2`，仓内 `asm_model.EditSuppress()` 逐字可搜。

---

## C #6 · `IModelDoc2.EditUnsuppress` 已被官方标 Obsolete

- **我们的原文**（`scripts/sw_assembly.py`，`unsuppress_component()` 内）：

  ```
  def unsuppress_component(asm_model, component_name):
      """解压缩（显示）组件"""
      _select_by_id(asm_model.Extension, component_name, "COMPONENT")
      asm_model.EditUnsuppress()
  ```

- **官方的原文**：

  - `C:\swapi\types\IModelDoc2\EditUnsuppress.md` —— `Obsolete. Superseded by [[IModelDoc2::EditUnsuppress2]].`
  - CHM `SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IModelDoc2~EditUnsuppress.html` —— `Obsolete. Superseded by IModelDoc2::EditUnsuppress2 .`

- **判定：成立** —— 官方两源一致标 Obsolete。
- **一句话依据**：官方点名后继 `EditUnsuppress2`，仓内 `asm_model.EditUnsuppress()` 逐字可搜。

---

## C #7 · `IMateEntity2.ReferenceType` 已被官方标 Obsolete

- **我们的原文**（`scripts/sw_assembly.py`，`collect_mate_entity_evidence()` 内）：

  ```
  "reference_type": int(get_com_member(mate_entity, "ReferenceType") or -1),
  "reference_type2": int(get_com_member(mate_entity, "ReferenceType2") or -1),
  ```

- **官方的原文**：

  - `C:\swapi\types\IMateEntity2\ReferenceType.md` —— `Obsolete. Superseded by [[IMate2Entity::Reference2]].`，同页签名 `System.int ReferenceType {get;}`
  - CHM `SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IMateEntity2~ReferenceType.html` —— `Obsolete. Superseded by IMate2Entity::Reference2 .`（条目记录的「两源对后继写法不一致」本次**复现**：结构化页写接口名 `IMate2Entity`、CHM 写显示名 `IMate2Entity::Reference2`）

- **判定：成立** —— 官方两源一致标 Obsolete。
- **一句话依据**：官方点名后继 `IMate2Entity::Reference2`，仓内 `get_com_member(mate_entity, "ReferenceType")` 逐字可搜。
- ★ 留痕（不判不成立）：官方点名的后继接口 `IMate2Entity` 在 `C:\swapi\types\` 下**没有目录** ⇒ 换后继这条路**在离线源里查不到成员页**（与原条目口径一致，不另计一条）。

---

## 查不到 / 未核（按纪律记「查不到」，不顶替）

- **C #8 `ISldWorks.ActivateDoc2`（置信度=中）**：本轮**未核**（范围外）。顺带记录：该条目称「CHM 解包目录内没有 `ISldWorks~ActivateDoc2.html`」，本轮未复核，不作断言。
- **B #2 / #3 / #4（置信度=中）**：本轮**未核**（范围外）。
- **`C:\swapi\types\IMate2\Name.md`**：**不存在**（不是「找到但内容对不上」，是**源里没有这一页**）⇒ 按铁律 3 记「查不到」，未用 `IFeature\Name.md` 或任何相似名字顶替。
- **`C:\swapi\types\IMate2Entity\`**：**不存在** ⇒ C #7 点名的后继**查不到成员页**。
- **A #1 的运行时后果**：`mate.Name = name` 在真机上究竟抛不抛，**本轮未实测**（未跑 SolidWorks）⇒ 只按官方成员表层面判定，不对运行时行为下断言。

---

## 口径与纪律自查

- 本轮只读 `C:\swapi`（`types\` · `index\` · `examples\`）、`D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\`（CHM 解包）、`D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt` 与仓内 `scripts/sw_assembly.py`；
- **仓内只新建了本文件**，未改任何其它文件；
- **未写行号**，全部给可搜索的原文片段；
- **9 条全部两段原文齐备**，无一条靠「看起来可能有问题」下结论。