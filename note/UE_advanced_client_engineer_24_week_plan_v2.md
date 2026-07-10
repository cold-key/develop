# 中高级 UE 客户端开发工程师 24 周成长计划 V2

> **目标版本**：UE 5.8  
> **总周期**：24 周  
> **每周投入**：30–40 小时，总投入约 720–960 小时  
> **目标岗位**：以 UE C++ Gameplay / 客户端开发为主，具备多人网络、UI/工具、AI/性能的完整工程能力  
> **主项目**：Networked Outpost（联机前哨基地）  
> **核心原则**：A 线深挖，B/C/D 全部达到可独立实现、可调试、可面试讲解的深度

---

## 目录

1. [本次调整结论](#1-本次调整结论)
2. [四条能力主线与权重](#2-四条能力主线与权重)
3. [最终能力目标](#3-最终能力目标)
4. [每周 30–40 小时的使用方式](#4-每周-3040-小时的使用方式)
5. [项目与模块架构](#5-项目与模块架构)
6. [24 周总览](#6-24-周总览)
7. [阶段一：工程基础与最小纵切，第 1–4 周](#7-阶段一工程基础与最小纵切第-14-周)
8. [阶段二：数据、资源、存档与内容管线，第 5–8 周](#8-阶段二数据资源存档与内容管线第-58-周)
9. [阶段三：A 线——GAS 与 Gameplay 架构深挖，第 9–13 周](#9-阶段三a-线gas-与-gameplay-架构深挖第-913-周)
10. [阶段四：B 线——多人网络与 Dedicated Server，第 14–17 周](#10-阶段四b-线多人网络与-dedicated-server第-1417-周)
11. [阶段五：D 线——AI、调度与性能，第 18–20 周](#11-阶段五d-线ai调度与性能第-1820-周)
12. [阶段六：C 线——UI 架构与编辑器工具，第 21–22 周](#12-阶段六c-线ui-架构与编辑器工具第-2122-周)
13. [阶段七：质量、构建与面试交付，第 23–24 周](#13-阶段七质量构建与面试交付第-2324-周)
14. [贯穿全程的工程要求](#14-贯穿全程的工程要求)
15. [六个阶段验收里程碑](#15-六个阶段验收里程碑)
16. [作品集最终交付物](#16-作品集最终交付物)
17. [面试能力清单](#17-面试能力清单)
18. [范围控制与降级策略](#18-范围控制与降级策略)
19. [官方资料索引](#19-官方资料索引)

---

# 1. 本次调整结论

原计划的技术方向基本正确，但按照普通业余投入设计时，存在以下问题：

1. 网络、测试、打包介入过晚。
2. GAS、网络、UI、AI、工具、性能被平均展开，缺少明确主线。
3. Replication Graph、Iris、MVVM、Slate 等高级系统都被当作硬性深挖内容，容易造成广而不深。
4. 缺少调试诊断、UE::Tasks、版本控制、Cook/UAT、GPU 基础分析。
5. 单周任务缺少“完成定义”，容易停留在 API 跑通而非工程能力。

在每周能够投入 30–40 小时的前提下，本计划不再删掉 A/B/C/D 中的任何一项，而是采用：

```text
A：重点深挖，形成你的面试主标签。
B：达到可独立完成服务器权威联机原型的深度。
C：达到可设计事件驱动 UI 和实用编辑器工具的深度。
D：达到可实现 AI 任务系统并以数据证明优化效果的深度。
```

计划仍然保持 24 周，但改为：

```text
先建立工程底座
→ 完成最小纵切
→ 深挖 GAS / Gameplay
→ 网络化核心系统
→ 构建 AI 和性能场景
→ 完成 UI 与工具
→ 用测试、构建、文档和演示收口
```

---

# 2. 四条能力主线与权重

## A：GAS + Gameplay 架构，第一主线，约 35%

目标不是“会用 GAS 节点”，而是能够设计：

```text
Enhanced Input
→ 输入语义
→ Ability 激活
→ Tag 条件判断
→ Cost / Cooldown
→ Ability Task
→ Gameplay Event
→ Server Authority / Prediction
→ Gameplay Effect
→ Gameplay Cue
→ UI 状态更新
```

必须掌握：

- ASC 放在 Pawn、PlayerState、普通 Actor 上的取舍。
- AttributeSet 初始化、修改和复制。
- Ability 激活、取消、阻塞、并发和生命周期。
- Gameplay Effect 的 Instant / Duration / Infinite。
- Gameplay Tags、Tag Query、Tag Relationship。
- Cost、Cooldown、SetByCaller、Execution Calculation 基础。
- Ability Task 和至少一个自定义 Ability Task。
- Ability Set / Ability Definition 数据驱动授予。
- GAS 与普通 ActorComponent 的边界。
- GAS 的服务器权威、复制和预测基础。
- Lyra 中 Input → Ability、Ability Set、Tag Relationship 的实现思路。

最终主打能力：

> 能以 GAS 为中心，设计可扩展、数据驱动、支持联机的 Gameplay 能力架构，同时知道哪些系统不应该使用 GAS。

---

## B：网络 + Dedicated Server，约 25%

必须掌握：

- Authority、Local Role、Remote Role。
- Actor Ownership 与 Owning Connection。
- Server / Client / NetMulticast RPC。
- 属性复制与 RepNotify。
- Replicated Component / Replicated Subobject。
- `FFastArraySerializer`。
- Relevancy、Priority、Dormancy。
- CharacterMovement 基础网络模型。
- 延迟、丢包、重复请求和服务器校验。
- Dedicated Server 构建与双客户端测试。
- Network Insights。
- Replication Graph 基础实现。
- Iris 保持概念和实验性了解，不作为项目核心依赖。

最终主打能力：

> 能将已有单机 Gameplay 架构改造成服务器权威架构，并解释所有权、复制粒度、安全校验和扩展策略。

---

## C：UI + 编辑器工具，约 15%

必须掌握：

- UMG 生命周期。
- C++ UI 后端与 Blueprint Widget 表现层分工。
- 事件驱动更新，避免 Tick 和复杂 Property Binding。
- Presenter / ViewModel 思想。
- UMG MVVM 的使用与限制。
- CommonUI 的页面栈、输入路由和手柄导航。
- Slate 基础。
- Editor Module。
- Data Validation。
- 实用的资产检查与定位工具。
- Slate Insights / Widget Reflector 基础。

最终主打能力：

> 能让 UI 不直接依赖杂乱 Gameplay 对象，并能开发提高内容生产效率的编辑器工具。

---

## D：AI + 大规模调度与性能，约 15%

必须掌握：

- 简单状态机、Behavior Tree、StateTree 的适用边界。
- Worker 任务数据与执行器分离。
- 任务队列、任务取消、目标失效处理。
- 导航、感知或查询的基础用法。
- 集中调度代替所有 Actor 每帧扫描。
- Timer、事件驱动、批处理、对象池。
- UE::Tasks 的线程边界。
- Unreal Insights。
- CPU、GameThread、RenderThread、GPU Bound 的初步判断。
- 大量 Actor / Component / Tick 的优化。
- ISM/HISM 基础。

最终主打能力：

> 能实现可保存、可复制的 Worker 任务系统，并使用 Trace 数据证明调度优化效果。

---

## 其余 10%：底层与工程质量

包括：

- UObject、反射、GC、生命周期。
- UBT、Build.cs、Target.cs、模块依赖。
- Git LFS / Perforce 基本认知。
- 日志、断言、Visual Logger、Gameplay Debugger。
- 自动化测试与 Functional Test。
- Cook、Package、RunUAT、命令行测试。
- 基础动画链路。
- 技术文档、演示和面试表达。

---

# 3. 最终能力目标

24 周结束后，不以“学完所有系统”为验收，而以以下能力为验收。

## 独立设计能力

能够从需求出发回答：

```text
这个状态由谁拥有？
客户端还是服务器能够修改？
是否需要复制？
使用 Actor、Component、UObject 还是 Subsystem？
使用普通组件还是 GAS？
使用硬引用、软引用还是 Primary Asset？
UI 如何收到变化？
如何测试？
如何分析性能？
如何在打包版本复现问题？
```

## 独立实现能力

能够独立完成：

```text
输入
→ 交互
→ Ability
→ 服务器校验
→ 状态复制
→ UI 更新
→ 存档
→ AI 使用该状态
→ 性能分析
→ 自动化测试
→ Dedicated Server 打包
```

## 独立排错能力

能够使用：

```text
UE_LOG
check / ensure
断点与调用栈
Visual Logger
Gameplay Debugger
Unreal Insights
Network Insights
Memory Insights
Slate Insights
控制台命令
网络模拟
Cook / Package 日志
```

## 面试表达能力

每个核心模块都能够说明：

```text
需求是什么
第一版怎么设计
遇到什么问题
如何定位
为什么这样修改
替代方案是什么
当前方案的边界是什么
如果项目规模扩大将如何演进
```

---

# 4. 每周 30–40 小时的使用方式

## 30 小时核心投入

```text
16 小时：编码与系统集成
5 小时：官方文档、源码和示例阅读
3 小时：测试、调试与故障注入
3 小时：打包、Trace、性能或网络记录
3 小时：技术文档、图表、周复盘
```

## 额外 10 小时进阶投入

```text
4 小时：阅读 Lyra / 引擎相关源码
3 小时：完成本周进阶任务
2 小时：重构与 Code Review
1 小时：模拟面试讲解
```

## 每周固定完成定义 Definition of Done

一个功能只有满足以下条件才算完成：

```text
1. Editor PIE 中可以运行。
2. Standalone 或打包版本至少验证一次。
3. 有失败路径和日志，不只处理成功路径。
4. 至少有一个自动化测试、Functional Test 或可重复测试步骤。
5. 核心状态不依赖 UI 或 Level Blueprint。
6. 写清楚状态所有权与生命周期。
7. 写清楚为何使用当前 UE 系统，而不是只记录 API。
8. Git 提交可独立回滚。
```

涉及性能、网络或加载时，还必须增加：

```text
9. 保存一次 Trace 或指标记录。
10. 写清测试环境、Actor 数量、延迟或打包配置。
```

---

# 5. 项目与模块架构

## 项目主题

# Networked Outpost / 联机前哨基地

核心循环：

```text
玩家选择建筑
→ 本地显示预览
→ Ability 发起建造请求
→ 服务器验证资源、距离和位置
→ 服务器生成建筑
→ 建筑进入生产
→ Worker 自动采集与运输
→ 库存、生产和任务状态复制
→ UI 事件驱动更新
→ 世界状态可保存恢复
```

## 模块演进策略

不要第一天就拆出大量模块。

### 第 1 周初始结构

```text
Source/
├─ OutpostRuntime/
└─ OutpostEditor/
```

### 第 5～9 周边界稳定后拆分

```text
Source/
├─ OutpostCore/          # Tag、公共类型、数据定义、通用接口
├─ OutpostGameplay/      # 建筑、库存、交互、生产、Worker
├─ OutpostAbilities/     # ASC、AttributeSet、Ability、Effect、AbilityTask
├─ OutpostUI/            # UMG、CommonUI、MVVM/Presenter
└─ OutpostEditor/        # Data Validation、Slate 工具
```

依赖方向：

```text
OutpostCore
   ↑
OutpostGameplay
   ↑          ↖
OutpostAbilities  OutpostUI

OutpostEditor 可依赖所有 Runtime 模块
Runtime 模块禁止依赖 OutpostEditor
OutpostCore 禁止依赖 UMG、Slate、GameplayAbilities
```

## 主要运行时对象

```text
GameInstance
└─ UOutpostGameInstanceSubsystem
   └─ 全局配置、会话外服务

World
├─ AOutpostGameMode                # Server Only
├─ AOutpostGameState               # 全局复制状态
├─ UOutpostWorldSubsystem          # World 生命周期服务
├─ AOutpostPlayerController        # 玩家意图、本地选择、UI 模式
├─ AOutpostPlayerState             # 跨 Pawn、可复制玩家状态、ASC
└─ AOutpostCharacter
   ├─ UOutpostInteractionComponent
   ├─ UOutpostCommandComponent
   └─ 表现和移动相关组件
```

推荐将玩家 ASC 放在 PlayerState，Pawn 作为 Avatar Actor；建筑或 Worker 根据生命周期决定使用独立 ASC 或普通组件。

## 作品集目录

```text
UEAdvancedClientPortfolio/
├─ Source/
├─ Config/
├─ Content/
│  ├─ Data/
│  ├─ Gameplay/
│  ├─ UI/
│  ├─ Maps/
│  └─ Tests/
├─ Docs/
├─ Scripts/
│  ├─ BuildDevelopment.bat
│  ├─ RunTests.bat
│  └─ BuildServerAndClients.bat
├─ SavedProfiling/
├─ Builds/
├─ README.md
└─ DemoVideo.mp4
```

---

# 6. 24 周总览

| 周 | 主线 | 核心成果 |
|---|---|---|
| 1 | 工程底座 | 模块、构建、版本控制、日志和首次打包 |
| 2 | UObject | 反射、GC、生命周期、指针语义 |
| 3 | Framework | Gameplay Framework、Component、Subsystem、诊断 |
| 4 | 最小纵切 | Enhanced Input、交互命令、权威边界、基础测试 |
| 5 | 数据驱动 | DataAsset、Gameplay Tags、Primary Asset |
| 6 | 资源管线 | Asset Manager、异步加载、Cook 验证 |
| 7 | 核心 Gameplay | 库存、建筑、生产、事件驱动 UI |
| 8 | 持久化与工具 | SaveGame、版本兼容、Data Validation |
| 9 | GAS 1 | ASC、AttributeSet、初始化与所有权 |
| 10 | GAS 2 | Ability、Effect、Cost、Cooldown、Cue |
| 11 | GAS 3 | Ability Task、Target Data、取消和事件 |
| 12 | GAS 4 | Ability Set、数据驱动、输入和 Tag Relationship |
| 13 | GAS 5 | 网络预测、复制、安全、Lyra 对照与重构 |
| 14 | 网络 1 | Authority、Ownership、RPC、属性复制 |
| 15 | 网络 2 | Fast Array、子对象、Dormancy、Relevancy |
| 16 | 网络 3 | 网络化建造、交互、GAS、延迟与校验 |
| 17 | 网络 4 | Dedicated Server、Network Insights、Replication Graph |
| 18 | AI 1 | Worker 任务模型、StateTree/BT、导航和动画基础 |
| 19 | AI 2 | 任务调度、保存、复制、故障恢复 |
| 20 | 性能 | Insights、UE::Tasks、批处理、ISM、GPU 基础 |
| 21 | UI | 事件驱动 UMG、Presenter/MVVM、CommonUI |
| 22 | 工具 | Slate、Editor Tab、数据验证、UI 性能 |
| 23 | 质量与构建 | 自动化、Functional Test、RunUAT、CI 脚本 |
| 24 | 作品集 | 最终优化、README、视频、面试材料 |

---

# 7. 阶段一：工程基础与最小纵切，第 1–4 周

---

## 第 1 周：工程、构建、版本控制与第一份可运行包

### 核心目标

建立可以持续迭代六个月的项目底座，而不是立即堆 Gameplay 功能。

### 学习内容

- `.uproject`、Module、Plugin 基本结构。
- UBT、UHT、Build.cs、Target.cs。
- Public / Private 依赖。
- Development Editor、Development、DebugGame、Shipping。
- Git LFS 或 Perforce 基础。
- `.gitignore`、二进制资产冲突。
- Log Category。
- Editor、Standalone、Packaged Build 的差异。

### 实操

```text
1. 创建 OutpostRuntime 和 OutpostEditor。
2. 配置 Public / Private 目录。
3. 创建自定义日志类别：
   LogOutpost
   LogOutpostAbility
   LogOutpostNetwork
   LogOutpostAI
   LogOutpostUI
4. 建立 Git LFS 与提交规范。
5. 添加一张启动地图和最小 GameMode。
6. 完成第一次 Development 打包。
7. 编写 BuildDevelopment.bat。
```

### 必须产出

```text
Docs/01_ProjectBuildAndSourceControl.md
Scripts/BuildDevelopment.bat
Builds/Week01/
```

### 验收

- 删除 Intermediate 和 Binaries 后可以重新生成项目并编译。
- OutpostEditor 不进入 Runtime 包。
- 打包程序可以启动到目标地图。
- 能解释 Build.cs 与 Target.cs 的职责差异。
- 能解释为什么 `.uasset` 冲突不能像文本代码一样直接合并。

### 进阶任务

- 创建一个最简单的 Runtime Plugin。
- 比较 Project Module 和 Plugin Module 的适用场景。
- 使用 Include What You Use 思路清理头文件。

---

## 第 2 周：UObject、反射、GC、生命周期和指针语义

### 学习内容

- UObject 与普通 C++ 对象。
- UCLASS、USTRUCT、UENUM、UPROPERTY、UFUNCTION。
- CDO。
- `NewObject`、`CreateDefaultSubobject`、`SpawnActor`。
- Actor 构造、注册、初始化、BeginPlay、EndPlay、Destroy。
- `TObjectPtr`、裸 `UObject*`、`TWeakObjectPtr`、`TSoftObjectPtr`。
- `TSubclassOf`、`TSoftClassPtr`。
- UObject 引用跟踪和 GC。
- Actor Component 生命周期。

### 实操

```text
UOutpostItemDefinition : UPrimaryDataAsset
UOutpostInventoryComponent : UActorComponent
AOutpostPickupActor : AActor
FOutpostItemStack : USTRUCT
```

要求：

- 组件使用 `TObjectPtr` 保存默认子对象引用。
- Definition 使用软引用保存图标、Mesh 和表现类。
- 局部临时引用与成员持有引用使用不同指针类型。
- 观察对象销毁、弱引用失效和 EndPlay。
- 使用 `ensure` 捕获错误配置。
- 不使用“随便加 UPROPERTY”解决所有生命周期问题。

### 必须产出

```text
Docs/02_UObjectReflectionGCLifecycle.md
Tests/InventoryDataTypes
```

### 验收

能够独立回答：

```text
1. 为什么普通 struct 不需要继承 UObject？
2. UPROPERTY 为什么不只是给蓝图使用？
3. 裸 UObject* 什么时候合理？
4. Soft Reference 什么时候可能返回空？
5. 构造函数、OnRegister、PostInitializeComponents、BeginPlay 如何分工？
6. CDO 为什么不能保存单个运行实例的状态？
```

### 进阶任务

- 使用 `FGCObject` 或查阅 AddReferencedObjects。
- 观察热重载或 Live Coding 对 CDO 默认值的影响。
- 阅读 `UObjectGlobals` 中对象创建相关代码入口。

---

## 第 3 周：Gameplay Framework、组件化、Subsystem 与调试诊断

### 学习内容

- GameInstance、World、GameMode、GameState。
- PlayerController、PlayerState、Pawn、Character。
- LocalPlayer 与 LocalPlayerSubsystem。
- ActorComponent 能力组合。
- GameInstanceSubsystem、WorldSubsystem、LocalPlayerSubsystem。
- Interface、Native Delegate、Dynamic Delegate。
- `check`、`ensure`、日志等级。
- Visual Logger、Gameplay Debugger 基础。

### 实操

实现空壳并明确职责：

```text
AOutpostGameMode
AOutpostGameState
AOutpostPlayerController
AOutpostPlayerState
AOutpostCharacter
UOutpostGameInstanceSubsystem
UOutpostWorldSubsystem
UOutpostInteractionComponent
UOutpostProductionComponent
```

要求：

- 为每个类写 2～5 行职责注释。
- 禁止创建没有明确生命周期理由的 Manager。
- 使用 Native Delegate 传播运行时状态。
- 为交互组件增加 Visual Logger 快照。
- 在 Gameplay Debugger 中显示当前交互目标或玩家资源。

### 必须产出

```text
Docs/03_GameplayFrameworkAndDiagnostics.md
Docs/03_ObjectOwnershipDiagram.drawio 或 PNG
```

### 验收

- 能解释 PlayerState 和 PlayerController 的状态边界。
- 能解释 GameMode 为什么客户端不存在。
- 能解释 Subsystem 为什么不是所有 Manager 的默认答案。
- UI 代码尚未出现，Gameplay 状态仍能被日志和 Debugger 观察。
- 具备一条可复现的错误定位记录。

### 进阶任务

- 自定义 Gameplay Debugger Category。
- 比较 UE Interface 和纯 C++ 接口。
- 阅读 Lyra 的 PlayerState、Pawn Extension 或 Component Manager 结构。

---

## 第 4 周：Enhanced Input、交互命令与服务器权威边界

### 学习内容

- Input Action、Input Mapping Context。
- Trigger、Modifier 和 Mapping 优先级。
- LocalPlayerSubsystem 添加 IMC。
- Character / Controller 输入职责。
- 输入语义与 Gameplay 命令分离。
- 客户端请求与权威执行的设计。
- 自动化测试基础。

### 实操

实现：

```text
UOutpostInputConfig
UOutpostInteractionComponent
UOutpostCommandComponent
UOutpostInteractableInterface
FOutpostInteractionQuery
FOutpostInteractionResult
FOutpostCommandRequest
FOutpostCommandResult
```

链路：

```text
E / 鼠标点击
→ Input Action
→ PlayerController 形成玩家意图
→ Interaction Query
→ Command Request
→ Authority Execute 接口
→ Result / Failure Reason
```

本周可以仍在单机运行，但 API 必须按照服务器权威设计：

```text
RequestPlaceBuilding()
ValidatePlaceBuilding()
ExecutePlaceBuilding()
```

不能把验证和执行全部写在 UI 或输入回调里。

### 必须产出

```text
Docs/04_InputInteractionCommandAuthority.md
Tests/InteractionQuery
```

### 验收

- 输入层不知道库存具体实现。
- 交互对象通过 Interface 或明确抽象调用。
- 命令有成功、目标无效、距离不足、条件不满足等失败结果。
- 本地表现与真实状态修改入口分开。
- 至少一个 C++ Automation Test 可通过命令行或 Editor 运行。

### 进阶任务

- 支持交互优先级和多个候选目标。
- 使用 Gameplay Tags 描述交互能力。
- 阅读 Lyra 的 Input Config 到 Ability 输入绑定路径。

---

# 8. 阶段二：数据、资源、存档与内容管线，第 5–8 周

---

## 第 5 周：DataAsset、Gameplay Tags 与 Primary Asset

### 学习内容

- DataAsset 与 DataTable。
- Primary Asset 与 Secondary Asset。
- `FPrimaryAssetId`。
- Gameplay Tag、Tag Container、Tag Query。
- Native Gameplay Tags。
- 硬引用与软引用造成的依赖。
- Asset Audit / Reference Viewer / Size Map。

### 实操

实现：

```text
UOutpostItemDefinition
UOutpostBuildingDefinition
UOutpostWorkerDefinition
UOutpostAbilityDefinition
```

建议字段：

```text
PrimaryAssetId
DisplayName
Description
Icon
GameplayTags
RuntimeClass
VisualClass
Costs
Soft References
```

建立 Tag 体系：

```text
Item.Resource.Wood
Item.Resource.Ore
Building.Production.Sawmill
Building.Storage.Warehouse
Ability.Build.Place
Ability.Resource.Collect
Ability.Worker.Assign
State.Player.Interacting
State.Building.Producing
State.Worker.Busy
Failure.Build.InsufficientResource
Failure.Build.InvalidLocation
```

### 模块重构

此时根据真实依赖，将 Runtime 拆为：

```text
OutpostCore
OutpostGameplay
```

暂不急于拆 Ability 和 UI 模块。

### 必须产出

```text
Docs/05_DataDrivenDesignAndTags.md
Content/Data/
```

### 验收

- 代码中不存在物品类型字符串比较。
- 数据资产不直接保存运行时实例状态。
- 能解释 Tag 与 Enum 各自适用场景。
- 使用 Reference Viewer 确认一个 Definition 没有意外拖入大量资源。
- Primary Asset ID 在存档和运行时查询中保持稳定。

### 进阶任务

- 使用 Native Gameplay Tags。
- 为 Tag 命名和来源 `.ini` 制定规范。
- 编写 Tag Query 组合条件测试。

---

## 第 6 周：Asset Manager、异步加载、Cook 与加载失败

### 学习内容

- 自定义 `UAssetManager`。
- Primary Asset Type 扫描。
- Streamable Manager。
- `FStreamableHandle`。
- Asset Bundle。
- 异步加载回调和对象生命周期。
- Cook 规则。
- Editor 中存在但包中缺失的原因。
- 启动加载与按需加载策略。

### 实操

实现：

```text
UOutpostAssetManager
FOutpostAssetLoadRequest
```

功能：

```text
1. 启动时只加载轻量 Definition。
2. 打开建筑列表时加载 Icon Bundle。
3. 确认放置前加载 Gameplay / World Bundle。
4. 处理取消、重复请求、失败和调用者销毁。
5. 记录加载开始、结束、失败和耗时。
6. 完成第二次 Development Cook + Package。
```

### 必须产出

```text
Docs/06_AssetManagerAsyncLoadingAndCook.md
SavedProfiling/Week06_AssetLoading.utrace
Builds/Week06/
```

### 验收

- 不在 Widget Construct 或 Actor 构造中同步加载大量资产。
- 打包版本能够正确找到 Primary Asset。
- 失败时 UI 或调用者得到明确错误，不会永久停在 Loading。
- 能通过 Reference Viewer 和 Asset Audit 分析依赖。
- 能解释软引用降低的是不必要的加载依赖，而不是自动解决所有内存问题。

### 进阶任务

- 实现请求合并或简单缓存。
- 比较直接使用 AssetManager 与再封装 Subsystem 的必要性。
- 输出一次同步加载与异步加载的 Trace 对比。

---

## 第 7 周：库存、建筑、生产与第一个完整纵切

### 学习内容

- 聚合根与状态所有权。
- Component API 设计。
- 事件驱动状态变化。
- Timer 与 Tick。
- 原子操作和失败原因。
- UMG 最小展示层。

### 实操

实现：

```text
UOutpostInventoryComponent
UOutpostBuildingComponent
UOutpostProductionComponent
AOutpostBuilding
AOutpostResourceNode
```

完整链路：

```text
选择建筑
→ 检查配置
→ 检查库存
→ 本地放置预览
→ Authority API 校验
→ 扣除资源
→ 生成建筑
→ Timer 驱动生产
→ 添加产物
→ Delegate 通知 UI
```

UI 本周只做最小版本：

- 当前资源。
- 建筑菜单。
- 失败原因。
- 生产进度。

禁止：

- UI Tick 查询库存。
- Widget 直接修改 Inventory。
- 用 Level Blueprint 连接核心逻辑。

### 必须产出

```text
Docs/07_CoreGameplayVerticalSlice.md
Demo/Week07_VerticalSlice.mp4
Tests/InventoryAndBuildingCost
```

### 验收

- 纵切可从启动到生产完成。
- 所有失败结果可观察。
- Inventory Add/Remove/Stack 有测试。
- Building Cost 有测试。
- Standalone 与打包版本可运行。
- 生产逻辑不依赖帧率。

### 进阶任务

- 使用交易式接口避免扣一半资源后失败。
- 建筑放置支持碰撞、坡度和范围验证。
- 增加基础 Animation Montage / Notify，用于采集表现。

---

## 第 8 周：SaveGame、版本兼容与 Data Validation

### 学习内容

- 保存可重建数据，而不是保存 Actor 实例。
- Stable ID。
- Save Version。
- 世界恢复顺序。
- 异步保存基础。
- `UDataValidation` / Asset Validation。
- Editor Module 与 Runtime 边界。

### 实操

实现：

```text
UOutpostSaveGame
FOutpostBuildingSaveData
FOutpostInventorySaveData
FOutpostProductionSaveData
FOutpostWorkerSaveData
FOutpostWorldSaveData
```

保存：

- Definition ID。
- Stable Instance ID。
- Transform。
- Inventory。
- Production Queue。
- 剩余时间。
- Worker Task 基础数据。

加载：

```text
读取版本
→ 迁移旧数据
→ 创建世界对象
→ 恢复组件状态
→ 恢复对象之间引用
→ 触发 UI 刷新
```

编辑器验证：

- ID 重复。
- 必填资产为空。
- Cost 为负。
- Tag 不符合规范。
- RuntimeClass 不合法。
- 软引用资产不存在。

### 必须产出

```text
Docs/08_SaveVersioningAndDataValidation.md
OutpostEditor/DataValidator
Tests/SaveLoadRoundTrip
```

### 验收

- 保存后重新启动打包程序仍能恢复。
- 至少模拟一次 V1 → V2 迁移。
- 保存数据不直接持有运行时 Actor 指针。
- Validator 能在内容错误时给出资产和字段信息。
- 能说明加载顺序和引用恢复策略。

### 进阶任务

- 后台序列化纯数据，再回 GameThread 应用。
- 输出 Data Validation 报告文件。
- 支持双击定位错误资产。

---

# 9. 阶段三：A 线——GAS 与 Gameplay 架构深挖，第 9–13 周

> 这是整个计划投入最多、面试权重最高的阶段。  
> 五周总投入约 150–200 小时。

---

## 第 9 周：ASC、AttributeSet、Owner/Avatar 与初始化

### 学习内容

- GAS 解决的问题与适用边界。
- ASC 生命周期。
- Owner Actor / Avatar Actor。
- PlayerState ASC 与 Pawn ASC。
- `InitAbilityActorInfo`。
- AttributeSet。
- Attribute 初始化和复制。
- Gameplay Tag 与 Loose Tag。
- Gameplay Effect Spec 基础。

### 实操

拆出：

```text
OutpostAbilities
```

实现：

```text
UOutpostAbilitySystemComponent
UOutpostAttributeSet
UOutpostGameplayAbility
UOutpostAbilitySet
```

属性建议：

```text
Health
MaxHealth
Energy
BuildResource
CarryCapacity
MoveSpeed
```

要求：

- 玩家 ASC 放在 PlayerState。
- Character 作为 Avatar。
- Respawn 后正确重新初始化。
- Attribute 使用 RepNotify。
- 基础初始化使用 Gameplay Effect 或明确初始化策略。
- 编写属性 Clamp 和修改测试。

### 必须产出

```text
Docs/09_GASArchitectureAndInitialization.md
Docs/09_ASC_Owner_Avatar_Diagram.png
Tests/GASAttributeInitialization
```

### 验收

- 能解释 ASC 放在 PlayerState 与 Pawn 的取舍。
- Pawn 重生不会丢失应保留 Ability。
- 能解释 Attribute、普通变量和 Inventory 数据的边界。
- 初始化顺序可重复，不依赖偶然的 BeginPlay 顺序。
- 能排查 ActorInfo 未初始化导致 Ability 失败的问题。

### 进阶任务

- 研究 AbilitySystemGlobals。
- 增加属性派生关系。
- 阅读 Lyra PlayerState、Pawn Extension 和 Ability System 初始化链路。

---

## 第 10 周：Gameplay Ability、Effect、Cost、Cooldown 与 Cue

### 学习内容

- Ability Instancing Policy。
- Net Execution Policy。
- Activation Owned Tags / Required Tags / Blocked Tags。
- Gameplay Effect Duration Policy。
- Modifier。
- Cost 和 Cooldown。
- SetByCaller。
- Gameplay Cue。
- Ability Commit。
- Ability 结束和取消。

### 实操

实现三个能力：

```text
GA_Build_PlaceBuilding
GA_Resource_Collect
GA_Player_Dash 或 GA_Player_Interact
```

配套：

```text
GE_BuildCost
GE_CollectReward
GE_DashCost
GE_DashCooldown
GC_BuildPlaced
GC_CollectImpact
```

要求：

- Ability 不直接访问具体 Widget。
- 建造资源不足通过 Tag 或失败信息暴露。
- Cost 和 Cooldown 数据化。
- Cue 只负责表现，不持有权威 Gameplay 状态。
- Ability 在取消、目标失效、角色死亡时能够正确结束。

### 必须产出

```text
Docs/10_AbilityEffectCostCooldownCue.md
Tests/AbilityActivationAndCost
```

### 验收

- 能区分 Ability、Effect、Cue 的职责。
- Ability 失败不会扣除资源。
- Ability 成功只能 Commit 一次。
- 冷却 UI 可从 Gameplay Effect / Tag 状态获取。
- 能解释为什么生产系统不一定适合做成 Ability。

### 进阶任务

- 自定义 Gameplay Effect Execution Calculation。
- 使用 SetByCaller 传入建造消耗。
- 实现一个 Stack 或 Periodic Effect。

---

## 第 11 周：Ability Task、Target Data、Gameplay Event 与取消模型

### 学习内容

- Ability Task 生命周期。
- Wait Gameplay Event。
- Wait Target Data。
- Target Actor / Target Data。
- Gameplay Event。
- Ability 取消、阻塞和互斥。
- 异步节点和 Delegate。
- 自定义 Ability Task。

### 实操

实现建造能力完整链路：

```text
激活 Ability
→ 创建本地放置预览
→ 持续更新目标位置
→ 确认或取消
→ 构造 Target Data
→ 服务器验证
→ Commit
→ Spawn Building
→ Cue
→ End Ability
```

至少实现一个自定义任务：

```text
UAbilityTask_WaitValidBuildingPlacement
```

或：

```text
UAbilityTask_WaitOutpostInteractionTarget
```

要求：

- Task 结束时解除 Delegate。
- Avatar 销毁时安全退出。
- 取消操作不遗留预览 Actor。
- 目标失效有明确失败结果。

### 必须产出

```text
Docs/11_AbilityTasksTargetDataAndCancellation.md
Tests/AbilityCancelCleanup
```

### 验收

- 能解释 Ability Task 为什么不是普通 AsyncTask。
- 能处理 Ability 被外部 Tag 或死亡状态取消。
- 自定义 Task 不产生悬空回调。
- Target Data 不直接信任客户端。
- Ability 结束路径覆盖成功、取消、失败、Owner 销毁。

### 进阶任务

- 编写自定义 Target Data Struct。
- 使用 Scoped Prediction Window 做实验。
- 阅读 Lyra 的 Target Data 或 Weapon Ability 相关实现。

---

## 第 12 周：数据驱动 Ability Set、输入绑定与 Tag Relationship

### 学习内容

- Ability Set。
- Ability Definition。
- Input Tag。
- Ability Input Buffer / Pressed / Released。
- Tag Relationship Mapping。
- Grant / Remove Ability。
- Ability 来源追踪。
- Data Asset 驱动的能力组合。

### 实操

实现：

```text
UOutpostAbilitySet
UOutpostAbilityDefinition
UOutpostAbilityGrantComponent
UOutpostAbilityTagRelationshipMapping
```

配置：

```text
Player Definition
→ Build / Interact / Dash Ability Set

Worker Definition
→ Collect / Carry / Deposit Ability Set

Building Definition
→ 可选的主动能力或状态 Effect
```

输入链路：

```text
IA_Build
→ Input Tag
→ ASC Input Pressed
→ Ability Spec 匹配
→ TryActivateAbility
```

要求：

- 输入配置不硬编码 Ability Class。
- Ability 可由装备、角色定义或临时状态授予。
- 移除来源时只移除由该来源授予的能力。
- Tag Relationship 控制阻塞和取消。
- 普通生产逻辑继续留在 Component，不强行 GAS 化。

### 必须产出

```text
Docs/12_DataDrivenAbilityInputAndTags.md
Tests/AbilityGrantRemove
```

### 验收

- 更换 Player Definition 可以改变能力组合。
- 输入层不知道具体 Ability 类。
- Ability 授予和移除没有重复或残留。
- 能画出 Enhanced Input 到 Ability 激活链路。
- 能清楚列出项目中“使用 GAS”和“不使用 GAS”的系统。

### 进阶任务

- 加入 Ability Level。
- 设计 Ability Source Object。
- 对照 Lyra Ability Set 和 Tag Relationship Mapping。

---

## 第 13 周：GAS 网络预测、复制、安全与架构复盘

### 学习内容

- Local Predicted、Server Only、Server Initiated。
- Prediction Key 基础。
- Ability / Effect / Cue 的复制。
- 客户端预测与服务器权威。
- 错误预测回滚概念。
- GAS Debugger、Gameplay Debugger。
- Lyra GAS 架构对照。

### 实操

对建造或 Dash 做预测实验：

```text
本地立即播放表现或显示确认反馈
→ 服务器验证
→ 接受则同步真实结果
→ 拒绝则撤销本地表现并显示原因
```

故障注入：

- 延迟 150ms。
- 丢包。
- 重复按键。
- 越距请求。
- 资源不足但客户端数据滞后。
- Ability 激活中 Pawn 被销毁。

架构复盘：

```text
1. 哪些能力使用预测？
2. 哪些能力必须 Server Only？
3. 哪些状态放 Attribute？
4. 哪些状态放 Inventory / Component？
5. Cue 与普通事件表现如何分工？
```

### 必须产出

```text
Docs/13_GASPredictionReplicationSecurity.md
Docs/13_LyraGASComparison.md
SavedProfiling/Week13_GASNetworkSession.utrace
```

### 验收

- 能解释“预测不等于信任客户端”。
- 延迟下能力不会重复扣费或重复生成 Actor。
- 服务器拒绝能够清理本地预测表现。
- 使用 Gameplay Debugger 或 GAS Debug 命令观察 Ability、Tag、Effect。
- 能以 10 分钟完整讲解项目 GAS 架构。

### 进阶任务

- 研究 Minimal / Mixed / Full Replication Mode。
- 对比 Lyra 的 ASC 子类与项目实现。
- 写一份“为什么不把 Worker 生产系统全部改成 GAS”的技术决策记录。

---

# 10. 阶段四：B 线——多人网络与 Dedicated Server，第 14–17 周

---

## 第 14 周：Authority、Ownership、RPC、RepNotify 与测试环境

### 学习内容

- Client-Server 模型。
- Authority。
- Autonomous Proxy / Simulated Proxy。
- Actor Ownership。
- Owning Connection。
- RPC 调用条件。
- RepNotify。
- Listen Server 与 Dedicated Server。
- PIE 多进程与网络模拟。

### 实操

建立网络测试地图和流程：

```text
Server + Client A + Client B
```

网络化：

- PlayerState 资源。
- GameState 全局阶段。
- Building Spawn。
- Inventory 修改入口。
- 交互请求。
- UI 读取复制状态。

统一状态通知：

```text
Server 本地修改
→ HandleStateChanged()

Client OnRep
→ HandleStateChanged()
```

### 必须产出

```text
Docs/14_NetworkAuthorityOwnershipRPC.md
Tests/NetworkTestChecklist.md
```

### 验收

- 客户端不能直接修改权威库存。
- 能解释为什么 Client RPC 必须有正确 Owning Connection。
- Server 本地 UI/逻辑不依赖 OnRep 是否调用。
- 能区分 RPC、属性复制和 Gameplay Cue 的使用场景。
- 两个客户端看到一致建筑和资源状态。

### 进阶任务

- 加入 RPC Validation 风格的显式服务器检查。
- 编写网络角色日志。
- 使用不同 Net Mode 运行同一测试用例。

---

## 第 15 周：Fast Array、复制组件/子对象、Relevancy 与 Dormancy

### 学习内容

- Replicated Component。
- Replicated Subobject。
- `FFastArraySerializer`。
- Delta Serialization。
- Actor Relevancy。
- Net Priority / Net Update Frequency。
- Dormancy。
- 条件复制。
- 动态 Actor 生命周期。

### 实操

使用 Fast Array 实现至少一个：

```text
Inventory Items
Production Queue
Worker Task Queue
```

对建筑和资源节点实现：

- 空闲建筑进入 Dormancy。
- 状态改变时 Flush Dormancy。
- 远距离资源节点降低更新频率。
- Owner-only 数据使用条件复制。
- 组件或 UObject 子对象正确注册复制。

### 必须产出

```text
Docs/15_FastArraySubobjectDormancyRelevancy.md
SavedProfiling/Week15_NetworkBaseline.utrace
Tests/FastArrayReplicationChecklist.md
```

### 验收

- 能解释为什么不能无脑复制整个大数组。
- 新增、修改、删除项能够在客户端正确回调。
- Dormant Actor 状态变化后能够恢复复制。
- 非相关客户端不会收到不必要数据。
- 能解释 Actor、Component、Subobject 的复制边界。

### 进阶任务

- 对比传统复制与 Iris 下子对象注册差异。
- 对 Fast Array 编写客户端 UI 增量更新。
- 测量 50、200、500 个复制对象的流量变化。

---

## 第 16 周：网络化建造、交互、GAS 与安全校验

### 学习内容

- 服务器验证。
- 防重复请求。
- 距离、资源、目标和状态校验。
- 客户端表现与服务器结果。
- GAS 与普通 RPC 的组合。
- 网络延迟和丢包下的 UX。

### 实操

完成联机核心循环：

```text
Client 选择建筑
→ 本地预览
→ Ability / RPC 发送请求
→ Server 验证位置、资源、Tag、冷却
→ Server Commit / Spawn
→ Actor Replication
→ Inventory Fast Array 更新
→ Client UI 更新
```

Worker 指令：

```text
Client 选择 Worker
→ Command Request
→ Server Ownership / Team 校验
→ Server 分配任务
→ Task State 复制
```

作弊测试：

- 越距采集。
- 修改客户端资源显示。
- 伪造无权限 Worker。
- 快速重复提交。
- 无效 Definition ID。
- 非法 Transform。
- 已销毁目标。

### 必须产出

```text
Docs/16_NetworkedGameplaySecurity.md
Demo/Week16_TwoClientGameplay.mp4
Tests/ServerAuthorityFunctionalTests
```

### 验收

- 所有权威状态最终只由服务器改变。
- 客户端预测失败能够恢复。
- 重复 RPC 不会重复扣费或生成。
- 服务器日志能指出拒绝原因。
- 150ms 延迟下仍有合理反馈。

### 进阶任务

- 为命令增加序列号或幂等处理。
- 对关键 RPC 增加频率限制思路。
- 编写网络状态机图。

---

## 第 17 周：Dedicated Server、Network Insights 与复制扩展

### 学习内容

- Server Target。
- Client / Server Build。
- 启动参数。
- Network Insights。
- RPC 和属性流量分析。
- Replication Graph。
- Iris 当前定位和迁移概念。
- Server Travel 基础。

### 实操

```text
1. 构建 Windows Dedicated Server。
2. 启动 Server + 两个独立 Client。
3. 运行完整建造、采集、生产循环。
4. 使用 Network Insights 记录会话。
5. 生成 200 个资源点、50 个 Worker、100 个建筑。
6. 实现一个最小 Replication Graph：
   - Always Relevant 玩家状态
   - 空间化建筑和资源
   - 距离或频率策略
7. 对 Iris 做单独实验分支或阅读验证，不将其作为主分支依赖。
```

### 必须产出

```text
Docs/17_DedicatedServerAndNetworkScaling.md
Scripts/BuildServerAndClients.bat
Scripts/RunLocalMultiplayer.bat
SavedProfiling/Week17_NetworkInsights.utrace
Builds/Week17_ServerAndClients/
```

### 验收

- 独立 Server 和 Client 可由脚本启动。
- 能定位带宽最高的 Actor、属性或 RPC。
- 能说明 Replication Graph 解决的是连接相关对象筛选成本，不是替代所有复制设计。
- 能说明 Iris 是可选复制系统，项目为何不把实验性能力作为核心依赖。
- 能给出下一步支持更多玩家时的优化顺序。

### 进阶任务

- Server Travel 或简单重连实验。
- 运行长时间服务器稳定性测试。
- 在单独分支尝试开启 Iris 并记录兼容问题。

---

# 11. 阶段五：D 线——AI、调度与性能，第 18–20 周

---

## 第 18 周：Worker 任务模型、StateTree/Behavior Tree 与动画基础

### 学习内容

- 状态机、Behavior Tree、StateTree。
- AIController。
- Navigation System。
- Blackboard / StateTree Context。
- 任务数据和执行器分离。
- Animation Blueprint、State Machine、Montage、Notify 基础。

### 实操

实现：

```text
AOutpostWorkerCharacter
AOutpostWorkerAIController
UOutpostTaskComponent
UOutpostWorkerBrainComponent
FOutpostTaskData
```

任务：

```text
Idle
→ MoveToResource
→ Collect
→ MoveToStorage
→ Deposit
→ Complete
```

异常：

- 目标被销毁。
- 路径失败。
- 仓库已满。
- Worker 被打断。
- 任务被更高优先级任务替换。

可选择 StateTree 作为主实现，Behavior Tree 做小型对照实验；不需要维护两套完整生产实现。

动画：

- Locomotion State Machine。
- Collect Montage。
- Notify 触发表现事件，但权威资源结算不依赖动画帧事件。

### 必须产出

```text
Docs/18_WorkerAIStateTreeAndAnimation.md
Tests/WorkerTaskStateTransitions
```

### 验收

- 任务状态是可序列化数据，不是只藏在节点内部。
- AI 目标失效后能恢复。
- 动画表现与权威 Gameplay 结算解耦。
- 能解释为何选择 StateTree 或 Behavior Tree。
- Worker Brain 不直接修改 UI。

### 进阶任务

- 使用 EQS 选择资源点。
- 使用 Smart Object 做交互点实验。
- 比较 StateTree 与 C++ 状态机的调试体验。

---

## 第 19 周：集中调度、任务队列、保存与复制

### 学习内容

- 任务发布者和执行者。
- 中央任务池。
- 事件驱动分配。
- 优先级、取消、抢占。
- AI 状态复制。
- 保存恢复中的重新绑定。
- Visual Logger 和 Gameplay Debugger。

### 实操

实现：

```text
UOutpostTaskSchedulerSubsystem 或明确生命周期的 Scheduler UObject
FOutpostTaskHandle
FOutpostTaskRequest
FOutpostTaskAssignment
```

第一版故意实现：

```text
每个 Worker Tick 扫描所有任务
```

然后重构为：

```text
任务发布事件
→ Scheduler 建立索引
→ 固定预算或事件驱动分配
→ Worker 只执行已分配任务
```

网络：

- 服务器运行 AI 决策。
- 客户端只复制必要表现状态。
- 不复制完整决策内部数据。
- 任务队列可用 Fast Array。

存档：

- 保存任务类型、目标 Stable ID、阶段和必要参数。
- 加载后重新解析目标引用。

### 必须产出

```text
Docs/19_TaskSchedulerSaveReplication.md
SavedProfiling/Week19_BeforeScheduler.utrace
SavedProfiling/Week19_AfterScheduler.utrace
```

### 验收

- 100 个 Worker 不再每帧全量扫描。
- 任务目标失效不会造成无限重试。
- Server 与 Client 的 AI 状态职责清晰。
- 存档恢复后 Worker 能继续或安全重建任务。
- Visual Logger 能显示 Worker 的任务、目标和失败原因。

### 进阶任务

- 任务空间索引。
- 每帧预算调度。
- 任务饥饿和公平性策略。
- 任务系统压力测试脚本。

---

## 第 20 周：Unreal Insights、UE::Tasks、批处理与基础 GPU 分析

### 学习内容

- GameThread、RenderThread、RHIThread。
- Tick 开销。
- Timer、事件、批处理。
- UE::Tasks。
- UObject 线程边界。
- Task Prerequisite。
- Memory Insights。
- `stat unit`、`stat game`、`stat gpu`。
- GPU Visualizer。
- Draw Call、材质、透明、LOD、ISM/HISM。
- 对象池适用边界。

### 实操

压力场景：

```text
500 个资源点
100 个 Worker
200 个建筑
持续生产和任务分配
两个客户端
```

优化实验：

```text
1. Worker 全 Tick → 集中调度。
2. 资源点 Actor → 部分使用 ISM/HISM 表现。
3. 高频更新 → 分帧或预算处理。
4. 纯数据候选计算放入 UE::Tasks。
5. 只在 GameThread 访问和修改 UObject。
6. 对 UI、网络和 AI 同时进行 Trace。
```

至少记录：

- GameThread 时间。
- Worker 调度耗时。
- Tick 数量。
- 内存占用。
- Draw Call。
- GPU 时间。
- 网络带宽。
- 打开建筑菜单耗时。

### 必须产出

```text
Docs/20_PerformanceOptimizationReport.md
SavedProfiling/Week20_Before.utrace
SavedProfiling/Week20_After.utrace
```

### 验收

- 能判断测试场景是 Game、Render 还是 GPU Bound。
- 后台 Task 不直接访问可能销毁的 UObject。
- 优化报告包含环境、规模、指标和前后对比。
- 不为了“多线程”而把轻量任务异步化。
- 至少有一项优化达到稳定可复现的明显收益。

### 进阶任务

- Memory Insights 对比。
- Slate Insights 捕获 UI 刷新。
- 自定义 Trace Channel 或 Scope。
- 对比 Actor、Mass Entity 概念，但不要求迁移项目。

---

# 12. 阶段六：C 线——UI 架构与编辑器工具，第 21–22 周

---

## 第 21 周：事件驱动 UMG、Presenter/MVVM 与 CommonUI

### 学习内容

- UUserWidget 生命周期。
- Widget 创建、添加和移除。
- Presenter / ViewModel。
- Field Notify。
- UMG MVVM。
- CommonUI Activatable Widget。
- 页面栈。
- 输入路由。
- 键鼠、手柄切换。
- UI 与网络状态。

### 架构策略

项目核心 UI 使用稳定的事件驱动接口：

```text
Gameplay / RepNotify / Delegate
→ C++ Presenter 或 ViewModel
→ Widget 更新
```

同时选取一个完整页面使用 UMG MVVM，验证：

- Field Notify。
- One Way / Two Way Binding。
- ViewModel 创建方式。
- 列表项和生命周期。

CommonUI 用于：

- 主菜单。
- 暂停菜单。
- 建筑详情页面栈。
- 输入方式切换与 Back 行为。

### 实操

实现：

```text
UOutpostHUDRoot
UOutpostInventoryPresenter / ViewModel
UOutpostBuildingMenuPresenter / ViewModel
UOutpostProductionPresenter / ViewModel
UOutpostNetworkStatusViewModel
UOutpostActivatableWidget
```

要求：

- UI 不 Tick 查询 Gameplay。
- UI 不发送任意服务器 RPC，只调用明确 Command/Ability API。
- Widget 解绑所有 Delegate。
- 异步图标加载处理 Widget 被关闭的情况。
- 支持键鼠和手柄基本导航。
- 冷却、库存、生产和网络错误状态可正确显示。

### 必须产出

```text
Docs/21_UIArchitectureMVVMCommonUI.md
Docs/21_UIDataFlowDiagram.png
Tests/UIStatePresenterTests
```

### 验收

- 打开关闭页面不会产生重复绑定。
- UI 在 Pawn 更换或重新连接后能重新绑定数据源。
- 能解释 Presenter、官方 MVVM 和原始 Property Binding 的差异。
- 能解释 CommonUI 解决的是导航和输入路由，而不是 Gameplay 数据架构。
- 无 UI Tick 和复杂 Blueprint Getter Binding。

### 进阶任务

- 分析 ListView Entry 生命周期。
- 支持本地多玩家 UI 的基础结构。
- 使用 Slate Insights 或 Widget Reflector 查找无效刷新。

---

## 第 22 周：Slate Editor Tool、数据验证与内容生产效率

### 学习内容

- Slate Declarative Syntax。
- SWidget。
- Editor Tab。
- ToolMenus。
- Asset Registry。
- Data Validation。
- Property Editor。
- 资产定位和打开。
- Editor Utility 与 C++ Slate 工具的边界。

### 实操

将第 8 周验证器升级为：

# Outpost Data Inspector

功能：

```text
1. 扫描 Item / Building / Worker / Ability Definition。
2. 错误、警告、信息分级。
3. 搜索和筛选。
4. 显示资产详情。
5. 双击定位或打开资产。
6. 检查重复 ID、资源缺失、Tag、Cost、Ability Set。
7. 显示软引用和 Primary Asset 信息。
8. 导出 CSV / JSON 报告。
9. 提供一键运行全部验证。
```

可选附加工具：

- Gameplay Tag 浏览。
- Ability Set 关系查看。
- Building Cost 批量检查。
- 资源依赖摘要。

### 必须产出

```text
Docs/22_SlateEditorDataInspector.md
OutpostEditor/DataInspector
Demo/Week22_EditorTool.mp4
```

### 验收

- Runtime Build 不包含 Slate Editor 代码。
- 工具处理空资产、重命名、删除等情况。
- 工具解决真实内容生产问题，不只是显示 Hello World。
- 能解释 Asset Registry 与同步加载资产的差异。
- 能从错误项直接定位到资产。

### 进阶任务

- 使用 Detail Customization。
- 增加批量修复安全项。
- 编写 Editor Automation Test。
- 输出验证结果供 CI 读取。

---

# 13. 阶段七：质量、构建与面试交付，第 23–24 周

---

## 第 23 周：自动化测试、Functional Test、RunUAT 与最小 CI

### 学习内容

- Simple / Complex Automation Test。
- Automation Spec。
- Functional Test。
- Editor Test 与 Runtime Test。
- 命令行运行测试。
- UnrealEditor-Cmd。
- RunUAT BuildCookRun。
- Exit Code 和日志。
- CI 基础。

### 测试矩阵

低层测试：

```text
Inventory Add / Remove / Stack
Building Cost
Gameplay Tag Query
Attribute Clamp
Ability Grant / Remove
Ability Cost / Cooldown
Save / Load Round Trip
Data Migration
Task State Transition
Fast Array Item Logic
```

功能测试：

```text
放置建筑后资源扣除
无资源时建造失败
越距采集失败
双客户端看到同一建筑
Worker 完成采集和存入
存档恢复生产与任务
Ability 取消后无残留
```

构建脚本：

```text
1. 编译。
2. 运行核心 Automation Tests。
3. 运行 Data Validation。
4. Cook。
5. 构建 Client 和 Server。
6. 输出日志与失败码。
```

### 必须产出

```text
Docs/23_TestingBuildAutomation.md
Scripts/RunTests.bat
Scripts/BuildCookRun.bat
TestReports/
```

### 验收

- 一条命令可以运行核心测试。
- 测试失败时进程返回失败状态。
- 至少一个 Functional Test 可自动运行。
- Data Validation 可接入构建前检查。
- 干净环境能够按 README 构建项目。

### 进阶任务

- GitHub Actions / Jenkins / TeamCity 本地或云端最小流水线。
- Gauntlet 概念实验。
- 服务器长时间运行和自动客户端连接测试。

---

## 第 24 周：最终打磨、作品集、源码复盘与面试材料

### 本周停止增加新系统

只允许：

- 修 Bug。
- 补测试。
- 优化演示。
- 清理依赖。
- 完善文档。
- 记录指标。
- 准备讲解。

### 最终演示流程

```text
1. 启动 Dedicated Server 和两个客户端。
2. 玩家使用 GAS 建造能力放置建筑。
3. 服务器验证资源和位置。
4. 建筑进入生产并复制状态。
5. Worker 通过任务系统采集和运输。
6. UI 通过事件驱动 / ViewModel 更新。
7. 保存并恢复世界。
8. 打开 Editor Data Inspector 展示错误检测。
9. 展示 Unreal Insights 和 Network Insights 前后对比。
10. 运行自动化测试脚本。
```

### 源码阅读复盘

至少完成：

```text
1. Lyra Gameplay Framework 与 PlayerState / Pawn 初始化。
2. Lyra Enhanced Input → Ability。
3. Lyra Ability Set。
4. Lyra Tag Relationship。
5. Lyra Interaction 或目标选择。
6. 哪些设计适合当前项目。
7. 哪些设计对个人项目属于过度设计。
```

### 必须产出

```text
README.md
Docs/24_ArchitectureOverview.md
Docs/24_InterviewTalkingPoints.md
Docs/24_KnownLimitationsAndNextSteps.md
DemoVideo.mp4
Builds/FinalClient/
Builds/FinalServer/
SavedProfiling/Final/
```

### 验收

- 新机器按 README 可启动或构建。
- 2～3 分钟视频展示结果。
- 10～15 分钟技术讲解有明确主次。
- 项目不足写得真实，不夸大。
- 能回答“为什么用 GAS”和“为什么有些系统不用 GAS”。
- 能展示一份代码、一份 Trace、一项测试和一个编辑器工具。
- 简历描述包含量化指标和技术取舍。

---

# 14. 贯穿全程的工程要求

## 每周测试

每周至少新增：

```text
一个自动化测试
或
一个 Functional Test
或
一份可重复故障测试脚本
```

第 23 周是测试体系收口，不是第一次开始测试。

## 每两周打包

建议在以下周完成打包验证：

```text
第 1、6、8、12、17、20、23、24 周
```

避免只在 Editor 中运行半年后才发现 Cook 问题。

## 每月一次 Trace

至少保存：

```text
第 4 周：基础 Gameplay
第 6 周：资源加载
第 13 周：GAS + 网络
第 17 周：网络复制
第 20 周：综合性能
第 24 周：最终版本
```

## 每周一次源码阅读

源码阅读不是漫无目的通读：

```text
先提出一个问题
→ 找入口类和调用链
→ 跟踪关键路径
→ 写出项目可借鉴点
→ 记录不适合当前项目的部分
```

## 每周一次 10 分钟讲解

固定录音或口述：

```text
本周系统解决什么问题？
为什么选择这个 UE 系统？
状态由谁拥有？
失败路径是什么？
网络下如何工作？
如何测试？
性能风险是什么？
替代方案是什么？
```

---

# 15. 六个阶段验收里程碑

## 第 4 周：工程底座

必须能展示：

- 可编译、可打包项目。
- 输入到交互命令链。
- Gameplay Framework 关系图。
- 日志和调试工具。
- 基础测试。

失败信号：

- 仍依赖 Level Blueprint。
- 所有逻辑都写在 Character。
- 无法解释对象生命周期。

---

## 第 8 周：单机纵切与内容管线

必须能展示：

- 数据驱动建筑和物品。
- Asset Manager 异步加载。
- 建造、生产和 UI 闭环。
- SaveGame。
- Data Validation。
- 打包版本。

失败信号：

- 打开 UI 时同步加载大量资产。
- UI 直接修改 Inventory。
- SaveGame 保存 Actor 指针。

---

## 第 13 周：A 线 GAS 深度验收

必须能展示：

- ASC / AttributeSet。
- 三个完整 Ability。
- Cost / Cooldown / Effect / Cue。
- 自定义 Ability Task。
- Ability Set。
- Input Tag。
- 预测或网络实验。
- GAS 测试与 Lyra 对照。

失败信号：

- 只会在蓝图里调用 Activate Ability。
- 无法解释 Owner / Avatar。
- 所有 Gameplay 都被强行做成 Ability。
- Ability 取消后有残留状态。

---

## 第 17 周：B 线网络验收

必须能展示：

- 两客户端联机。
- Dedicated Server。
- 服务器权威校验。
- Fast Array。
- Dormancy / Relevancy。
- Network Insights。
- 最小 Replication Graph。

失败信号：

- 客户端可以直接修改资源。
- 不理解 Ownership。
- 只会给变量加 `Replicated`。
- 没有延迟和丢包测试。

---

## 第 20 周：D 线 AI 与性能验收

必须能展示：

- Worker 任务系统。
- 目标失效恢复。
- 服务器 AI。
- 可保存、可复制任务状态。
- 100 Worker 压力场景。
- 优化前后 Trace。
- Game / Render / GPU Bound 基础判断。

失败信号：

- 每个 Worker 每帧全量搜索。
- 只说“优化了”但没有数据。
- 工作线程直接访问 UObject。

---

## 第 22 周：C 线 UI 与工具验收

必须能展示：

- 事件驱动 UMG。
- 一个 MVVM 页面。
- CommonUI 页面栈和输入导航。
- Slate Data Inspector。
- Data Validation。
- UI 性能检查。

失败信号：

- UI Tick 查询所有状态。
- Widget 直接调用任意 RPC。
- Editor 模块进入 Runtime Build。
- 工具只展示静态文本，没有生产价值。

---

# 16. 作品集最终交付物

## 代码

```text
多模块 C++ 工程
GAS 核心实现
服务器权威 Gameplay
Fast Array
AI 任务调度
事件驱动 UI
Slate Editor Tool
自动化测试
构建脚本
```

## 文档

至少包含：

```text
01 Project Build
02 UObject / GC
03 Gameplay Framework
04 Input / Command / Authority
05 Data Driven / Tags
06 Asset Manager / Cook
07 Core Gameplay
08 Save / Validation
09–13 GAS
14–17 Networking
18–20 AI / Performance
21 UI
22 Editor Tool
23 Testing / Build Automation
24 Architecture / Interview
```

## 性能证据

```text
加载 Trace
GAS 网络会话
Network Insights
AI 调度优化前后
综合性能优化前后
最终版本 Trace
```

## 演示

```text
2–3 分钟结果视频
10–15 分钟技术讲解
Client + Dedicated Server 包
一键启动脚本
一键测试脚本
编辑器工具演示
```

---

# 17. 面试能力清单

## A：GAS / Gameplay

- ASC 的放置与初始化。
- Owner / Avatar。
- AttributeSet。
- Ability 生命周期。
- Instancing / Net Execution Policy。
- Cost / Cooldown。
- Gameplay Effect。
- Gameplay Cue。
- Ability Task。
- Target Data。
- Prediction Key 基础。
- Ability Set。
- Input Tag。
- Tag Relationship。
- GAS 与普通组件边界。

## B：网络

- Authority / Role。
- Ownership / Owning Connection。
- RPC。
- RepNotify。
- Fast Array。
- Replicated Component / Subobject。
- Relevancy / Priority / Dormancy。
- Character Movement 网络模型。
- Dedicated Server。
- Network Insights。
- Replication Graph。
- Iris 概念、风险和适用条件。

## C：UI / Tool

- UMG 生命周期。
- Delegate 解绑。
- Presenter / ViewModel。
- Field Notify / MVVM。
- CommonUI 输入路由。
- Slate。
- Editor Module。
- Asset Registry。
- Data Validation。
- Slate Insights / Widget Reflector。

## D：AI / Performance

- BT / StateTree / 状态机取舍。
- Task Model。
- 目标失效与取消。
- 集中调度。
- Timer / Tick / Event。
- UE::Tasks。
- GameThread / RenderThread / GPU。
- Unreal Insights。
- Memory Insights。
- ISM / HISM。
- 网络化 AI。

## 工程质量

- UBT / UHT。
- 模块依赖。
- UObject / GC。
- Git LFS / Perforce。
- Logging / check / ensure。
- Visual Logger。
- Automation Test。
- Functional Test。
- RunUAT。
- Cook / Package。
- 构建脚本和最小 CI。

---

# 18. 范围控制与降级策略

即使每周投入 30–40 小时，也必须限制内容量。

## 不允许同时扩张的内容

```text
不制作大量美术内容。
不制作完整商业游戏。
不同时维护 Behavior Tree 和 StateTree 两套完整 AI。
不让 Iris 成为主分支依赖。
不实现商业级登录、匹配、EOS 和跨平台服务。
不深挖 Nanite、Lumen 和渲染源码。
不实现完整开放世界。
不追求复杂动画系统。
```

## 时间不足时的降级顺序

不能降级：

```text
A 线 GAS 深度
服务器权威
Fast Array / Ownership / Dormancy
AI 调度优化报告
事件驱动 UI
自动化测试
Dedicated Server
```

可以降级：

```text
Replication Graph 从复杂节点降为最小空间节点
Iris 从实验降为阅读和分支验证
CommonUI 页面数量减少
Slate 工具减少批量修复功能
EQS / Smart Object 只做实验
CI 使用本地脚本代替完整服务器
GPU 优化只做基础诊断
```

## 功能冻结

```text
第 22 周结束后禁止增加新系统。
第 23～24 周只允许测试、修复、优化和包装。
```

---

# 19. 官方资料索引

以下链接以 UE 5.8 官方文档为主。

## C++ 与工程

- [Programming with C++](https://dev.epicgames.com/documentation/unreal-engine/programming-with-cplusplus-in-unreal-engine)
- [Unreal Engine Modules](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-modules)
- [Unreal Build Tool](https://dev.epicgames.com/documentation/unreal-engine/unreal-build-tool-in-unreal-engine)
- [Build Configurations Reference](https://dev.epicgames.com/documentation/unreal-engine/build-configurations-reference-for-unreal-engine)
- [Packaging Unreal Engine Projects](https://dev.epicgames.com/documentation/unreal-engine/packaging-your-project)

## UObject 与 Gameplay Framework

- [Objects in Unreal Engine](https://dev.epicgames.com/documentation/unreal-engine/objects-in-unreal-engine)
- [Object Pointers](https://dev.epicgames.com/documentation/unreal-engine/object-pointers-in-unreal-engine)
- [Actor Lifecycle](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-actor-lifecycle)
- [Gameplay Framework](https://dev.epicgames.com/documentation/unreal-engine/gameplay-framework-in-unreal-engine)
- [Programming Subsystems](https://dev.epicgames.com/documentation/unreal-engine/programming-subsystems-in-unreal-engine)

## 输入、数据与资源

- [Enhanced Input](https://dev.epicgames.com/documentation/unreal-engine/enhanced-input-in-unreal-engine)
- [Using Gameplay Tags](https://dev.epicgames.com/documentation/unreal-engine/using-gameplay-tags-in-unreal-engine)
- [Asset Management](https://dev.epicgames.com/documentation/unreal-engine/asset-management-in-unreal-engine)
- [Asynchronous Asset Loading](https://dev.epicgames.com/documentation/unreal-engine/asynchronous-asset-loading-in-unreal-engine)
- [Saving and Loading Your Game](https://dev.epicgames.com/documentation/unreal-engine/saving-and-loading-your-game-in-unreal-engine)

## GAS

- [Gameplay Ability System](https://dev.epicgames.com/documentation/unreal-engine/gameplay-ability-system-for-unreal-engine)
- [Using Gameplay Abilities](https://dev.epicgames.com/documentation/unreal-engine/using-gameplay-abilities-in-unreal-engine)
- [Gameplay Attributes and Attribute Sets](https://dev.epicgames.com/documentation/unreal-engine/gameplay-attributes-and-attribute-sets-for-the-gameplay-ability-system-in-unreal-engine)
- [Gameplay Effects](https://dev.epicgames.com/documentation/unreal-engine/gameplay-effects-for-the-gameplay-ability-system-in-unreal-engine)
- [Gameplay Ability Tasks](https://dev.epicgames.com/documentation/unreal-engine/gameplay-ability-tasks-in-unreal-engine)
- [Abilities in Lyra](https://dev.epicgames.com/documentation/unreal-engine/abilities-in-lyra-in-unreal-engine)

## 网络

- [Networking Overview](https://dev.epicgames.com/documentation/unreal-engine/networking-overview-for-unreal-engine)
- [Actor Replication](https://dev.epicgames.com/documentation/unreal-engine/actor-replication-in-unreal-engine)
- [Replicating UObjects](https://dev.epicgames.com/documentation/unreal-engine/replicating-uobjects-in-unreal-engine)
- [Actor Owner and Owning Connection](https://dev.epicgames.com/documentation/unreal-engine/actor-owner-and-owning-connection-in-unreal-engine)
- [Understanding Networked Movement](https://dev.epicgames.com/documentation/unreal-engine/understanding-networked-movement-in-the-character-movement-component-for-unreal-engine)
- [Replication Graph](https://dev.epicgames.com/documentation/unreal-engine/replication-graph-in-unreal-engine)
- [Iris Replication System](https://dev.epicgames.com/documentation/unreal-engine/iris-replication-system-in-unreal-engine)
- [Setting Up Dedicated Servers](https://dev.epicgames.com/documentation/unreal-engine/setting-up-dedicated-servers-in-unreal-engine)
- [Networking Insights](https://dev.epicgames.com/documentation/unreal-engine/networking-insights-in-unreal-engine)

## AI、性能与调试

- [Behavior Trees](https://dev.epicgames.com/documentation/unreal-engine/behavior-trees-in-unreal-engine)
- [StateTree](https://dev.epicgames.com/documentation/unreal-engine/overview-of-state-tree-in-unreal-engine)
- [Visual Logger](https://dev.epicgames.com/documentation/unreal-engine/visual-logger-in-unreal-engine)
- [Unreal Insights](https://dev.epicgames.com/documentation/unreal-engine/unreal-insights-in-unreal-engine)
- [Memory Insights](https://dev.epicgames.com/documentation/unreal-engine/memory-insights-in-unreal-engine)
- [Tasks System](https://dev.epicgames.com/documentation/unreal-engine/tasks-systems-in-unreal-engine)
- [Stat Commands](https://dev.epicgames.com/documentation/unreal-engine/stat-commands-in-unreal-engine)

## UI 与工具

- [UMG and Slate](https://dev.epicgames.com/documentation/unreal-engine/creating-user-interfaces-with-umg-and-slate-in-unreal-engine)
- [UMG Viewmodel](https://dev.epicgames.com/documentation/unreal-engine/umg-viewmodel-for-unreal-engine)
- [Common UI Overview](https://dev.epicgames.com/documentation/unreal-engine/overview-of-advanced-multiplatform-user-interfaces-with-common-ui-for-unreal-engine)
- [Slate Overview](https://dev.epicgames.com/documentation/unreal-engine/slate-overview-for-unreal-engine)
- [Slate Editor Window Quickstart](https://dev.epicgames.com/documentation/unreal-engine/slate-editor-window-quickstart-guide-for-unreal-engine)

## 测试与构建自动化

- [Automation Test Framework](https://dev.epicgames.com/documentation/unreal-engine/automation-test-framework-in-unreal-engine)
- [Write C++ Tests](https://dev.epicgames.com/documentation/unreal-engine/write-cplusplus-tests-in-unreal-engine)
- [Functional Testing](https://dev.epicgames.com/documentation/unreal-engine/functional-testing-in-unreal-engine)
- [Run Automation Tests](https://dev.epicgames.com/documentation/unreal-engine/run-automation-tests-in-unreal-engine)

---

# 最终定位

完成这 24 周后，你的作品集不应该给人以下印象：

```text
每个 UE 系统都碰过一点。
```

而应该形成清晰标签：

```text
以 GAS 和 C++ Gameplay 架构为主线，
能够把系统运行在服务器权威的多人环境中，
能够构建事件驱动 UI 和内容工具，
能够设计 AI 任务与集中调度，
并用测试、Trace、Dedicated Server 和构建脚本证明工程质量。
```

这仍然不能替代真实商业项目中的长期协作经验，但足以让你的能力证明从“教程学习者”提升为：

> **具备中高级 UE 客户端知识结构、完整项目证据和较强工程潜力的候选人。**
