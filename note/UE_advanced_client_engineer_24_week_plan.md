# 中高级 UE 客户端开发工程师 24 周成长计划

> 目标：从“能用 UE 做功能”提升到“能以中高级 UE 客户端开发工程师身份面试”，能够讲清楚 UE C++ 架构、模块化、反射与 GC、资源管理、异步加载、网络复制、GAS、UI 架构、性能分析、编辑器工具、自动化测试与源码阅读。
>
> 适用对象：已经学习过 UE 入门内容，有 C++ / 游戏客户端基础，不满足于只做蓝图交互、小型单机 Demo 或教学项目。
>
> 核心原则：**C++ 是主线，Blueprint 是可控的配置层、表现层和验证层。**

---

## 目录

1. [这份计划与入门计划的区别](#1-这份计划与入门计划的区别)
2. [最终作品集目标](#2-最终作品集目标)
3. [24 周总览](#3-24-周总览)
4. [阶段一：UE C++ 工程化基础重建，第 1–4 周](#4-阶段一ue-c-工程化基础重建第-14-周)
5. [阶段二：数据驱动、资源管理、异步加载，第 5–8 周](#5-阶段二数据驱动资源管理异步加载第-58-周)
6. [阶段三：Gameplay 系统、GAS、AI 任务，第 9–12 周](#6-阶段三gameplay-系统gasai-任务第-912-周)
7. [阶段四：多人同步与网络架构，第 13–16 周](#7-阶段四多人同步与网络架构第-1316-周)
8. [阶段五：UI 架构、编辑器工具、性能分析，第 17–20 周](#8-阶段五ui-架构编辑器工具性能分析第-1720-周)
9. [阶段六：自动化测试、源码阅读、面试包装，第 21–24 周](#9-阶段六自动化测试源码阅读面试包装第-2124-周)
10. [每月验收标准](#10-每月验收标准)
11. [简历表达模板](#11-简历表达模板)
12. [中高级 UE 客户端面试能力清单](#12-中高级-ue-客户端面试能力清单)
13. [暂时不要深挖的方向](#13-暂时不要深挖的方向)
14. [每周复盘模板](#14-每周复盘模板)
15. [面试演示顺序](#15-面试演示顺序)

---

# 1. 这份计划与入门计划的区别

入门计划的目标是：

```text
会用 UE 编辑器
能用 Actor / Component / Blueprint 做小功能
能完成移动、交互、UI、拾取、存档等基础闭环
```

这份计划的目标是：

```text
能设计系统
能拆模块
能解释 UE 运行时机制
能定位性能问题
能写可维护的 C++ Gameplay 架构
能做数据驱动和资源管理
能处理多人同步
能写工具和自动化测试
能阅读 Lyra 等官方大型样例
能在面试中讲清楚技术取舍
```

Blueprint 在本计划中的定位：

```text
不是主要实现语言；
不是让你成为蓝图程序员；
而是作为 C++ 类的资产配置层、表现层、关卡组合层和 API 验证层。
```

推荐职责划分：

```text
C++：
- 核心 Gameplay 状态
- 组件化能力
- 网络复制
- 资源管理
- GAS 逻辑
- 性能敏感逻辑
- Editor 工具
- 自动化测试

Blueprint：
- C++ 子类的默认参数配置
- Mesh / 材质 / 音效 / 特效绑定
- 简单表现层事件
- 关卡摆放和原型验证
- UMG 视觉布局
```

---

# 2. 最终作品集目标

最终不建议只做一个“玩法完整但技术普通”的小游戏，而是做一个技术覆盖面足够强的工程化作品集：

```text
UEAdvancedClientPortfolio/
├─ Source/
│  ├─ OutpostCore/              # 基础 Runtime 模块
│  ├─ OutpostGameplay/          # Gameplay 系统模块
│  ├─ OutpostUI/                # UI / MVVM / CommonUI 模块
│  ├─ OutpostEditor/            # Editor 工具模块
│  └─ OutpostTests/             # 自动化测试模块
├─ Content/
│  ├─ Data/
│  ├─ UI/
│  ├─ Maps/
│  └─ Blueprints/
├─ Docs/
│  ├─ 01_ModulesAndBuild.md
│  ├─ 02_UObjectReflectionGC.md
│  ├─ 03_GameplayFrameworkArchitecture.md
│  ├─ 04_EventsInterfacesTags.md
│  ├─ 05_DataDrivenDesign.md
│  ├─ 06_AssetManagerAsyncLoading.md
│  ├─ 07_SaveLoadArchitecture.md
│  ├─ 08_EditorDataValidationTool.md
│  ├─ 09_InputInteractionCommandSystem.md
│  ├─ 10_GASIntegration.md
│  ├─ 11_DataDrivenGAS.md
│  ├─ 12_WorkerAIAndTaskSystem.md
│  ├─ 13_BasicReplication.md
│  ├─ 14_NetworkedMovementAndInteraction.md
│  ├─ 15_ReplicationScaling.md
│  ├─ 16_DedicatedServerAndNetworkProfiling.md
│  ├─ 17_UIArchitectureMVVMCommonUI.md
│  ├─ 18_SlateEditorTool.md
│  ├─ 19_GameThreadOptimizationReport.md
│  ├─ 20_PerformanceProfilingReport.md
│  ├─ 21_AutomationTesting.md
│  ├─ 22_LyraReadingNotes.md
│  ├─ 23_BuildAndDemoGuide.md
│  └─ 24_InterviewTalkingPoints.md
├─ SavedProfiling/
│  ├─ BeforeOptimization.utrace
│  ├─ AfterOptimization.utrace
│  └─ NetworkSession.utrace
├─ README.md
└─ DemoVideo.mp4
```

建议项目主题：

# Networked Outpost / 联机前哨基地

一个小型“俯视角合作建造 + 资源生产 + Worker 自动化 + 技能交互”的原型。

不要追求内容量，追求技术含量：

```text
1. C++ 多模块工程
2. Gameplay Framework 正确拆分
3. ActorComponent 能力组合
4. DataAsset / Primary Asset 数据驱动
5. Asset Manager + 异步加载
6. Gameplay Tags
7. GAS 或类 GAS 技能系统
8. 多人联机复制
9. Dedicated Server 可运行
10. UMG MVVM / CommonUI UI 架构
11. Worker AI 任务系统
12. Save / Load 世界状态
13. Slate Editor 工具
14. 自动化测试
15. Unreal Insights / Network Insights 性能报告
```

核心循环：

```text
玩家选择建筑
→ 服务器校验资源和位置
→ 放置建筑
→ 建筑按时间生产
→ Worker 自动采集与搬运
→ 库存和生产状态复制给客户端
→ UI 通过 ViewModel 更新
→ 存档恢复世界状态
```

---

# 3. 24 周总览

建议周期：24 周 / 6 个月。

每周建议投入：

```text
工作日：
- 3 天 × 1.5 小时：C++ 实操
- 2 天 × 40 分钟：阅读文档 / 源码 / 整理笔记

周末：
- 4–6 小时：项目集成、录制演示、写技术文档
```

阶段划分：

```text
第 1–4 周：
UE C++ 工程化基础重建

第 5–8 周：
数据驱动、资源管理、异步加载

第 9–12 周：
Gameplay 系统、GAS、AI 任务

第 13–16 周：
多人同步与网络架构

第 17–20 周：
UI 架构、编辑器工具、性能分析

第 21–24 周：
自动化测试、Lyra 源码阅读、面试包装
```

---

# 4. 阶段一：UE C++ 工程化基础重建，第 1–4 周

目标：从“会写 UE C++ 类”提升到“理解 UE C++ 工程、模块、反射、对象生命周期、构建系统”。

---

## 第 1 周：UBT、模块、Build.cs / Target.cs

### 重点问题

```text
1. UE 为什么不用普通 CMake 工程？
2. Build.cs 和 Target.cs 分别控制什么？
3. Module 的 Public / Private 边界是什么？
4. Runtime Module、Editor Module、Developer Module 有什么区别？
5. 为什么减少 include 和模块依赖能改善编译速度？
```

### 阅读链接

- [Programming with C++](https://dev.epicgames.com/documentation/unreal-engine/programming-with-cplusplus-in-unreal-engine)
- [Unreal Engine Modules](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-modules)
- [Gameplay Modules](https://dev.epicgames.com/documentation/unreal-engine/gameplay-modules-in-unreal-engine)
- [Unreal Build Tool](https://dev.epicgames.com/documentation/unreal-engine/unreal-build-tool-in-unreal-engine)
- [Unreal Engine Build Tool Target Reference](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-build-tool-target-reference)
- [Module Properties](https://dev.epicgames.com/documentation/unreal-engine/module-properties-in-unreal-engine)
- [Epic C++ Coding Standard](https://dev.epicgames.com/documentation/unreal-engine/epic-cplusplus-coding-standard-for-unreal-engine)

### 实操任务

创建新项目：

```text
UEAdvancedClientPortfolio
```

建立模块：

```text
Source/
├─ OutpostCore/
├─ OutpostGameplay/
├─ OutpostUI/
└─ OutpostEditor/
```

要求：

```text
1. OutpostCore 不依赖 UI。
2. OutpostGameplay 可以依赖 OutpostCore。
3. OutpostUI 可以依赖 OutpostCore 和 OutpostGameplay。
4. OutpostEditor 只在 Editor Build 中编译。
5. 每个模块有清晰 Public / Private 目录。
6. Public 头文件尽量少 include，用前置声明降低耦合。
```

### 产出

```text
Docs/01_ModulesAndBuild.md
```

必须写清楚：

```text
- 每个模块负责什么
- 为什么这样拆
- Build.cs 中每个依赖为什么存在
- 哪些 include 被前置声明替代了
- 如果未来增加多人、UI、编辑器工具，模块依赖如何保持清晰
```

---

## 第 2 周：UObject、反射、GC、对象指针

### 重点问题

```text
1. UObject 和普通 C++ 对象的区别是什么？
2. UCLASS / UPROPERTY / UFUNCTION 到底让 UE 获得了什么能力？
3. UPROPERTY 与 GC 的关系是什么？
4. TObjectPtr、TWeakObjectPtr、TSoftObjectPtr、TSubclassOf 分别用于什么场景？
5. 为什么不要随便裸指针持有 UObject？
6. CDO 是什么？
7. 构造函数、PostInitializeComponents、BeginPlay 的职责区别是什么？
```

### 阅读链接

- [Reflection System](https://dev.epicgames.com/documentation/unreal-engine/reflection-system-in-unreal-engine)
- [Objects in Unreal Engine](https://dev.epicgames.com/documentation/unreal-engine/objects-in-unreal-engine)
- [Game Objects](https://dev.epicgames.com/documentation/unreal-engine/game-objects-in-unreal-engine)
- [Object Pointers](https://dev.epicgames.com/documentation/unreal-engine/object-pointers-in-unreal-engine)
- [Actor Lifecycle](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-actor-lifecycle)
- [Metadata Specifiers](https://dev.epicgames.com/documentation/unreal-engine/metadata-specifiers-in-unreal-engine)

### 实操任务

实现：

```cpp
UOutpostItemDefinition : public UPrimaryDataAsset
UOutpostInventoryComponent : public UActorComponent
AOutpostPickupActor : public AActor
```

要求：

```text
1. ItemDefinition 使用软引用保存图标、Mesh、音效。
2. PickupActor 使用 TObjectPtr 保存组件。
3. InventoryComponent 暴露 BlueprintCallable 接口，但核心逻辑用 C++。
4. 故意制造一个未被 UPROPERTY 持有的 UObject 引用，观察 GC 风险并写笔记。
5. 对比 TObjectPtr、TWeakObjectPtr、TSoftObjectPtr 的使用场景。
```

### 产出

```text
Docs/02_UObjectReflectionGC.md
```

必须写清楚：

```text
- 哪些对象应该继承 UObject
- 哪些对象应该只是普通 struct
- 为什么 UPROPERTY 不只是“给蓝图用”
- GC 问题如何排查
- 构造函数里应该做什么，不应该做什么
```

---

## 第 3 周：Gameplay Framework、Subsystem、Component 架构

### 重点问题

```text
1. GameInstance / World / GameMode / GameState / PlayerController / PlayerState / Pawn 的职责边界是什么？
2. 哪些数据属于 PlayerState，哪些属于 PlayerController？
3. Subsystem 适合放什么，不适合放什么？
4. ActorComponent 如何用于组合能力？
5. 为什么中大型项目倾向“组件化能力 + 数据驱动”？
```

### 阅读链接

- [Gameplay Framework](https://dev.epicgames.com/documentation/unreal-engine/gameplay-framework-in-unreal-engine)
- [Gameplay Framework Quick Reference](https://dev.epicgames.com/documentation/unreal-engine/gameplay-framework-quick-reference-in-unreal-engine)
- [Components](https://dev.epicgames.com/documentation/unreal-engine/components-in-unreal-engine)
- [Programming Subsystems](https://dev.epicgames.com/documentation/unreal-engine/programming-subsystems-in-unreal-engine)
- [Game Framework Component Manager](https://dev.epicgames.com/documentation/unreal-engine/game-framework-component-manager-in-unreal-engine)

### 实操任务

实现：

```text
UOutpostGameInstanceSubsystem
UOutpostWorldSubsystem
UOutpostInventoryComponent
UOutpostProductionComponent
UOutpostInteractionComponent
AOutpostPlayerController
AOutpostPlayerState
AOutpostCharacter
AOutpostGameMode
AOutpostGameState
```

职责要求：

```text
PlayerController：
- 输入
- UI 打开关闭
- 玩家本地操作请求
- 本地鼠标命中检测

PlayerState：
- 可复制的玩家资源、积分、队伍信息

GameMode：
- 只在服务器存在
- 出生规则
- 胜负规则
- 服务器端建造校验入口

GameState：
- 全局可复制状态
- 比赛阶段
- 全局计时
- 世界资源总览

Component：
- 可复用能力
- 库存、生产、交互、生命值、任务队列

Subsystem：
- 全局服务
- 配置索引
- 运行时注册表
- 资源查询
```

### 产出

```text
Docs/03_GameplayFrameworkArchitecture.md
```

必须包含一张对象关系图：

```text
GameInstance
  └─ GameInstanceSubsystem
World
  ├─ WorldSubsystem
  ├─ GameMode       # Server Only
  ├─ GameState      # Replicated
  ├─ PlayerController
  ├─ PlayerState    # Replicated
  └─ Pawn / Character
       ├─ InventoryComponent
       ├─ InteractionComponent
       └─ AbilitySystemComponent
```

---

## 第 4 周：接口、Delegate、事件总线、Gameplay Tags

### 重点问题

```text
1. UE Interface 和 C++ 纯虚接口有什么区别？
2. Dynamic Delegate、Native Delegate、Multicast Delegate 区别是什么？
3. 什么时候用 Interface，什么时候用 Delegate，什么时候直接引用？
4. Gameplay Tags 如何替代字符串、枚举和硬编码判断？
5. Tag Query 适合解决什么复杂条件判断？
```

### 阅读链接

- [Using Gameplay Tags](https://dev.epicgames.com/documentation/unreal-engine/using-gameplay-tags-in-unreal-engine)
- [Blueprint Interface](https://dev.epicgames.com/documentation/unreal-engine/blueprint-interface-in-unreal-engine)
- [Event Dispatchers](https://dev.epicgames.com/documentation/unreal-engine/event-dispatchers-in-unreal-engine)

### 实操任务

实现：

```text
UOutpostInteractableInterface
FOutpostInventoryChangedNativeDelegate
FOutpostInventoryChangedDynamicDelegate
Gameplay Tags:
- Item.Resource.Wood
- Item.Resource.Ore
- Building.Production.Sawmill
- Building.Storage.Warehouse
- Ability.Build.PlaceBuilding
- Ability.Resource.Collect
- State.Player.Interacting
- State.Building.Producing
```

要求：

```text
1. 交互对象通过 Interface 被调用。
2. 库存变化通过 Delegate 广播。
3. UI 不主动 Tick 查询库存。
4. 物品分类不使用字符串比较。
5. 建筑、物品、技能、状态统一使用 Gameplay Tags 表达语义。
```

### 产出

```text
Docs/04_EventsInterfacesTags.md
```

---

# 5. 阶段二：数据驱动、资源管理、异步加载，第 5–8 周

目标：让作品具备中大型 UE 项目的数据与资源组织能力。

---

## 第 5 周：DataAsset、DataTable、Primary Asset

### 重点问题

```text
1. DataAsset 和 DataTable 分别适合什么？
2. Primary Asset 和 Secondary Asset 的区别是什么？
3. 为什么大型项目不能到处硬引用资源？
4. 如何用 PrimaryAssetId 作为稳定的数据入口？
5. 数据和表现如何分离？
```

### 阅读链接

- [Asset Management](https://dev.epicgames.com/documentation/unreal-engine/asset-management-in-unreal-engine)
- [Data-Driven Gameplay Elements](https://dev.epicgames.com/documentation/unreal-engine/data-driven-gameplay-elements-in-unreal-engine)
- [UAssetManager API](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/UAssetManager)

### 实操任务

实现：

```cpp
UOutpostItemDefinition : public UPrimaryDataAsset
UOutpostBuildingDefinition : public UPrimaryDataAsset
UOutpostAbilityDefinition : public UPrimaryDataAsset
```

每个 Definition 至少包含：

```text
ID
DisplayName
Description
Icon
Mesh / VisualClass
GameplayTags
Cost
RuntimeClass
Soft References
```

建筑配置示例：

```text
Building.Production.Sawmill
- Cost: Wood 20, Ore 5
- ProductionOutput: Plank 2
- ProductionInterval: 5s
- RequiredTags: State.Player.CanBuild
- VisualClass: BP_Sawmill
```

### 产出

```text
Docs/05_DataDrivenDesign.md
```

---

## 第 6 周：Asset Manager 与异步加载

### 重点问题

```text
1. TSoftObjectPtr / TSoftClassPtr 解决什么问题？
2. 同步加载为什么可能造成卡顿？
3. Asset Manager 如何按类型扫描和加载 Primary Asset？
4. Load Bundle 的意义是什么？
5. 如何避免 UI 打开时瞬间加载大量资源？
```

### 阅读链接

- [Asset Management](https://dev.epicgames.com/documentation/unreal-engine/asset-management-in-unreal-engine)
- [Asynchronous Asset Loading](https://dev.epicgames.com/documentation/unreal-engine/asynchronous-asset-loading-in-unreal-engine)
- [Async Load Primary Asset](https://dev.epicgames.com/documentation/unreal-engine/BlueprintAPI/AssetManager/AsyncLoadPrimaryAsset)

### 实操任务

实现：

```text
UOutpostAssetManager : public UAssetManager
UOutpostAssetSubsystem
FOutpostAsyncLoadHandle
```

要求：

```text
1. 启动时只扫描轻量数据。
2. 打开建筑菜单时异步加载建筑图标。
3. 进入关卡前 Preload 当前关卡需要的建筑资源。
4. 所有异步加载过程有 Loading 状态和失败处理。
5. 避免在 UI Construct 中同步加载大量资源。
6. 使用 Unreal Insights 记录一次加载耗时。
```

### 产出

```text
Docs/06_AssetManagerAsyncLoading.md
SavedProfiling/AssetLoadingTrace.utrace
```

---

## 第 7 周：存档、序列化与世界状态恢复

### 重点问题

```text
1. SaveGame 应保存 Actor，还是保存可重建数据？
2. 如何保存建筑类型、位置、库存、生产进度？
3. 如何处理版本升级后的存档兼容？
4. 如何避免保存临时运行时对象引用？
```

### 阅读链接

- [Saving and Loading Your Game](https://dev.epicgames.com/documentation/unreal-engine/saving-and-loading-your-game-in-unreal-engine)

### 实操任务

实现：

```text
UOutpostSaveGame
FOutpostBuildingSaveData
FOutpostInventorySaveData
FOutpostWorkerSaveData
FOutpostWorldSaveData
```

要求：

```text
1. 保存所有建筑实例。
2. 保存建筑 Definition ID。
3. 保存 Transform、库存、生产队列、生产剩余时间。
4. 保存 Worker 当前任务。
5. 读取时根据 Definition ID 重新生成建筑。
6. 加入 SaveVersion 字段。
7. 写一个旧版本兼容处理示例。
```

### 产出

```text
Docs/07_SaveLoadArchitecture.md
```

---

## 第 8 周：配置验证与编辑器工具雏形

### 重点问题

```text
1. 设计师填错 DataAsset 时程序如何提前发现？
2. 如何避免运行时才发现资源缺失？
3. 如何写一个编辑器工具检查所有配置？
4. 为什么中高级程序员要关心内容管线？
```

### 阅读链接

- [Plugins](https://dev.epicgames.com/documentation/unreal-engine/plugins-in-unreal-engine)
- [Setting Up Editor Modules](https://dev.epicgames.com/documentation/unreal-engine/setting-up-editor-modules-for-customizing-the-editor-in-unreal-engine)
- [Slate Editor Window Quickstart](https://dev.epicgames.com/documentation/unreal-engine/slate-editor-window-quickstart-guide-for-unreal-engine)

### 实操任务

在 `OutpostEditor` 模块中实现工具：

```text
Outpost Data Validator
```

功能：

```text
1. 扫描所有 ItemDefinition / BuildingDefinition / AbilityDefinition。
2. 检查 ID 是否重复。
3. 检查图标、Mesh、RuntimeClass 是否为空。
4. 检查 Cost 是否存在负数。
5. 检查 Gameplay Tags 是否符合命名规范。
6. 输出错误列表。
7. 支持一键定位资产。
```

### 产出

```text
Docs/08_EditorDataValidationTool.md
```

---

# 6. 阶段三：Gameplay 系统、GAS、AI 任务，第 9–12 周

目标：实现一个可展示架构能力的 Gameplay 系统，而不是简单 if/else 堆功能。

---

## 第 9 周：Enhanced Input、交互系统、命令系统

### 重点问题

```text
1. 输入应该写在 Character 还是 PlayerController？
2. 如何让输入变成语义化命令，而不是直接操作对象？
3. RTS / 模拟经营 / 动作游戏中的交互系统如何统一？
4. 如何设计可扩展的 Interact Target？
```

### 阅读链接

- [Enhanced Input](https://dev.epicgames.com/documentation/unreal-engine/enhanced-input-in-unreal-engine)
- [Lyra Interaction System](https://dev.epicgames.com/documentation/unreal-engine/lyra-sample-game-interaction-system-in-unreal-engine)

### 实操任务

实现：

```text
UOutpostInputConfig
UOutpostInteractionComponent
UOutpostCommandComponent
IOutpostInteractable
FOutpostInteractionQuery
FOutpostInteractionResult
FOutpostCommandRequest
FOutpostCommandResult
```

要求：

```text
1. 鼠标点击、E 键交互、框选指令都走统一命令入口。
2. 命令可失败，并返回失败原因。
3. 交互对象通过 Gameplay Tags 描述能力。
4. 本地可以做交互提示，但最终执行要为后续服务器校验预留接口。
```

### 产出

```text
Docs/09_InputInteractionCommandSystem.md
```

---

## 第 10 周：GAS 基础集成

### 重点问题

```text
1. AbilitySystemComponent 应该挂在哪？
2. AttributeSet 负责什么？
3. GameplayAbility、GameplayEffect、GameplayCue 分别解决什么？
4. GAS 的输入激活、事件激活、标签阻塞如何工作？
5. 哪些项目适合 GAS，哪些不一定需要？
```

### 阅读链接

- [Gameplay Ability System](https://dev.epicgames.com/documentation/unreal-engine/gameplay-ability-system-for-unreal-engine)
- [Understanding Gameplay Ability System](https://dev.epicgames.com/documentation/unreal-engine/understanding-the-unreal-engine-gameplay-ability-system)
- [Using Gameplay Abilities](https://dev.epicgames.com/documentation/unreal-engine/using-gameplay-abilities-in-unreal-engine)
- [Gameplay Attributes and Attribute Sets](https://dev.epicgames.com/documentation/unreal-engine/gameplay-attributes-and-attribute-sets-for-the-gameplay-ability-system-in-unreal-engine)
- [Gameplay Effects](https://dev.epicgames.com/documentation/unreal-engine/gameplay-effects-for-the-gameplay-ability-system-in-unreal-engine)
- [Gameplay Ability Tasks](https://dev.epicgames.com/documentation/unreal-engine/gameplay-ability-tasks-in-unreal-engine)

### 实操任务

实现：

```text
UOutpostAbilitySystemComponent
UOutpostAttributeSet
UOutpostGameplayAbility
UOutpostGameplayEffect
```

至少实现三个 Ability：

```text
Ability.Build.PlaceBuilding
Ability.Resource.Collect
Ability.Worker.AssignTask
```

### 产出

```text
Docs/10_GASIntegration.md
```

必须写清楚：

```text
- ASC 放在 PlayerState、Pawn、Actor 上分别有什么取舍
- 哪些逻辑放 Ability
- 哪些逻辑仍然应该放普通 Component
- Gameplay Tags 如何控制 Ability 可用性
```

---

## 第 11 周：GAS 与数据驱动结合

### 重点问题

```text
1. Ability 如何由 DataAsset 授予？
2. 技能消耗、冷却、标签条件如何数据化？
3. 如何让建筑、Worker、玩家共享 Ability 框架？
4. Ability 与普通组件逻辑如何分工？
```

### 实操任务

实现：

```text
UOutpostAbilitySet
UOutpostAbilityDefinition
UOutpostAbilityGrantComponent
```

要求：

```text
1. 建筑 Definition 可以授予生产 Ability。
2. 玩家 Definition 可以授予建造 Ability。
3. Worker Definition 可以授予采集 Ability。
4. 使用 Gameplay Tags 控制技能可用性。
5. 使用 DataAsset 配置 Cost、Cooldown、RequiredTags、BlockedTags。
```

### 产出

```text
Docs/11_DataDrivenGAS.md
```

---

## 第 12 周：AI Worker 与任务系统

### 重点问题

```text
1. 简单状态机、Behavior Tree、StateTree 各适合什么？
2. AI 任务如何和 Gameplay 系统解耦？
3. Worker 如何执行采集、搬运、建造任务？
4. 任务状态如何可保存、可复制？
```

### 阅读链接

- [Behavior Trees](https://dev.epicgames.com/documentation/unreal-engine/behavior-trees-in-unreal-engine)
- [StateTree API](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/StateTreeModule)

### 实操任务

实现：

```text
UOutpostTaskComponent
AOutpostWorkerCharacter
UOutpostWorkerBrainComponent
FOutpostTaskData
```

Worker 支持：

```text
1. 前往资源点。
2. 采集资源。
3. 返回仓库。
4. 存入库存。
5. 如果目标失效，重新选择任务。
6. 任务状态可保存。
```

### 产出

```text
Docs/12_WorkerAIAndTaskSystem.md
```

---

# 7. 阶段四：多人同步与网络架构，第 13–16 周

目标：让作品从“单机客户端 Demo”升级为“能体现 UE 网络能力的工程项目”。

---

## 第 13 周：UE 网络模型、权威服务器、属性复制、RPC

### 重点问题

```text
1. Server Authoritative 是什么？
2. Actor Replication、Property Replication、RPC 分别解决什么？
3. Server RPC、Client RPC、NetMulticast RPC 适合什么？
4. OnRep 何时调用？
5. 为什么客户端不能直接改权威状态？
```

### 阅读链接

- [Networking Overview](https://dev.epicgames.com/documentation/unreal-engine/networking-overview-for-unreal-engine)
- [Networking and Multiplayer](https://dev.epicgames.com/documentation/unreal-engine/networking-and-multiplayer-in-unreal-engine)
- [Actor Replication](https://dev.epicgames.com/documentation/unreal-engine/actor-replication-in-unreal-engine)
- [Testing and Debugging Networked Games](https://dev.epicgames.com/documentation/unreal-engine/testing-and-debugging-networked-games-in-unreal-engine)
- [Console Commands for Network Debugging](https://dev.epicgames.com/documentation/unreal-engine/console-commands-for-network-debugging-in-unreal-engine)

### 实操任务

改造系统：

```text
1. 库存资源在服务器修改，通过 PlayerState 或 GameState 复制给客户端。
2. 建筑放置请求由客户端发起，服务器校验并生成建筑。
3. 生产进度由服务器驱动。
4. UI 只显示复制下来的状态。
5. OnRep 回调推动 UI ViewModel 更新。
```

### 产出

```text
Docs/13_BasicReplication.md
```

---

## 第 14 周：网络化移动、交互与预测思维

### 重点问题

```text
1. CharacterMovementComponent 为什么能处理网络移动？
2. 自定义移动能力要考虑哪些同步问题？
3. 客户端表现和服务器权威如何平衡？
4. 哪些东西可以本地预测，哪些不应该预测？
```

### 阅读链接

- [Understanding Networked Movement in Character Movement Component](https://dev.epicgames.com/documentation/unreal-engine/understanding-networked-movement-in-the-character-movement-component-for-unreal-engine)

### 实操任务

实现：

```text
1. 联机下角色移动正常。
2. 客户端请求采集，服务器验证距离和目标合法性。
3. 客户端本地显示交互提示，但真正资源变化由服务器决定。
4. 写一个“作弊请求”测试：客户端越距采集应被拒绝。
5. 网络延迟模拟下，UI 给出合理反馈。
```

### 产出

```text
Docs/14_NetworkedMovementAndInteraction.md
```

---

## 第 15 周：Replication Graph / Iris 概念与可选实现

### 重点问题

```text
1. 大量 Actor 复制为什么会造成服务器 CPU 压力？
2. Replication Graph 用什么方式降低每连接复制计算成本？
3. Iris 是什么，它和传统复制系统是什么关系？
4. 什么时候不应该过早引入 Replication Graph / Iris？
```

### 阅读链接

- [Replication Graph](https://dev.epicgames.com/documentation/unreal-engine/replication-graph-in-unreal-engine)
- [Iris Replication System](https://dev.epicgames.com/documentation/unreal-engine/iris-replication-system-in-unreal-engine)

### 实操任务

最低要求：

```text
1. 写一份 Replication Graph / Iris 对比笔记。
2. 项目中生成 200 个资源节点和 50 个 Worker。
3. 用 Network Insights 观察复制流量。
```

进阶要求：

```text
实现一个最简单的 Replication Graph 分区节点：
- 距离近的建筑高频复制
- 距离远的资源节点低频复制
```

### 产出

```text
Docs/15_ReplicationScaling.md
```

---

## 第 16 周：Dedicated Server、联机测试与网络分析

### 重点问题

```text
1. Listen Server 和 Dedicated Server 区别是什么？
2. 如何运行两个客户端连接本地服务器？
3. 如何分析网络带宽和 RPC 数量？
4. 如何写网络问题复现步骤？
```

### 阅读链接

- [Setting Up Dedicated Servers](https://dev.epicgames.com/documentation/unreal-engine/setting-up-dedicated-servers-in-unreal-engine)
- [Networking Insights](https://dev.epicgames.com/documentation/unreal-engine/networking-insights-in-unreal-engine)

### 实操任务

实现：

```text
1. 打包 Dedicated Server。
2. 本机启动 Server + 两个 Client。
3. 两个玩家可以合作建造和采集。
4. 使用 Networking Insights 记录一次会话。
5. 写清楚启动命令和复现步骤。
```

### 产出

```text
Docs/16_DedicatedServerAndNetworkProfiling.md
SavedProfiling/NetworkSession.utrace
```

---

# 8. 阶段五：UI 架构、编辑器工具、性能分析，第 17–20 周

目标：让作品达到“能讲 UI 架构、能讲性能定位、能给出优化前后证据”的水平。

---

## 第 17 周：UMG、MVVM、CommonUI

### 重点问题

```text
1. UI 为什么不应该大量 Tick 或直接绑定复杂 Getter？
2. ViewModel 如何隔离数据层和表现层？
3. CommonUI 解决什么跨平台导航问题？
4. C++ UI 后端和 UMG 表现层如何协作？
```

### 阅读链接

- [Creating User Interfaces with UMG and Slate](https://dev.epicgames.com/documentation/unreal-engine/creating-user-interfaces-with-umg-and-slate-in-unreal-engine)
- [UMG Viewmodel](https://dev.epicgames.com/documentation/unreal-engine/umg-viewmodel-for-unreal-engine)
- [Common UI Overview](https://dev.epicgames.com/documentation/unreal-engine/overview-of-advanced-multiplatform-user-interfaces-with-common-ui-for-unreal-engine)
- [Common UI Quickstart](https://dev.epicgames.com/documentation/unreal-engine/common-ui-quickstart-guide-for-unreal-engine)
- [Using CommonUI with Enhanced Input](https://dev.epicgames.com/documentation/unreal-engine/using-commonui-with-enhnaced-input-in-unreal-engine)

### 实操任务

实现 UI 架构：

```text
UOutpostInventoryViewModel
UOutpostBuildingMenuViewModel
UOutpostProductionViewModel
UOutpostNetworkStatusViewModel
```

要求：

```text
1. UI 不主动 Tick 查询 Gameplay 对象。
2. Gameplay 状态变化后推送到 ViewModel。
3. UMG 只负责布局和展示。
4. 支持键鼠和手柄导航基础逻辑。
5. 建筑菜单图标通过 Asset Manager 异步加载。
```

### 产出

```text
Docs/17_UIArchitectureMVVMCommonUI.md
```

---

## 第 18 周：Slate 与编辑器工具 UI

### 重点问题

```text
1. UMG 和 Slate 的关系是什么？
2. 为什么编辑器工具常用 Slate？
3. 如何写一个简单 Editor Window？
4. Runtime UI 和 Editor UI 如何隔离模块？
```

### 阅读链接

- [Slate Overview](https://dev.epicgames.com/documentation/unreal-engine/slate-overview-for-unreal-engine)
- [Understanding the Slate UI Architecture](https://dev.epicgames.com/documentation/unreal-engine/understanding-the-slate-ui-architecture-in-unreal-engine)
- [Slate UI Framework](https://dev.epicgames.com/documentation/unreal-engine/slate-user-interface-programming-framework-for-unreal-engine)
- [Using Slate in a Project](https://dev.epicgames.com/documentation/unreal-engine/using-slate-in-a-project-in-unreal-engine)
- [Slate Editor Window Quickstart](https://dev.epicgames.com/documentation/unreal-engine/slate-editor-window-quickstart-guide-for-unreal-engine)
- [Programming Tools with Slate UI in C++](https://dev.epicgames.com/documentation/unreal-engine/programming-tools-for-the-unreal-editor-with-slate-ui-in-cplusplus)

### 实操任务

升级第 8 周的数据验证工具：

```text
1. 使用 Slate 做一个 Editor Tab。
2. 左侧显示资产列表。
3. 右侧显示错误详情。
4. 支持双击打开资产。
5. 支持导出 CSV 报告。
6. 支持按错误等级筛选。
```

### 产出

```text
Docs/18_SlateEditorTool.md
```

---

## 第 19 周：CPU / GameThread / Tick 优化

### 重点问题

```text
1. GameThread、RenderThread、RHIThread 基本职责是什么？
2. Tick 过多为什么危险？
3. Timer、事件驱动、批处理、对象池分别适合什么？
4. 如何用 stat 命令和 Unreal Insights 找瓶颈？
```

### 阅读链接

- [Introduction to Performance Profiling and Configuration](https://dev.epicgames.com/documentation/unreal-engine/introduction-to-performance-profiling-and-configuration-in-unreal-engine)
- [Unreal Insights](https://dev.epicgames.com/documentation/unreal-engine/unreal-insights-in-unreal-engine)
- [Trace Quick Start](https://dev.epicgames.com/documentation/unreal-engine/trace-quick-start-guide-in-unreal-engine)
- [Timing Insights](https://dev.epicgames.com/documentation/unreal-engine/timing-insights-in-unreal-engine-5)
- [Stat Commands](https://dev.epicgames.com/documentation/unreal-engine/stat-commands-in-unreal-engine)
- [Common Memory and CPU Performance Considerations](https://dev.epicgames.com/documentation/unreal-engine/common-memory-and-cpu-performance-considerations-in-unreal-engine)

### 实操任务

制造并优化性能问题：

```text
1. 生成 500 个资源点和 100 个 Worker。
2. 第一版每个 Worker Tick 扫描任务。
3. 用 stat unit / stat game / Unreal Insights 定位开销。
4. 改成任务队列 + Timer / 事件驱动。
5. 记录优化前后帧耗时和 GameThread 耗时。
```

### 产出

```text
Docs/19_GameThreadOptimizationReport.md
SavedProfiling/BeforeGameThreadOptimization.utrace
SavedProfiling/AfterGameThreadOptimization.utrace
```

---

## 第 20 周：内存、加载、UI 性能与网络性能

### 重点问题

```text
1. 如何观察内存分配与泄漏？
2. 软引用和异步加载是否真的降低了启动开销？
3. UI 刷新过度如何定位？
4. 网络流量如何分析？
```

### 阅读链接

- [Memory Insights](https://dev.epicgames.com/documentation/unreal-engine/memory-insights-in-unreal-engine)
- [Low-Level Memory Tracker](https://dev.epicgames.com/documentation/unreal-engine/using-the-low-level-memory-tracker-in-unreal-engine)
- [Networking Insights](https://dev.epicgames.com/documentation/unreal-engine/networking-insights-in-unreal-engine)
- [Slate Insights](https://dev.epicgames.com/documentation/unreal-engine/slate-insights-in-unreal-engine)
- [Texture Streaming Metrics](https://dev.epicgames.com/documentation/unreal-engine/texture-streaming-metrics-in-unreal-engine)

### 实操任务

完成综合性能报告：

```text
1. 启动加载时间。
2. 打开建筑菜单加载时间。
3. 内存占用。
4. UI 刷新次数。
5. 网络流量。
6. 优化前后对比。
```

### 产出

```text
Docs/20_PerformanceProfilingReport.md
```

---

# 9. 阶段六：自动化测试、源码阅读、面试包装，第 21–24 周

目标：把作品从“做出来”提升为“可维护、可解释、可面试”。

---

## 第 21 周：自动化测试与功能测试

### 重点问题

```text
1. UE 自动化测试分哪几类？
2. 低层 C++ 测试和 Functional Test 区别是什么？
3. 哪些 Gameplay 逻辑值得写自动化测试？
4. 如何测试 DataAsset 配置合法性？
```

### 阅读链接

- [Automation Test Framework](https://dev.epicgames.com/documentation/unreal-engine/automation-test-framework-in-unreal-engine)
- [Write C++ Tests](https://dev.epicgames.com/documentation/unreal-engine/write-cplusplus-tests-in-unreal-engine)
- [Functional Testing](https://dev.epicgames.com/documentation/unreal-engine/functional-testing-in-unreal-engine)
- [Run Automation Tests](https://dev.epicgames.com/documentation/unreal-engine/run-automation-tests-in-unreal-engine)

### 实操任务

写测试：

```text
1. Inventory Add / Remove / Stack 测试。
2. Building Cost 校验测试。
3. DataAsset 配置扫描测试。
4. Save / Load 数据一致性测试。
5. Functional Test：放置建筑后资源扣除。
6. Server 权威校验测试：越距采集失败。
```

### 产出

```text
Docs/21_AutomationTesting.md
```

---

## 第 22 周：Lyra 源码阅读与架构复盘

### 重点问题

```text
1. Lyra 为什么采用模块化架构？
2. Lyra 的 Ability、Input、Experience、Game Feature 如何协作？
3. Lyra 如何组织可扩展 Gameplay？
4. 哪些设计可以借鉴，哪些对你的小项目过度设计？
```

### 阅读链接

- [Lyra Sample Game](https://dev.epicgames.com/documentation/unreal-engine/lyra-sample-game-in-unreal-engine)
- [Tour of Lyra](https://dev.epicgames.com/documentation/unreal-engine/tour-of-lyra-in-unreal-engine)
- [Abilities in Lyra](https://dev.epicgames.com/documentation/unreal-engine/abilities-in-lyra-in-unreal-engine)
- [Lyra Interaction System](https://dev.epicgames.com/documentation/unreal-engine/lyra-sample-game-interaction-system-in-unreal-engine)
- [Game Framework Component Manager](https://dev.epicgames.com/documentation/unreal-engine/game-framework-component-manager-in-unreal-engine)

### 实操任务

写 5 篇源码阅读笔记：

```text
1. Lyra Gameplay Framework 拆分
2. Lyra Input 到 Ability 的链路
3. Lyra Interaction System
4. Lyra Ability Set / Experience 思路
5. Lyra 哪些设计不适合小项目
```

### 产出

```text
Docs/22_LyraReadingNotes.md
```

---

## 第 23 周：打包、Dedicated Server、文档与演示

### 重点问题

```text
1. Development / Shipping 包有什么差异？
2. Dedicated Server 如何打包和启动？
3. 如何准备面试演示材料？
4. 如何让面试官快速看到你的技术深度？
```

### 阅读链接

- [Packaging Unreal Engine Projects](https://dev.epicgames.com/documentation/unreal-engine/packaging-your-project)
- [Build Configurations Reference](https://dev.epicgames.com/documentation/unreal-engine/build-configurations-reference-for-unreal-engine)
- [Setting Up Dedicated Servers](https://dev.epicgames.com/documentation/unreal-engine/setting-up-dedicated-servers-in-unreal-engine)

### 实操任务

准备：

```text
1. Windows Client 包。
2. Windows Dedicated Server 包。
3. 本地双客户端联机演示脚本。
4. 2–3 分钟短演示视频。
5. 10 分钟技术讲解文档。
6. README 首页写清楚技术亮点，而不是只写玩法介绍。
```

### 产出

```text
Builds/
DemoVideo.mp4
Docs/23_BuildAndDemoGuide.md
README.md
```

---

## 第 24 周：面试题库、项目复盘、简历表达

### 重点问题

```text
1. 你这个项目最能体现中高级能力的点是什么？
2. 如果面试官问“为什么不用纯蓝图”，怎么答？
3. 如果问“为什么用 GAS / 为什么不用 GAS”，怎么答？
4. 如果问“性能瓶颈怎么定位”，怎么答？
5. 如果问“网络复制怎么保证安全”，怎么答？
6. 如果问“你读过哪些 UE 源码”，怎么答？
```

### 产出文件

```text
Docs/24_InterviewTalkingPoints.md
```

必须包含以下回答：

```text
1. 项目整体架构
2. C++ 与 Blueprint 分工
3. 模块化设计
4. 数据驱动设计
5. Asset Manager 与异步加载
6. Gameplay Tags 使用场景
7. GAS 设计取舍
8. 网络复制架构
9. Dedicated Server 测试方法
10. UI 架构
11. 性能分析过程
12. 自动化测试覆盖
13. Lyra 源码借鉴
14. 项目仍有哪些不足
15. 如果加入团队，你能负责什么模块
```

---

# 10. 每月验收标准

## 第 1 月结束

你应该能讲清楚：

```text
1. UBT / Module / Build.cs / Target.cs
2. UObject / Reflection / GC
3. Gameplay Framework 职责划分
4. Subsystem / Component 架构
5. Interface / Delegate / Gameplay Tags
```

面试表现目标：

```text
不再只说“我会 Actor 和组件”，而是能讲“为什么这个系统这样拆”。
```

---

## 第 2 月结束

你应该能展示：

```text
1. DataAsset / PrimaryAssetId 驱动的物品和建筑系统
2. Asset Manager 异步加载
3. Save / Load 世界恢复
4. Editor 数据验证工具
```

面试表现目标：

```text
能体现你不只是写 Gameplay，还理解内容管线和大型项目资源管理。
```

---

## 第 3 月结束

你应该能展示：

```text
1. 命令式交互系统
2. GAS 技能系统
3. 数据驱动授予 Ability
4. Worker AI 任务循环
```

面试表现目标：

```text
能讲清楚“能力系统、任务系统、数据系统如何解耦”。
```

---

## 第 4 月结束

你应该能展示：

```text
1. 多人联机
2. 服务器权威
3. 属性复制与 RPC
4. 网络化交互校验
5. Dedicated Server
6. Network Insights 报告
```

面试表现目标：

```text
能证明你具备多人 UE 项目的基本工程能力。
```

---

## 第 5 月结束

你应该能展示：

```text
1. MVVM / CommonUI UI 架构
2. Slate 编辑器工具
3. Unreal Insights 性能分析
4. GameThread 优化前后对比
5. 内存、加载、UI、网络性能报告
```

面试表现目标：

```text
能从“我优化过”升级为“我用工具定位、记录指标、做前后对比”。
```

---

## 第 6 月结束

你应该能展示：

```text
1. 自动化测试
2. Lyra 源码阅读笔记
3. Client + Dedicated Server 打包
4. 完整 README
5. 2–3 分钟演示视频
6. 10 分钟技术讲解文档
```

面试表现目标：

```text
面试官可以通过仓库、文档、视频快速判断你具备中高级 UE 客户端潜力。
```

---

# 11. 简历表达模板

不要写：

```text
熟悉 UE5，掌握蓝图、C++、UMG、网络同步。
```

建议写：

```text
基于 UE5 C++ 实现一个联机前哨基地原型，采用多模块 Runtime / Editor 架构，核心 Gameplay 使用 C++ 组件化设计，表现层通过 Blueprint / UMG 配置。项目包含 DataAsset / AssetManager 驱动的物品与建筑系统、Gameplay Tags、GAS 技能系统、服务器权威的建筑放置与资源生产复制、Dedicated Server 本地双客户端联机测试、UMG MVVM / CommonUI UI 架构、Slate 编辑器数据校验工具，并使用 Unreal Insights / Network Insights 完成性能分析和优化报告。
```

可拆成要点：

```text
- 设计 OutpostCore / OutpostGameplay / OutpostUI / OutpostEditor 多模块架构，控制模块依赖与 Runtime / Editor 代码边界。
- 使用 UPrimaryDataAsset、PrimaryAssetId、Asset Manager 与软引用实现数据驱动资源加载，降低硬引用与启动加载压力。
- 基于 Gameplay Tags 和 GAS 实现建造、采集、任务分配等能力，支持数据驱动授予和标签条件控制。
- 实现服务器权威的资源、建筑、生产状态同步，支持 Dedicated Server 与双客户端联机测试。
- 使用 UMG MVVM / CommonUI 组织 UI 状态流，避免高频 Tick 和复杂绑定。
- 开发 Slate Editor 数据验证工具，扫描配置资产并输出错误报告。
- 使用 Unreal Insights、Memory Insights、Networking Insights 记录并优化 GameThread、加载、内存和网络性能。
- 编写 Inventory、Building Cost、Save / Load、Data Validation 等自动化测试。
```

---

# 12. 中高级 UE 客户端面试能力清单

## C++ / UE 基础

```text
- UObject / AActor / UActorComponent / USceneComponent 区别
- 反射系统
- GC 与 UPROPERTY
- TObjectPtr / TWeakObjectPtr / TSoftObjectPtr
- CDO
- Constructor / BeginPlay / Tick / EndPlay
- SpawnActor / Destroy
- Delegate / Interface
- Module / Build.cs / Target.cs
```

## Gameplay 架构

```text
- GameInstance / GameMode / GameState
- PlayerController / PlayerState / Pawn
- Subsystem
- ActorComponent 能力组合
- Gameplay Tags
- DataAsset / DataTable
- SaveGame
```

## 资源与内容管线

```text
- Asset Manager
- Primary Asset
- Soft Reference
- Async Loading
- Bundle
- 编辑器数据验证工具
```

## 多人网络

```text
- Server Authoritative
- Actor Replication
- Property Replication
- RPC
- OnRep
- PlayerState vs PlayerController
- Dedicated Server
- Network Insights
- Replication Graph / Iris 基本概念
```

## GAS

```text
- AbilitySystemComponent
- AttributeSet
- GameplayAbility
- GameplayEffect
- GameplayCue
- Gameplay Tags
- Ability Task
- 技能授予与输入激活
```

## UI

```text
- UMG
- ViewModel / MVVM
- CommonUI
- Slate
- UI 性能
- Slate Insights
```

## 性能与调试

```text
- stat unit / stat game / stat fps
- Unreal Insights
- Timing Insights
- Memory Insights
- Low-Level Memory Tracker
- Network Insights
- Tick 优化
- 异步加载优化
```

## 工程与质量

```text
- Editor Module
- Plugin
- 自动化测试
- Functional Test
- 打包
- Dedicated Server 构建
- README / 技术文档 / 性能报告
```

---

# 13. 暂时不要深挖的方向

除非岗位明确需要，否则这 24 周内不要把主线时间砸在这些方向上：

```text
1. 修改 UE 引擎源码
2. 深入渲染管线源码
3. Nanite / Lumen 底层实现
4. Mass Entity 大型模拟
5. 完整 Online Subsystem / EOS 商业级接入
6. 大型开放世界 World Partition
7. 复杂动画蓝图和 Motion Matching
8. 完整商业级编辑器插件产品
```

它们不是不重要，而是短期内不如以下内容对中高级客户端面试直接：

```text
UE C++ 架构
多人复制
资源管理
性能分析
工具链
作品集表达
```

---

# 14. 每周复盘模板

每周末固定写：

```markdown
## 本周完成

- 

## 本周最重要的技术点

- 

## 我踩的坑

- 

## 我如何定位问题

- 

## 如果面试官问这个模块，我会怎么讲

- 

## 下周风险

- 
```

---

# 15. 面试演示顺序

推荐 10 分钟讲解顺序：

```text
1. 30 秒：项目是什么，不讲玩法细节，直接讲技术目标。
2. 1 分钟：模块结构与 C++ / Blueprint 分工。
3. 1 分钟：Gameplay Framework 和组件架构。
4. 1 分钟：数据驱动与 Asset Manager。
5. 1 分钟：GAS / 技能 / 交互系统。
6. 1.5 分钟：多人同步与 Dedicated Server。
7. 1 分钟：UI 架构。
8. 1.5 分钟：Unreal Insights 性能优化前后对比。
9. 1 分钟：Editor 工具与自动化测试。
10. 30 秒：项目不足和下一步计划。
```

---

# 16. 最重要的一句话

中高级 UE 客户端不是“会更多节点、会更多 API”，而是：

```text
能把 UE 的系统拆清楚，
能用 C++ 做稳定的底层架构，
能让 Blueprint 成为安全的内容配置层，
能用工具证明性能问题和优化结果，
能在多人、资源、UI、工具链之间做工程取舍。
```
