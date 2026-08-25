
# UE Advanced Client Engineer V4 — Textbook

> **职责**：解释“为什么”和“机制是什么”。  
> **不负责**：把每一个点击、文件路径、测试命令都重复写一遍；那些在 `V4_03_Lab_Manual.md`。  
> **版本基线**：UE 5.8。  
> **资料原则**：Epic 官方 Concept/Programming Guide 为第一资料层；API 用于精确接口；Lyra/官方 Sample 用于工程对照；Engine Source 用于验证。

## 阅读方法

每章先读“工程问题”，再读机制正文。读完后不要直接背结论，去 Lab 做对应实验；出现与预期不一致时再打开 API/源码。每章都要求你能回答四件事：**谁拥有状态、生命周期多长、谁可修改、网络/存档/加载如何处理**。

## 全书知识依赖

```text
Build/Module
  → Reflection/UObject/Lifetime
  → Gameplay Framework/Communication
  → Input/Interaction/Authority
  → Data/Asset/Save
  → Core Gameplay
  → GAS
  → Networking/Scale
  → AI/Performance
  → UI/Tooling
  → Testing/Build/Portfolio
```

---

# C01 — UE 工程从 .uproject 到可执行文件

**对应进度**：Week 1

## 本章工程问题

> 为什么 UE 项目不是“一个 Visual Studio 工程”，而是一套由 Target、Module、UHT、UBT 与 UAT 共同描述的构建系统？

## 机制正文

普通 C++ 项目往往把“工程文件”当作事实来源，但 UE 恰好相反：`.sln`、`.vcxproj` 等更多是由 UnrealBuildTool 生成的 IDE 视图；真正稳定的工程描述来自 `.uproject`、`.uplugin`、`*.Build.cs`、`*.Target.cs` 和源码目录。理解这一点可以解释很多看似诡异的问题：为什么删掉 Intermediate 后还能重新生成工程；为什么新增 Module 只改 sln 不够；为什么 Editor Target 与 Game Target 会链接不同模块。

构建链应建立成一张因果图：项目/插件描述声明模块 → UBT 解析 Target 和 Build.cs 构造依赖图 → 对含 Unreal Reflection 宏的头文件运行 UHT 生成反射胶水代码 → C++ 编译器编译原始与生成代码 → Link 形成 Editor/Game/Server 等不同目标 → UAT 在需要时驱动 Build/Cook/Stage/Package。不要死记每个工具的命令，而要知道“哪一层拥有哪类决策”。

## 设计规则

- `.uproject` 不是 Visual Studio solution 的替代文本，而是 UE 项目入口。
- `Target.cs` 决定“构建哪类程序”；`Build.cs` 决定“模块怎样编译、依赖谁”。
- UHT 不是 C++ 编译器；它为反射系统生成额外代码。
- UAT 更接近自动化流水线驱动器，常用于 BuildCookRun。

## 在 Networked Outpost 中如何落地

Networked Outpost 要求从 Week 1 就有 Runtime Module 与 Editor Module，并且打包后验证 OutpostEditor/UnrealEd 没进入 Runtime。

## 官方资料 / 源码阅读方向

- Epic Docs: Programming with C++
- Epic C++ Coding Standard
- 源码入口: Engine/Source/Programs/UnrealBuildTool、UnrealHeaderTool、AutomationTool


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C02 — Module、Plugin 与物理依赖

**对应进度**：Week 1

## 本章工程问题

> 为什么项目目录整洁不等于架构清晰？Module 的真正边界是什么？

## 机制正文

Module 是编译、链接和依赖可见性的边界，不只是把文件分文件夹。Public/Private 也不是“头文件和 cpp 的固定分类”，而是在表达哪些头文件构成模块对外 API。一个 Runtime Module 的 Public 头如果 include 了 Editor-only 类型，就可能把 Editor 依赖沿公开接口扩散出去。

设计模块时先看稳定依赖方向，再看业务名字。早期只有 `OutpostRuntime` + `OutpostEditor` 是合理的，因为此时边界尚未稳定；过早拆成十个模块只会把不成熟设计固化。等数据、Gameplay、Ability、UI 的依赖关系真实出现后再拆分。Plugin 适合“可拔插、可复用、生命周期相对独立”的功能，而不是为了看起来工程化就把每个模块包装成 Plugin。

## 设计规则

- Runtime 禁止依赖 Editor。
- Core 层不要反向依赖 UMG、Slate、GameplayAbilities 等高层系统。
- Public header 的 include 会放大物理依赖；优先前置声明、最小 include。
- 模块拆分以“稳定依赖边界”而不是类数量为触发条件。

## 在 Networked Outpost 中如何落地

Week 5 以后再把 OutpostRuntime 拆成 Core/Gameplay/Abilities/UI；Editor Module 可以依赖 Runtime，反向禁止。

## 官方资料 / 源码阅读方向

- Epic C++ Coding Standard: Physical Dependencies
- UBT Module documentation / ModuleRules API


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C03 — Build Configuration、Target 与可重复构建

**对应进度**：Week 1

## 本章工程问题

> Development Editor、Development、DebugGame、Shipping 和 Server Target 到底差在哪里？

## 机制正文

学习配置不能停留在“Debug 比较慢”。你需要区分两条轴：一条是 Target Type（Editor/Game/Client/Server），决定程序角色和可链接模块；另一条是 Configuration（Debug/DebugGame/Development/Shipping/Test），决定优化、调试符号、断言与部分运行时功能。Dedicated Server 并不是在普通客户端上加 `-server` 就等价于 Server Target。

可重复构建是工程能力：记录 Engine Commit、VS/MSVC/SDK，提供脚本从清理 Binaries/Intermediate 到编译、Cook、Package，并以进程退出码决定成功失败。这样后续网络、CI、交付才有可信基础。

## 设计规则

- 构建脚本必须失败即失败，不能只检查“看起来生成了文件”。
- 验证打包目录不存在 Editor-only 二进制。
- Live Coding 用于局部迭代，不应该替代干净构建验证。

## 在 Networked Outpost 中如何落地

创建 `BuildDevelopment.bat` 与 `VerifyWeek01.bat`，并把其作为后续所有周的回归入口。

## 官方资料 / 源码阅读方向

- Epic Docs: Compiling Game Projects / Build Configurations / UAT BuildCookRun


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C04 — Reflection：UHT 为 C++ 增加了什么

**对应进度**：Week 2

## 本章工程问题

> 为什么 `UCLASS/UPROPERTY/UFUNCTION` 不是“给蓝图用的宏”？

## 机制正文

标准 C++ 编译器知道类型布局和语言语义，但 UE 还需要让 Editor、Serialization、GC、Networking、Blueprint 等系统以统一方式查询类型与成员元数据。UHT 在编译前扫描受支持的声明，并生成把 C++ 类型注册到 Unreal Reflection System 的胶水代码。

因此 `UPROPERTY` 的价值远超过“显示到 Details 面板”：它可以参与引用追踪、序列化、复制、编辑器暴露等不同系统，但具体行为由 specifier 决定。不要形成“只要是 UObject 指针就加 UPROPERTY”的机械规则；先明确这个字段是否是持久成员引用、是否需要序列化/复制/编辑器暴露，再选合适声明。

## 设计规则

- Reflection ≠ C++ RTTI；UE 有自己的 `UClass/FProperty/UFunction` 元模型。
- `GENERATED_BODY()` 是生成代码挂接点之一。
- 并非所有普通 C++ 类型都需要反射；算法内部数据常保持普通 C++ 即可。

## 在 Networked Outpost 中如何落地

创建 `FNormalItem` 与 `USTRUCT FOutpostItemStack` 对照实验，定位 generated 代码，观察 `StaticStruct`/属性注册差异。

## 官方资料 / 源码阅读方向

- Epic Docs: Programming with C++ / Properties / Functions / Structs / Interfaces
- 源码阅读: Generated code + UObject/Class.h


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C05 — UObject、UClass 与 Class Default Object

**对应进度**：Week 2

## 本章工程问题

> 为什么构造函数会在“没有 Spawn 实例”时执行？CDO 为什么不能保存实例状态？

## 机制正文

每个 UObject 类都由 `UClass` 描述，而类默认对象（CDO）是该类的一份特殊默认实例，用于提供默认属性值并参与对象初始化、Blueprint 默认值等流程。很多“编辑器启动时构造函数怎么执行了”的困惑，本质上来自把 UObject 构造函数误认为普通业务实例构造。

工程上要把“定义时默认值”和“运行时状态”严格分开。构造函数适合创建默认子对象、设置类默认配置；依赖 World、Player、网络连接或其他运行对象的逻辑通常不应放在这里。CDO 也不应持有某个会话或玩家的动态状态。

## 设计规则

- 构造函数阶段不要假定 World 已完成初始化。
- 默认子对象属于类/实例构造体系，不等价于运行时动态组件。
- 看到构造函数多次执行，先判断是否是 CDO/Blueprint class reinstance，而不是立即认为出现重复 Spawn。

## 在 Networked Outpost 中如何落地

为 `UOutpostItemDefinition`、`AOutpostPickupActor` 打印对象名、Class、Flags、是否 CDO；比较编辑器加载与 PIE。

## 官方资料 / 源码阅读方向

- Epic Docs/API: UObject / UClass / GetDefaultObject
- 源码入口: UObjectGlobals、Class.cpp


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C06 — 对象创建、Outer 与生命周期归属

**对应进度**：Week 2

## 本章工程问题

> `NewObject`、`CreateDefaultSubobject`、`SpawnActor` 为什么不能互换？Outer 又为什么不是 Owner？

## 机制正文

三种创建方式对应不同对象模型：`CreateDefaultSubobject` 参与 Actor/UObject 的默认子对象构造；`NewObject` 创建一般 UObject 并通过 Outer 建立命名/生命周期语境；`SpawnActor` 由 UWorld 创建 Actor，进入 Level、组件注册、网络和 Actor 生命周期。把它们理解成三个“new 的包装”会导致初始化时机和世界归属错误。

`Outer` 主要表达 UObject 的 containment/name/lifetime context，不等同于 Actor Ownership，也不等同于网络 Owning Connection。Actor 的 `Owner` 又是一套 Gameplay/Networking 语义。必须把这三种“拥有”拆开。

## 设计规则

- Actor 必须通过 World 的 Spawn 路径进入完整世界生命周期。
- Outer 不自动保证所有对象永远不被 GC；引用追踪仍需正确。
- 网络 Ownership 要从 connection/RPC 语义理解，不要从 UObject Outer 推导。

## 在 Networked Outpost 中如何落地

分别创建 Definition UObject、默认 InteractionComponent、运行时 Pickup Actor，记录 Outer/Owner/World 与销毁行为。

## 官方资料 / 源码阅读方向

- Epic API: NewObject, CreateDefaultSubobject, UWorld::SpawnActor
- 源码: UObjectGlobals.cpp、LevelActor.cpp


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C07 — GC、对象指针与 Actor/Component 生命周期

**对应进度**：Week 2

## 本章工程问题

> UE 的 GC 如何决定一个 UObject 是否仍然可达？为什么 Actor Destroy 与内存回收不是同一件事？

## 机制正文

UE 对 UObject 采用可达性分析的垃圾回收模型。工程上真正重要的不是背 GC 算法，而是能判断“这个成员是否构成强引用”“弱引用何时失效”“Soft Reference 是否代表对象已经加载”。`TObjectPtr` 表达 UObject 强成员引用语义；`TWeakObjectPtr` 适合观察不拥有生命周期的对象；`TSoftObjectPtr/TSoftClassPtr` 主要表达可序列化的软资产路径与按需加载，不是弱引用的替代品。

Actor 生命周期还叠加了 World 语义：构造、组件创建/注册、初始化、BeginPlay、EndPlay、Destroy。`Destroy()` 表示 Actor 从 Gameplay 世界退出，实际 UObject 内存释放通常在后续 GC。Component 也有 Register/Initialize/BeginPlay/Unregister 等阶段。把绑定 Delegate、Timer、Subsystem 查询都堆在构造函数或析构函数，是典型生命周期错误。

## 设计规则

- 成员强引用、弱观察、软资产引用三类语义必须主动区分。
- 跨帧保存 UObject 引用前必须明确谁保证其有效。
- 在回调中优先验证对象有效性和生命周期，而不是假定“上次还有效”。
- Incremental GC 在 UE5.8 仍是需要谨慎评估的实验性能力，不作为主项目依赖。

## 在 Networked Outpost 中如何落地

做 5 组生命周期实验：Editor 放置、PIE、Runtime Spawn、Destroy、Level 切换；再制造 Weak/Soft 引用不同失效场景。

## 官方资料 / 源码阅读方向

- Epic Docs: Object Pointers / Garbage Collection / Incremental GC
- 源码入口: GarbageCollection.cpp、Actor.cpp、ActorComponent.cpp


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C08 — Gameplay Framework 是生命周期与网络角色的分工

**对应进度**：Week 3

## 本章工程问题

> GameMode、GameState、PlayerController、PlayerState、Pawn 为什么不能合成一个“PlayerManager”？

## 机制正文

Gameplay Framework 的价值不是提供一堆父类，而是把“世界规则、全局复制状态、连接/玩家意图、玩家持久状态、当前 Avatar”分给生命周期和网络可见性不同的对象。GameMode 只在服务器存在，因此适合权威规则；GameState 在服务器与客户端存在并复制全局可见状态；PlayerController 与连接和本地输入强相关；PlayerState 适合跨 Pawn 的可复制玩家状态；Pawn/Character 是当前世界中的可控制实体。

设计时先写状态表：这个状态是否跨 Pawn？客户端是否需要看到？只属于一个连接还是所有连接？随 World 销毁还是跨地图？再选类。不要从“这个类名字听起来适合”出发。

## 设计规则

- GameMode server-only 是网络架构事实，不是风格选择。
- PlayerState 与 Pawn 的边界会直接影响 Respawn、GAS ASC 放置和网络复制。
- PlayerController 不是“所有玩家状态的容器”。

## 在 Networked Outpost 中如何落地

建立 OutpostGameMode/GameState/PC/PS/Character 空壳；给每类写 owner/lifetime/replication 注释，并画对象图。

## 官方资料 / 源码阅读方向

- Epic Docs: Gameplay Framework / Game Mode and Game State / Player Controllers
- Lyra: LyraGameMode、LyraGameState、LyraPlayerState、PawnExtension


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C09 — Component、Subsystem、Manager 与服务边界

**对应进度**：Week 3

## 本章工程问题

> 什么时候应该用 ActorComponent，什么时候是 Subsystem，什么时候普通 UObject/纯 C++ 服务更合适？

## 机制正文

ActorComponent 适合“跟随某个 Actor 生命周期、组合到该 Actor 上的能力”；Subsystem 适合绑定到 Engine/GameInstance/World/LocalPlayer 等明确宿主生命周期的服务。两者都不是“方便全局访问”的理由。一个没有自然宿主、只处理纯数据算法的系统可能更适合普通 C++ 类型或被某个 owning object 明确持有的 UObject。

判断方法是先写三件事：谁创建、何时销毁、谁可以访问。若答案只是“任何地方都能 Get”，说明设计仍未完成。

## 设计规则

- 不要用 Subsystem 替代所有 Singleton/Manager。
- Component 不应偷偷依赖某个具体 GameMode 或 Widget。
- 跨 World 数据不要放 WorldSubsystem；本地玩家输入/UI 服务不要放 GameInstanceSubsystem。

## 在 Networked Outpost 中如何落地

OutpostInteractionComponent 随 Character；World 级任务/世界服务放 WorldSubsystem；跨 Session 配置才考虑 GameInstanceSubsystem。

## 官方资料 / 源码阅读方向

- Epic Docs/API: Programming Subsystems
- 源码: SubsystemCollection.cpp


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C10 — Interface、Delegate 与诊断链

**对应进度**：Week 3

## 本章工程问题

> 系统之间如何通信而不形成互相持有的耦合网？

## 机制正文

Interface 适合表达“调用目标具备某种能力/契约”；Delegate 适合表达“一处状态变化，需要零到多个观察者被通知”。两者解决的方向不同：Interface 更像请求或能力发现，Delegate 更像事件传播。Dynamic Delegate 提供反射/Blueprint 能力，Native Delegate 更轻、更 C++ 化。

从本周起，日志、`check/ensure`、Visual Logger、Gameplay Debugger 必须成为设计的一部分。可观察性不是项目收尾才加的功能；如果一个系统只能靠 UI 看状态，它的调试架构已经有问题。

## 设计规则

- 命令/查询使用明确接口；状态变化使用事件，而不是消费者每帧拉取。
- 解绑与生命周期同样重要，特别是异步/Delegate 回调。
- `check` 用于不可恢复程序不变量，`ensure` 用于希望记录但继续运行的异常。

## 在 Networked Outpost 中如何落地

交互组件通过 Interface 查询对象；库存变化通过 Native Delegate 广播；Gameplay Debugger 显示当前交互目标和资源。

## 官方资料 / 源码阅读方向

- Epic API: Delegates / Interfaces / Visual Logger / Gameplay Debugger


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C11 — Enhanced Input：从硬件输入到语义输入

**对应进度**：Week 4

## 本章工程问题

> 为什么 `W`、鼠标左键不应该直接等于 Gameplay 行为？

## 机制正文

Enhanced Input 把硬件映射、数值变换、触发条件和语义 Action 分层。`Input Mapping Context` 表示某个输入环境下“设备输入→Action”的映射；Modifier 改值，Trigger 决定何时产生 Started/Triggered/Completed 等语义；LocalPlayerSubsystem 管理本地玩家的 Context。

工程上应继续把 Action 与业务命令分离：`IA_Interact` 表示玩家意图“交互”，但它不应该知道库存、Server RPC 或具体门/资源节点的实现。PlayerController/Character 将输入翻译为命令，再交给 Interaction/Command 层。

## 设计规则

- 输入配置不硬编码业务对象。
- UI/Game 输入切换要以 Context、Focus、CommonUI 等体系管理，不依赖随手 EnableInput/DisableInput。
- 本地玩家相关输入系统不要假定 Dedicated Server 存在 LocalPlayer。

## 在 Networked Outpost 中如何落地

建立 OutpostInputConfig；IA_Interact/Build 只产生意图，交互与命令组件负责查询/请求。

## 官方资料 / 源码阅读方向

- Epic Docs: Enhanced Input
- Lyra: Input Config / EnhancedInputComponent / Ability Input


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C12 — Query、Command 与第一次服务器权威边界

**对应进度**：Week 4

## 本章工程问题

> 如何把“我想做什么”与“世界是否允许我做”拆开？

## 机制正文

交互通常至少包含 Query 和 Command 两层：Query 是本地/世界信息查询，例如候选目标、距离、提示；Command 是改变权威状态的请求，例如建造、采集、分配 Worker。客户端可以预测或预览，但最终状态修改入口需要按服务器权威设计。

这一周只做最小网络冒烟：拥有正确 Ownership 的 Client 在 owned Actor 上发 Server RPC，服务器修改 Replicated 属性，客户端通过 RepNotify 观察结果；然后故意移除 Ownership 验证 RPC 约束。目的不是学完整 Networking，而是让后续 API 从一开始具有权威边界。

## 设计规则

- 请求函数与验证/执行函数分开。
- 客户端显示预览 ≠ 客户端有权生成真实建筑。
- 失败原因应该是结构化结果，而不是散落日志字符串。

## 在 Networked Outpost 中如何落地

实现 FOutpostInteractionQuery/Result、FOutpostCommandRequest/Result 和 Request/Validate/Execute API；完成 Listen Server 冒烟测试。

## 官方资料 / 源码阅读方向

- Epic Docs: Networking Overview / RPC / Replicated Properties


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C13 — Definition、Instance 与 DataAsset/DataTable

**对应进度**：Week 5

## 本章工程问题

> 为什么静态定义、运行时实例状态和批量表格数据必须分层？

## 机制正文

DataAsset 适合有资产身份、可引用其他资产、需要设计器按对象编辑的定义；DataTable 更适合大量同构 row 数据和表格化编辑。无论使用哪种，Definition 都不应该保存某个运行实例的库存数量、剩余生产时间等动态状态。

建立“Definition → Runtime Instance/Component State → Save Data”三层后，很多系统会自然变清晰：定义可由 AssetManager 管理，运行实例由 World/Actor 生命周期管理，存档只保存稳定 ID 和可重建状态。

## 设计规则

- 静态定义和运行时状态物理分离。
- DataAsset 不是为了“避免写代码”；它是配置/身份边界。
- DataTable row key 不要轻易承担跨版本稳定 ID，除非明确管理迁移。

## 在 Networked Outpost 中如何落地

实现 Item/Building/Worker/Ability Definition；运行时 Inventory Item 只保存 Definition ID + Count 等状态。

## 官方资料 / 源码阅读方向

- Epic Docs: Data Driven Gameplay Elements / Data Assets / Data Tables


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C14 — Gameplay Tags：层级语义而不是字符串替代

**对应进度**：Week 5

## 本章工程问题

> 什么时候 Gameplay Tag 比 Enum 更合适？

## 机制正文

Gameplay Tag 是可层级匹配、可组合查询、可由多系统共享的语义标识。它适合开放集合、层级分类和跨系统条件，例如 `Ability.Build.Place`、`State.Worker.Busy`、`Failure.Build.InvalidLocation`。Enum 更适合封闭、编译期稳定、需要 switch exhaustiveness 的状态集合。

Tag 的最大风险不是性能，而是治理：命名、来源、层级和生命周期不受控时会退化为“高级字符串”。建立 Native Gameplay Tags 与命名规范，并为 Tag Query 写测试。

## 设计规则

- Tag 表达语义，不用于替代所有布尔值。
- Failure Tag 与 State Tag 分开。
- 高频核心 Tag 可使用 Native Gameplay Tags，避免散落字符串请求。

## 在 Networked Outpost 中如何落地

建立 Item/Building/Ability/State/Failure tag taxonomy；写至少三个 TagQuery 组合测试。

## 官方资料 / 源码阅读方向

- Epic Docs: Gameplay Tags


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C15 — Primary Asset 与引用依赖图

**对应进度**：Week 5

## 本章工程问题

> 为什么“软引用了”仍可能把大量资源拖进内存或 Cook？

## 机制正文

Primary Asset 是 AssetManager 可以按身份直接管理的资产；Secondary Asset 通常随引用关系被带入。硬引用会形成直接加载依赖，软引用把“引用身份”和“当前是否加载”分离，但并不会自动替你设计 Cook、Chunk 或生命周期。

Reference Viewer、Size Map、Asset Audit 应成为数据架构工具。每创建一个 Definition，都要检查它是否意外硬引用了巨大的 Blueprint、SkeletalMesh、Material 链。

## 设计规则

- PrimaryAssetId 应稳定且可用于 Save/查询。
- 软引用降低不必要的强加载依赖，不等于自动节省所有内存。
- 运行时 Class/Visual Asset 是否软化取决于使用时机和加载策略。

## 在 Networked Outpost 中如何落地

为 Definition 分配 Primary Asset Type/ID，检查引用图并记录一项意外依赖修正。

## 官方资料 / 源码阅读方向

- Epic Docs: Asset Management / Cooking and Chunking


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C16 — Asset Manager 与异步加载生命周期

**对应进度**：Week 6

## 本章工程问题

> 异步加载为什么不仅是把 `LoadObject` 换成一个异步函数？

## 机制正文

异步加载的真正复杂度在请求生命周期：调用者可能销毁、用户可能取消、多个调用者可能请求同一资产、回调可能晚于 UI 页面关闭。`FStreamableHandle` 不只是“等待结果”的句柄，它代表可管理的加载请求。

AssetManager 提供 Primary Asset 身份、扫描、Bundle 与加载策略入口。项目可以在启动时只加载轻量定义，打开菜单时加载 Icon bundle，确认放置前加载 World/Gameplay bundle。这样加载时机由使用场景驱动，而不是由某个 Widget Construct 偶然触发。

## 设计规则

- 异步回调必须处理调用者失效。
- 重复请求要决定合并、复用还是独立；不能无意识重复加载。
- UI 必须有 Loading/Failed/Ready 状态，而不是永远 spinner。

## 在 Networked Outpost 中如何落地

实现 UOutpostAssetManager 与 FOutpostAssetLoadRequest；记录开始/结束/失败/耗时。

## 官方资料 / 源码阅读方向

- Epic Docs: Asset Management / Streamable Manager API


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C17 — Cook：Editor 能看到 ≠ Package 一定存在

**对应进度**：Week 6

## 本章工程问题

> 为什么资源在编辑器里工作，打包后却找不到？

## 机制正文

Editor 拥有完整 Asset Registry、开发内容和编辑器依赖；Cook/Package 只保留按照引用、规则和配置进入构建的内容。软引用如果没有被 Primary Asset Rule、明确 Cook 配置或其他路径纳入，打包后可能不存在。

因此资源系统的验收必须在 Packaged Build 完成。Cook 问题要沿“资产是否被发现 → 是否被 Cook → 是否 staged → 运行时是否按正确路径/ID 请求”逐层排查，而不是直接在代码里加同步 Load 兜底。

## 设计规则

- 每两周打包不是形式主义，而是持续验证 Content Pipeline。
- Cook rule 是部署协议的一部分。
- Editor-only asset/reference 不能泄漏到 Runtime。

## 在 Networked Outpost 中如何落地

故意移除一个 Primary Asset Cook Rule 复现“Editor 正常、Package 缺失”，写排查记录后修复。

## 官方资料 / 源码阅读方向

- Epic Docs: Cooking Content and Creating Chunks / Packaging


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C18 — Inventory：状态所有权、事务与失败原因

**对应进度**：Week 7

## 本章工程问题

> 一个看似简单的 Add/Remove 为什么值得单独设计 API？

## 机制正文

库存是训练状态所有权的好对象：数量由 InventoryComponent 拥有，外界不能直接改数组；所有修改通过原子操作，先验证容量/成本/合法性，再一次性提交，避免“扣了一半失败”。结果应返回结构化 Failure Reason，便于 UI、日志、网络统一处理。

数据结构先满足正确性和可测试性，之后网络阶段再换 Fast Array 等复制表示。不要过早为了网络 API 把业务模型绑定到复制实现。

## 设计规则

- 数组/Map 是内部表示，不是公共 API。
- UI 订阅变化事件，不持有写权限。
- 操作结果包含失败原因和变化摘要，便于网络/测试。

## 在 Networked Outpost 中如何落地

实现 Add/Remove/CanAfford/ConsumeCost；为 stack、overflow、insufficient、rollback 写测试。

## 官方资料 / 源码阅读方向

- Epic API: Actor Components / Delegates / Containers


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C19 — Building / Production：Timer、状态机与纵切

**对应进度**：Week 7

## 本章工程问题

> 为什么生产系统不应该靠每个建筑 Tick 检查时间？

## 机制正文

生产行为通常是低频状态迁移：Idle → Producing → Complete/Blocked。Timer 或调度器比无条件 Tick 更贴合语义，也更容易在存档时保存“结束时间/剩余时间”。本周先做单机正确模型，网络阶段再复制必要状态。

纵切的意义是第一次把输入、查询、库存事务、Spawn、生产、Delegate、UI 串成一条可测试链，而不是追求内容量。每一步必须可以失败并返回原因。

## 设计规则

- Tick 不是禁用，而是只用于真正逐帧问题。
- 权威生产状态不依赖动画 Notify 或 Widget。
- 建造流程先 Validate 再 Consume，再 Spawn/Commit；失败要可回滚。

## 在 Networked Outpost 中如何落地

完成“选择建筑→本地预览→Validate→扣资源→Spawn→Timer 生产→库存→UI”的纵切。

## 官方资料 / 源码阅读方向

- Epic Docs/API: Timers / Actor Spawning / UMG basics


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C20 — SaveGame：保存可重建状态

**对应进度**：Week 8

## 本章工程问题

> 为什么不能把 Actor 指针或整个 UObject 图直接“保存下来”？

## 机制正文

运行时 Actor/UObject 的地址、Outer、World 关系并不跨会话稳定。可靠存档保存的是“如何重建世界”的纯数据：Definition ID、Stable Instance ID、Transform、库存、任务阶段、剩余时间以及对象之间以 Stable ID 表达的引用。

加载是有序恢复：先读取/迁移版本 → 创建对象骨架 → 恢复各自局部状态 → 解析跨对象引用 → 触发系统/UI 刷新。很多 SaveGame Bug 其实是恢复顺序问题，而不是序列化 API 问题。

## 设计规则

- 存档格式是一种长期协议，必须有 Version。
- 时间状态优先保存可解释数据，例如剩余秒数/结束时间，而不是 TimerHandle。
- 跨对象引用用稳定 ID 二阶段解析。

## 在 Networked Outpost 中如何落地

保存建筑/库存/生产/Worker 基础数据；退出打包程序后重启恢复；模拟 V1→V2。

## 官方资料 / 源码阅读方向

- Epic Docs: Saving and Loading Your Game


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C21 — Data Validation：把内容错误前移

**对应进度**：Week 8

## 本章工程问题

> 为什么内容配置错误不应该等玩家运行到那张地图才发现？

## 机制正文

数据驱动项目把大量规则移到资产后，编译器无法替你检查重复 ID、负成本、非法 Tag、缺失软引用等业务约束。Data Validation 的目的就是把这些错误移到编辑器/CI 阶段。

Validator 的输出必须包含“哪一个资产、哪一个字段、为什么错误、如何定位”，否则只是另一份难读日志。后续 Week 22 的 Slate 工具是在这个验证核心之上增加交互界面，而不是重写验证逻辑。

## 设计规则

- Validation logic 独立于 Slate UI。
- 错误/警告/信息分级。
- Runtime 模块不能依赖 Editor validation 实现。

## 在 Networked Outpost 中如何落地

实现重复 ID、必填资产、Cost、Tag、RuntimeClass、Soft Reference 六类检查。

## 官方资料 / 源码阅读方向

- Epic Docs/API: Data Validation / Editor Modules


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C22 — GAS 适用边界与 ASC Owner/Avatar

**对应进度**：Week 9

## 本章工程问题

> GAS 为什么存在？哪些 Gameplay 不该塞进 GAS？

## 机制正文

GAS 解决的是具有“拥有者、激活生命周期、条件/Tag、资源属性、Effect、异步执行、网络复制/预测”这一类反复出现的 Gameplay 模式。它不是“更高级的 Component”，也不应该吞掉库存、生产队列、任务调度等所有业务系统。

ASC 的 Owner Actor 与 Avatar Actor 是 GAS 生命周期设计核心：Owner 更适合承载持续 AbilitySystem 状态，Avatar 是当前执行/表现实体。玩家频繁 Respawn 或切 Pawn 时，把 ASC 放 PlayerState 可以让能力状态跨 Pawn 持续；Character 作为 Avatar 在 Possess/Respawn 时重新 `InitAbilityActorInfo`。

## 设计规则

- 先回答“这个行为是否有 Ability 生命周期/网络预测/Effect/Tag 协调需求”，再决定是否 GAS。
- Owner/Avatar 与网络 Actor Owner 不是同一个概念。
- 初始化顺序必须显式设计，不能碰巧依赖 BeginPlay。

## 在 Networked Outpost 中如何落地

Outpost PlayerState 持有 ASC，Character 为 Avatar；Respawn 实验验证 Ability/Attribute 不丢失。

## 官方资料 / 源码阅读方向

- Epic 5.8: Gameplay Ability System Overview
- Epic: Abilities in Lyra


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C23 — AttributeSet、Gameplay Effect 与数值状态

**对应进度**：Week 9

## 本章工程问题

> 哪些数字应该是 Attribute，哪些仍然是普通业务数据？

## 机制正文

Attribute 适合需要被 Gameplay Effect 修改、复制、预测或参与 GAS 计算的数值，如 Health/Energy/MoveSpeed。库存中的木材条目、建筑生产队列并不会因为“也是数字”就变成 Attribute。

AttributeSet 定义属性和边界处理，Gameplay Effect 描述对属性/Tag 的修改。初始化应通过明确策略（常见是初始化 GE）完成，并对 Clamp/PreAttributeChange/PostGameplayEffectExecute 等职责有清晰边界。

## 设计规则

- Attribute 是 GAS 数值协议，不是万能数据表。
- Server 仍是权威数值来源；客户端显示可基于复制/预测值。
- Clamp 规则要测试，而不是散落在 UI。

## 在 Networked Outpost 中如何落地

实现 Health/MaxHealth/Energy/BuildResource/CarryCapacity/MoveSpeed，并写初始化/Clamp 测试。

## 官方资料 / 源码阅读方向

- Epic GAS docs: Attributes / Gameplay Effects
- Lyra Attribute Sets


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C24 — Gameplay Ability 的生命周期与并发

**对应进度**：Week 10

## 本章工程问题

> Ability 为什么不是“调用一次函数”？

## 机制正文

Ability 有 Grant、CanActivate、Activate、运行中、Commit、Cancel/End 等状态，并且可能跨多帧等待动画、目标选择或事件。Instancing Policy 决定 Ability 实例如何存在；Net Execution Policy 决定在哪一端执行/预测。

最常见的工程错误是结束路径不完整：取消时预览 Actor/Delegate/Task 没清，死亡后 Ability 还在运行，或一次成功路径重复 Commit。设计 Ability 时先画状态机和所有终止路径，再写业务代码。

## 设计规则

- 每个 Ability 必须定义成功、失败、取消、Owner/Avatar 销毁路径。
- 不要在 Ability 里直接访问具体 Widget。
- Ability 负责协调动作，不等于把所有子系统逻辑搬进 Ability。

## 在 Networked Outpost 中如何落地

实现 Build/Collect/Dash(或 Interact) 三个能力，给每个画生命周期和取消路径。

## 官方资料 / 源码阅读方向

- Epic 5.8: Using Gameplay Abilities


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C25 — Effect、Cost、Cooldown 与 Gameplay Cue

**对应进度**：Week 10

## 本章工程问题

> 一次 Ability 的规则变化和表现应该分别放在哪里？

## 机制正文

Gameplay Effect 适合表达属性与 Tag 的 Instant/Duration/Infinite 修改；Cost/Cooldown 是 Ability 激活规则的一部分，通常由 Effect/Tag 配合；Gameplay Cue 是面向表现的事件/持续视觉音效层，不应保存真实资源扣除或建造状态。

把数据和表现拆开后，服务器可以权威修改 Effect/Attribute，客户端通过复制和 Cue 呈现。`SetByCaller` 适合把一次执行上下文中的动态数值传入 Effect，但仍要有明确数据来源和验证。

## 设计规则

- 失败的 Ability 不应提前扣 Cost。
- Cooldown UI 从 GAS 状态/Tag/Effect 得到，不再自建第二套倒计时真相。
- Cue 可丢失/重放时不应破坏权威 Gameplay。

## 在 Networked Outpost 中如何落地

实现 GE_BuildCost、DashCost/Cooldown、CollectReward 与两个 Cue；做 Commit 一次性测试。

## 官方资料 / 源码阅读方向

- Epic GAS docs: Gameplay Effects / Gameplay Cues


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C26 — AbilityTask、TargetData、GameplayEvent 与取消清理

**对应进度**：Week 11

## 本章工程问题

> 如何在 Ability 中安全地等待“未来才会发生”的事情？

## 机制正文

AbilityTask 把 Ability 内的异步等待建模成有生命周期的任务：等待输入、Montage、Gameplay Event、Target Data 等。它不是普通线程 AsyncTask；它依附 Ability 生命周期，并通过 Delegate 产生后续事件。

Target Data 是客户端目标信息与服务器验证之间的重要边界。客户端可以提交“我选了这个位置/目标”，服务器仍要验证距离、碰撞、资源与权限。自定义 Task 最重要的不是节点能跑，而是 `OnDestroy`/EndTask 时解绑 Delegate、停止 Timer、清理预览，确保取消没有悬空回调。

## 设计规则

- 异步 = 生命周期问题，不只是语法问题。
- Target Data 是输入，不是服务器事实。
- 每个 Task 的 Cleanup 必须可重复且幂等。

## 在 Networked Outpost 中如何落地

实现 `UAbilityTask_WaitValidBuildingPlacement` 或交互目标 Task；覆盖成功/取消/销毁测试。

## 官方资料 / 源码阅读方向

- Epic GAS docs: Ability Tasks / Targeting
- Lyra Interaction: AbilityTask_WaitForInteractableTargets_*


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C27 — Ability Set、Input Tag 与 Tag Relationship

**对应进度**：Week 12

## 本章工程问题

> 如何让角色/装备/状态数据化授予能力，而不是在输入代码里硬编码 Ability Class？

## 机制正文

Ability Set 把一组 Ability、Effect、AttributeSet 作为可授予配置；Input Tag 把 Enhanced Input 的语义映射到 Ability Spec；Tag Relationship 集中表达能力间 Required/Blocked/Cancel 关系。这样输入层不需要知道具体 Ability 类，装备或 Player Definition 可以按数据授予/移除。

授予必须跟踪来源。装备卸下时只移除由该装备授予的 Spec/Effect，而不是“清空同类能力”。这就是为什么项目需要 `FGrantedHandles`/source object 一类机制。

## 设计规则

- 输入层只产生 Input Tag，不 new/查找 Ability Class。
- Grant 与 Remove 成对设计。
- 能力互斥优先用 Tag/Activation Group 等系统化规则，而不是每个 Ability 互相查类。

## 在 Networked Outpost 中如何落地

实现 OutpostAbilitySet、Definition、GrantComponent、TagRelationshipMapping；更换 Player Definition 改变能力组合。

## 官方资料 / 源码阅读方向

- Epic: Abilities in Lyra — ULyraAbilitySet / Tag relationships
- Lyra Input → Ability path


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C28 — GAS 网络预测：快反馈与服务器权威并存

**对应进度**：Week 13

## 本章工程问题

> 预测到底预测了什么，服务器拒绝时又如何恢复？

## 机制正文

网络预测的目标是让本地玩家立即看到合理反馈，同时服务器仍拥有最终权威。Local Predicted Ability 会在客户端先执行可预测部分，并通过 Prediction Key 等机制把客户端预测与服务器确认关联。并非所有副作用都天然可回滚，Instant damage 等尤其需要理解 GAS 的预测边界。

学习预测必须配合故障注入：150ms 延迟、丢包、重复输入、客户端资源滞后、Pawn 在 Ability 中被销毁。你要观察“预测表现、权威结果、拒绝原因、清理”四个阶段，而不是只看正常局域网。

## 设计规则

- Prediction ≠ trust；所有关键规则仍在 Server 验证。
- 只预测可以可靠 reconcile 的表现/状态。
- 重复输入与网络重传要避免重复 Commit/Spawn。

## 在 Networked Outpost 中如何落地

选择 Dash 或 Build 做预测实验；记录一份 GAS + Network Trace 与拒绝清理证据。

## 官方资料 / 源码阅读方向

- Epic GAS Overview / Using Gameplay Abilities
- Lyra ASC and predicted abilities


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C29 — Client-Server、Authority、Role 与 Ownership

**对应进度**：Week 14

## 本章工程问题

> “Actor 在客户端存在”与“客户端拥有它”有什么区别？

## 机制正文

网络学习最容易混淆三个维度：Authority 表示哪一端拥有该 Actor 的权威状态；Local/Remote Role 描述当前实例的网络角色；Ownership/Owning Connection 决定特定 RPC、Owner-only replication 等关系。一个客户端能看到某 Actor，不代表它拥有该 Actor，更不代表可以让服务器接受任意修改。

Server 是真相源；客户端维护近似副本和本地预测。所有 Gameplay 状态设计都要标明“谁写、谁读、谁复制给谁”。

## 设计规则

- 先做状态权限表，再写 RPC。
- 不要把 HasAuthority 当作万能 if；明确代码在哪种 NetMode/Role 应执行。
- 网络 Owner 是通信权限链，不等价于 UObject Outer。

## 在 Networked Outpost 中如何落地

在 Server + ClientA + ClientB 上打印角色/Owner/Connection；对 PlayerState、Building、ResourceNode 分类。

## 官方资料 / 源码阅读方向

- Epic 5.8: Networking Overview / Actor Role and Remote Role / Ownership


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C30 — RPC、Replicated Property 与 RepNotify

**对应进度**：Week 14

## 本章工程问题

> 什么时候发送事件，什么时候复制状态？

## 机制正文

RPC 表达一次性的远程调用/意图；Property Replication 表达需要让远端最终拥有的状态。原则上“客户端请求建造”适合 Server RPC，“建筑已存在/库存数量”适合状态复制。不要用可靠 Multicast 持续同步状态，也不要用 RPC 重造一套属性同步协议。

RepNotify 是客户端对复制状态变化的反应入口，但 Server 本地修改通常不会依赖同一个 OnRep 自动回调，因此可统一成 `HandleStateChanged`：Server 修改后显式调用，Client OnRep 后调用。

## 设计规则

- State over event：长期真相用属性复制。
- Server RPC 参数永远需要验证。
- Reliable 不是“更安全”，滥用会造成队头阻塞/带宽问题。

## 在 Networked Outpost 中如何落地

网络化 PlayerState 资源、GameState 阶段、Building Spawn；实现 Server/Client 统一状态处理。

## 官方资料 / 源码阅读方向

- Epic Docs: RPCs / Replicate Actor Properties


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C31 — Replicated Component 与 Subobject

**对应进度**：Week 15

## 本章工程问题

> 一个 Actor 内部复杂状态应该都摊平成 Actor 属性吗？

## 机制正文

ActorComponent 可以拥有独立的 replicated state；普通 UObject subobject 也可以参与复制，但需要正确注册/生命周期管理。选择边界应跟业务聚合一致：InventoryComponent 的条目和通知逻辑可以保持在组件，而不是把所有字段搬到 Actor。

复杂之处在于“对象存在、被 Actor 持有、被注册为可复制 subobject”是不同条件。UE5 的复制系统和 Iris 对 subobject 注册机制有更明确接口，因此实验必须在实际网络环境验证创建、销毁与重连。

## 设计规则

- 复制边界与所有权边界尽量一致。
- 动态 subobject 的创建/销毁要由权威端主导。
- 不要因为能 replicate UObject 就把所有数据对象 UObject 化。

## 在 Networked Outpost 中如何落地

选择 Inventory 或 Production 组件做复制；额外建立一个最小 UObject subobject 实验。

## 官方资料 / 源码阅读方向

- Epic Networking docs: Replicated Subobjects / Actor Components
- Iris docs as comparison


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C32 — Fast Array：增量复制动态集合

**对应进度**：Week 15

## 本章工程问题

> 为什么复制整个 TArray 在频繁变更时不理想？

## 机制正文

`FFastArraySerializer` 面向“有稳定 item identity、频繁增删改、希望 delta serialization 与客户端回调”的动态集合。它不是性能魔法；你仍需要正确标记 Item dirty/Array dirty、设计 item key、处理 PostReplicatedAdd/Change/Remove，并决定 UI 如何增量更新。

先用 Inventory/Production Queue 的普通业务 API 作为真相，再把 Fast Array 当网络表示层。这样测试仍能在无网络环境验证业务逻辑。

## 设计规则

- 业务逻辑不要散进 PostReplicated* 回调。
- Item identity 必须稳定。
- 比较普通数组与 Fast Array 的流量，用 Network Insights 证明差异。

## 在 Networked Outpost 中如何落地

至少把 Inventory Items、Production Queue、Worker Task Queue 之一改为 Fast Array，并做 50/200/500 条变更测量。

## 官方资料 / 源码阅读方向

- Epic API/Docs: Fast TArray Replication


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C33 — Relevancy、Priority、Dormancy 与复制预算

**对应进度**：Week 15

## 本章工程问题

> 服务器为什么不能每帧把所有 Actor 的所有状态发给所有连接？

## 机制正文

网络复制是按连接分配预算。Relevancy 决定某 Actor 是否值得考虑给某连接；Priority/Update Frequency 影响有限带宽下的发送调度；Dormancy 允许长期静止 Actor 暂停常规复制。它们都是“减少无价值工作”，不是改变权威状态模型。

Outpost 中空闲建筑、远距离资源点很适合实验 Dormancy/距离策略。关键是状态改变时正确唤醒，否则客户端会永远停在旧状态。

## 设计规则

- 先正确再优化；不要为了 Dormancy 引入状态不同步。
- 每项优化必须有流量/CPU 指标。
- Relevancy 是 per-connection 的。

## 在 Networked Outpost 中如何落地

空闲建筑 Dormant，生产/受损时 Flush；远距离资源降低更新；记录 Network baseline。

## 官方资料 / 源码阅读方向

- Epic Networking Overview: Dormancy/Relevancy/Priority


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C34 — 服务器验证、幂等与网络 Gameplay 安全

**对应进度**：Week 16

## 本章工程问题

> “RPC 到服务器了”为什么远远不等于“这个操作合法”？

## 机制正文

Server RPC 只是把请求送到权威端，真正安全性来自服务器重新验证：玩家是否有权限、距离是否合理、资源是否足够、Definition ID 是否允许、Transform 是否可放置、目标是否仍有效、请求是否重复。不要相信客户端 UI、客户端缓存资源或客户端计算出来的最终价格。

重复请求是网络 Gameplay 常见 bug。对建造/交易类操作设计 request id、sequence 或其他幂等策略，使同一逻辑请求重复到达不会重复扣费/Spawn。

## 设计规则

- 客户端只发送必要意图/参数，不发送“我已经验证合法”的结论。
- 拒绝原因可记录/返回，但不要泄露不必要安全信息。
- 服务器日志要能定位恶意/异常请求模式。

## 在 Networked Outpost 中如何落地

执行越距、改本地资源、伪造 Worker、重复提交、非法 Definition/Transform、已销毁目标七类作弊测试。

## 官方资料 / 源码阅读方向

- Epic Networking docs + GAS networking guidance


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C35 — Dedicated Server、构建目标与本地测试拓扑

**对应进度**：Week 17

## 本章工程问题

> 为什么 Listen Server 通过不代表 Dedicated Server 一定正确？

## 机制正文

Dedicated Server 没有本地玩家、渲染和许多客户端假设。任何把核心状态初始化绑到本地 PlayerController、Widget、LocalPlayer 的代码都会暴露。Server Target 让你构建专用服务器程序；测试应由脚本启动 Server + 两个独立 Client，避免 PIE 单进程隐藏问题。

Server/Client 的启动参数、地图、端口、日志目录必须脚本化，才能做重复网络实验和最终交付。

## 设计规则

- Dedicated Server 不应加载 UI/渲染依赖。
- 核心逻辑不能依赖“本地玩家一定存在”。
- 测试拓扑、延迟、丢包参数写进文档。

## 在 Networked Outpost 中如何落地

构建 Windows Server Target，脚本启动 Server + ClientA + ClientB，跑完整建造采集生产。

## 官方资料 / 源码阅读方向

- Epic 5.8: Setting Up Dedicated Servers


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C36 — Network Insights、Replication Graph 与 Iris 定位

**对应进度**：Week 17

## 本章工程问题

> 当 Actor 数量增长时，应该先优化什么？Iris 是否应该直接替代当前复制？

## 机制正文

Network Insights 用数据告诉你 Actor、属性、RPC 等流量热点；Replication Graph 主要优化大规模 Actor 的“每连接相关对象筛选/调度”问题，不会替你修复错误的状态粒度或高频 RPC。先做基线，再决定是否需要 Graph。

UE5.8 官方仍说明 Generic Replication 是默认系统；Iris 是更新的复制系统，并且部分文档仍标注需要谨慎使用实验性能力。课程因此要求理解和独立实验，不把 Iris 作为主分支硬依赖。

## 设计规则

- 先减少无意义状态/频率，再引入更复杂复制框架。
- Replication Graph 是 scaling tool，不是 Gameplay architecture。
- Iris 学习重点是理解 replication bridge/protocol/filter/prioritization 等思想。

## 在 Networked Outpost 中如何落地

200 资源点 + 50 Worker + 100 建筑；Network Insights 定位热点；实现最小空间化 RepGraph。

## 官方资料 / 源码阅读方向

- Epic 5.8 Networking Overview
- Epic: Replication Graph
- Epic: Introduction/Components of Iris


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C37 — AI 行为建模：C++ FSM、Behavior Tree、StateTree

**对应进度**：Week 18

## 本章工程问题

> 为什么“会用一个 AI 节点”不等于设计了可维护 AI？

## 机制正文

行为框架只是执行模型。C++ 状态机适合小而明确、强类型逻辑；Behavior Tree 适合层次化决策/任务组合；StateTree 结合选择与状态模型，适合清晰状态迁移和数据驱动。选择依据是任务复杂度、可视化需求、数据共享和调试体验，而不是“哪个更新”。

Worker 的真正业务状态应放在可序列化的 TaskData/Component 中，而不是只藏在 BT/StateTree 节点内。这样 SaveGame、Replication、Debugging 才不被行为工具锁死。

## 设计规则

- AI 决策结构与权威业务状态分离。
- 只选一个框架做生产实现，另一个做小型对照。
- 目标失效和取消是第一等状态。

## 在 Networked Outpost 中如何落地

实现 Idle→MoveToResource→Collect→MoveToStorage→Deposit→Complete；StateTree 主实现，BT 可做对照。

## 官方资料 / 源码阅读方向

- Epic Docs: Behavior Trees / StateTree


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C38 — Navigation 与 Animation：表现不能拥有权威结算

**对应进度**：Week 18

## 本章工程问题

> 为什么采集动画 Notify 不应该决定服务器什么时候真正增加木材？

## 机制正文

Navigation 解决路径可达性和 MoveTo 等空间执行；Animation Blueprint/State Machine/Montage/Notify 解决视觉表现同步。权威 Gameplay 状态必须能在低帧率、无渲染 Dedicated Server、动画被打断时仍保持正确，因此资源结算不应依赖某个客户端动画帧事件。

Notify 可以触发表现或向权威流程发“到达动画窗口”的信号，但最终规则必须有服务器状态机/Ability/Task 验证。

## 设计规则

- 表现系统可以丢失，权威逻辑不能依赖其必达。
- Dedicated Server 没有可见动画仍要完成业务。
- 路径失败需要明确回退/重试策略。

## 在 Networked Outpost 中如何落地

Worker locomotion + Collect montage；禁用动画或 Dedicated Server 下验证资源仍只结算一次。

## 官方资料 / 源码阅读方向

- Epic Docs: Navigation System / Animation Blueprints / Montages / Notifies


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C39 — 集中任务调度：从 N×M 扫描到事件/预算驱动

**对应进度**：Week 19

## 本章工程问题

> 为什么每个 Worker 每帧扫描所有任务是一个很好的“故意做错”实验？

## 机制正文

先做 `N workers × M tasks` 全量扫描，可以在 Unreal Insights 中得到清晰坏基线；随后把任务发布与 Worker 执行分离：TaskScheduler 维护索引/队列，任务变化触发事件或固定预算调度，Worker 只处理已经分配的 Task。这样不仅降低 CPU，也让优先级、取消、抢占、保存和复制更容易建模。

Scheduler 的宿主要基于生命周期选择：WorldSubsystem 适合随 World 存在的世界任务服务；普通 UObject 也可以由明确 World service 持有。不要因为“中央调度”就默认 GameInstance Singleton。

## 设计规则

- 先量化 O(N×M) 基线。
- AI 决策只在 Server；客户端复制必要表现状态。
- 任务保存 Stable target ID，加载后重新解析。

## 在 Networked Outpost 中如何落地

对 100 Worker 建立 Before/After Trace，记录 GameThread 时间和分配频率。

## 官方资料 / 源码阅读方向

- Epic Docs: Subsystems / Unreal Insights


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C40 — Unreal Insights：从“感觉卡”到证据链

**对应进度**：Week 20

## 本章工程问题

> 一次性能优化应如何证明？

## 机制正文

性能诊断从“Bound 类型”开始：Game Thread、Render Thread/RHI、GPU、IO/Load、网络、内存都可能造成体验问题。Unreal Insights Trace 提供 CPU scope、task、load、network 等时间线；Stat 命令适合快速 triage。先建立可重复场景和基线，再改一件事，再用相同条件复测。

报告至少记录机器、Build Configuration、Actor 数、分辨率、网络条件、采样时间和 commit。没有测试条件的数字无法比较。

## 设计规则

- 优化前先定义 metric。
- 避免只在 Editor Profiler 下得出 Shipping 结论。
- 一次改动对应一组前后数据，便于归因。

## 在 Networked Outpost 中如何落地

建立 100 Worker 压力地图；保存 before/after utrace 与简短性能报告。

## 官方资料 / 源码阅读方向

- Epic Docs: Unreal Insights / Testing and Optimizing Your Content


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C41 — UE::Tasks 与线程边界

**对应进度**：Week 20

## 本章工程问题

> 什么工作可以移出 GameThread，什么绝不能随意并行？

## 机制正文

UE::Tasks 适合把可并行的 CPU 纯计算拆成任务，但“多线程”不是把任意 Actor/UObject 操作包进 lambda。绝大部分 UObject/Actor/Component 世界状态和很多引擎 API 仍要求 GameThread 语义。正确模式往往是：GameThread 快照纯数据 → Worker Task 计算 → GameThread 应用结果。

线程优化前必须证明某段纯计算确实是热点；否则同步、拷贝和调度开销可能让方案更差。

## 设计规则

- 跨线程传 POD/不可变快照，而不是裸操作 UObjects。
- 任务取消与 owning object 生命周期必须设计。
- 结果应用回 GameThread 时再次验证世界对象。

## 在 Networked Outpost 中如何落地

选择 Worker 任务评分或空间批量计算做纯数据任务；故意跨线程访问 UObject 并记录为什么禁止/危险。

## 官方资料 / 源码阅读方向

- Epic Docs/API: Tasks System / Async Execution


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C42 — 批处理、对象池、ISM/HISM 与大量 Actor 成本

**对应进度**：Week 20

## 本章工程问题

> 大量对象的成本来自哪里，为什么“减少 Tick”只是其中一项？

## 机制正文

大量 Actor/Component 带来 Tick 注册、Transform、碰撞、网络、GC、组件管理和渲染 draw call 等多种成本。优化需要按瓶颈分层：逻辑调度可批处理/降频，表现可用 ISM/HISM 减少 draw call，短命对象可能对象池，非必要 UObject 数量可下降。

不要为了对象池而对象池：UE Actor 生命周期、网络和复杂状态重用会增加正确性成本。只有 Profile 证明 spawn/destroy 或 GC 是热点时才值得。

## 设计规则

- 优化策略必须对应具体瓶颈。
- 逻辑对象与视觉实例可以分离。
- 网络 Actor 不能仅为了渲染 ISM 化而丢失权威语义；需要拆表示层。

## 在 Networked Outpost 中如何落地

把大量静态资源点视觉表示改为 ISM/HISM 对照；记录 Game/Render/GPU 三侧差异。

## 官方资料 / 源码阅读方向

- Epic Docs: Instanced Static Mesh / Hierarchical ISM / Performance Guidelines


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C43 — UMG 生命周期与事件驱动 UI

**对应进度**：Week 21

## 本章工程问题

> 为什么 UI Tick/Property Binding 很容易把架构拖回“到处查询状态”？

## 机制正文

Widget 是表现对象，有自己的 Construct/Destruct/OnInitialized、可见性和输入生命周期。它不应该成为 Gameplay 状态 owner。事件驱动 UI 的核心是：Gameplay/Presenter 在状态变化时推送 ViewData，Widget 只渲染；页面关闭/隐藏时管理订阅与焦点。

高频打开的界面通常适合创建一次、控制 Visibility/页面栈，而不是每次 Remove/Create；但是否缓存仍要看资源与生命周期。关键是让页面状态与输入模式恢复可预测。

## 设计规则

- Widget 不直接修改 Inventory 或任意发 RPC。
- 避免 Tick 扫状态和复杂 property binding。
- Delegate 订阅要和 Widget 生命周期配对。

## 在 Networked Outpost 中如何落地

库存、建筑、失败原因、生产进度全部由事件更新；记录关闭/重开/角色重生后的订阅正确性。

## 官方资料 / 源码阅读方向

- Epic Docs: UMG UI Designer / Widget Lifecycle relevant API
- Slate Insights / Widget Reflector


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C44 — Presenter/MVVM 与 CommonUI 输入路由

**对应进度**：Week 21

## 本章工程问题

> 如何让页面不直接认识一堆 Gameplay 对象，同时稳定处理手柄/键鼠/页面栈？

## 机制正文

Presenter/ViewModel 层把 Gameplay 状态转成 UI 可消费 ViewData，并把 UI Intent 转发给命令接口。UMG MVVM 可以减少样板绑定，但不应因为框架存在就把所有逻辑搬进 ViewModel；核心仍是单向数据流和依赖方向。

CommonUI 适合复杂多层界面、页面栈、输入路由、焦点与手柄导航。它解决的是 UI interaction architecture，而不是 Gameplay input 本身。菜单打开时 Input Routing、Focus、Mouse/Controller 模式需要统一策略。

## 设计规则

- View 不知道服务器和 RPC。
- Presenter/ViewModel 不拥有权威 Gameplay。
- 页面栈比散落 AddToViewport/RemoveFromParent 更可控。

## 在 Networked Outpost 中如何落地

构建 HUD + BuildMenu + Pause/Settings 栈；键鼠和手柄切换，验证焦点恢复。

## 官方资料 / 源码阅读方向

- Epic 5.8: Common UI Plugin for Advanced User Interfaces
- UMG Viewmodel/MVVM docs


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C45 — Slate Editor Tool、Asset Registry 与生产工具

**对应进度**：Week 22

## 本章工程问题

> 怎样写一个真正解决生产问题的 Editor Tool，而不是 Hello World Tab？

## 机制正文

Slate 是 UE 原生声明式 UI 框架；Editor 工具通常还涉及 ToolMenus、Tab Manager、Asset Registry、Property Editor。Asset Registry 允许读取资产元数据和发现资产，而不必为了列表扫描就同步加载全部对象。

本课程工具以 Week 8 的 Validator 为业务核心：Slate 只负责筛选、展示、定位、导出。这样工具逻辑可以被 CI/命令行复用，并确保 OutpostEditor 不进入 Runtime Build。

## 设计规则

- 工具 UI 与 validation core 分离。
- 资产列表优先 AssetRegistry metadata，只有需要时加载。
- 处理 rename/delete/missing asset 等编辑器现实情况。

## 在 Networked Outpost 中如何落地

实现 Outpost Data Inspector：扫描、错误分级、搜索筛选、详情、双击定位、CSV/JSON 导出、一键验证。

## 官方资料 / 源码阅读方向

- Epic Docs/API: Slate / Asset Registry / ToolMenus / Property Editor


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C46 — Automation Test 与 Functional Test：测试不同层级

**对应进度**：Week 23

## 本章工程问题

> 什么逻辑适合纯 C++ 测试，什么必须进 World/网络场景？

## 机制正文

低层纯逻辑如 Inventory Add/Remove、TagQuery、Attribute clamp、migration 可用 Automation/Spec 快速测试；需要 World、Actor、移动、网络或完整 Gameplay 链的场景更适合 Functional Test 或专门测试地图。不要把所有东西都做成昂贵的端到端测试，也不要只测 helper 函数。

测试的价值是锁住工程不变量：Ability 取消无残留、无资源建造失败、双客户端看到同一建筑、Save/Load round trip。每次重构都能自动证明这些条件仍成立。

## 设计规则

- 测试层次化：pure logic → world integration → network functional。
- 失败必须返回非零/可被 CI 识别。
- 测试数据应固定，避免依赖编辑器手工环境。

## 在 Networked Outpost 中如何落地

整理 10+ 低层测试和 5+ 功能测试；至少一个网络 Functional Test 可重复运行。

## 官方资料 / 源码阅读方向

- Epic Docs: Automation Test Framework / Functional Testing


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C47 — UnrealEditor-Cmd、RunUAT 与最小 CI

**对应进度**：Week 23

## 本章工程问题

> 怎样把“我机器上能打包”升级为可重复交付流程？

## 机制正文

CI 不等于上云。第一步是本地一条命令能够：编译 → Automation → Data Validation → Cook → 构建 Client/Server → 收集日志/报告，并在任一环节失败时传播非零 Exit Code。`UnrealEditor-Cmd` 适合命令行编辑器任务/测试，RunUAT/BuildCookRun 驱动构建部署流水线。

等本地脚本稳定后，再迁移到 GitHub Actions/Jenkins/TeamCity。否则只是把不可重复的手工流程搬到服务器。

## 设计规则

- 先本地 deterministic，再 CI。
- Builds/Trace/TestReports 默认是产物，不直接污染普通 Git 历史。
- 报告关联 commit、engine version、config。

## 在 Networked Outpost 中如何落地

提供 RunTests.bat、BuildCookRun.bat、BuildServerAndClients.bat；干净环境按 README 执行。

## 官方资料 / 源码阅读方向

- Epic Docs: AutomationTool / BuildCookRun / Command-Line Arguments


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# C48 — 项目收口、源码复盘与面试表达

**对应进度**：Week 24

## 本章工程问题

> 如何把六个月学习变成可以被别人验证的工程能力？

## 机制正文

最后一周停止增加系统。重点是把“设计→问题→诊断→改进→证据”整理成故事。每个核心系统至少有一张对象/数据流图、一份关键代码、一项测试或 Trace、一个明确 trade-off。

源码复盘也不追求读完 Engine：选择与项目直接相关的调用链，例如 UObject 创建、Actor 生命周期、PlayerState/Pawn 初始化、Lyra Input→Ability、Ability Set/Tag Relationship、Replication。能指出“Lyra 哪些设计适合当前项目、哪些是规模驱动的过度设计”，比背类名更有价值。

## 设计规则

- 作品集不隐藏限制。
- 量化性能/网络指标必须附测试条件。
- 10–15 分钟讲解有主线：问题、架构、网络、安全、性能、工具、测试。

## 在 Networked Outpost 中如何落地

冻结功能、清理依赖、最终 Client/Server、README、Architecture Overview、Interview Talking Points、Demo。

## 官方资料 / 源码阅读方向

- Epic Lyra Sample + Engine Source
- 课程全部 Docs/Trace/Test artifacts


## 阅读时必须做的笔记

1. 画一张对象/数据/调用链图，不抄文档配图。
2. 写出“最容易误用的一个 API 或生命周期假设”。
3. 写出本章与前一章的依赖关系。
4. 写出一个“不采用当前方案”的反例，说明替代方案何时更好。

## 自检问题

- 如果把本章系统放到 Dedicated Server，哪些本地假设会失效？
- 如果 Actor/Pawn/Widget 在异步回调前被销毁，当前设计是否安全？
- 如果数据规模扩大 100 倍，最先暴露的是 CPU、内存、加载还是网络问题？
- 你能否不说 API 名，只用状态所有权与生命周期解释本章设计？

---

# 附录 A — UE 5.8 官方主资料索引（V4 基线）

以下页面用于 V4 主线，版本/内容在 2026-08-24 按 UE 5.8 官方文档核对：

- Programming with C++ in Unreal Engine  
  https://dev.epicgames.com/documentation/en-us/unreal-engine/programming-with-cpp-in-unreal-engine
- Epic C++ Coding Standard  
  https://dev.epicgames.com/documentation/en-us/unreal-engine/epic-cplusplus-coding-standard-for-unreal-engine
- Networking Overview  
  https://dev.epicgames.com/documentation/en-us/unreal-engine/networking-overview-for-unreal-engine
- Networking and Multiplayer  
  https://dev.epicgames.com/documentation/en-us/unreal-engine/networking-and-multiplayer-in-unreal-engine
- Setting Up Dedicated Servers  
  https://dev.epicgames.com/documentation/unreal-engine/setting-up-dedicated-servers-in-unreal-engine
- Gameplay Ability System Overview  
  https://dev.epicgames.com/documentation/en-us/unreal-engine/understanding-the-unreal-engine-gameplay-ability-system
- Using Gameplay Abilities  
  https://dev.epicgames.com/documentation/unreal-engine/using-gameplay-abilities-in-unreal-engine
- Abilities in Lyra  
  https://dev.epicgames.com/documentation/unreal-engine/abilities-in-lyra-in-unreal-engine
- Lyra Interaction System  
  https://dev.epicgames.com/documentation/unreal-engine/lyra-sample-game-interaction-system-in-unreal-engine
- Cooking and Chunking  
  https://dev.epicgames.com/documentation/en-us/unreal-engine/cooking-content-and-creating-chunks-in-unreal-engine
- Common UI  
  https://dev.epicgames.com/documentation/unreal-engine/common-ui-plugin-for-advanced-user-interfaces-in-unreal-engine
- Introduction to Iris / Components of Iris  
  https://dev.epicgames.com/documentation/unreal-engine/introduction-to-iris-in-unreal-engine  
  https://dev.epicgames.com/documentation/en-us/unreal-engine/components-of-iris-in-unreal-engine

## 附录 B — 源码阅读模板

每次源码阅读只允许带一个具体问题开始，例如：

```text
问题：SpawnActor 之后 BeginPlay 为什么不是立刻无条件调用？
公开 API：UWorld::SpawnActor
实现入口：LevelActor.cpp
关键路径：Spawn → FinishSpawning → Component Init → BeginPlay gating
结论：记录 World/Actor 是否已 begun play、deferred spawn 等条件
项目验证：用日志/断点复现实验
```

如果 30 分钟后还在“漫游类文件”，停止并重新定义问题。
