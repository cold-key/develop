# Unreal Engine 12 周学习计划

> 适用对象：有 Cocos / Cocos2d-x 与游戏客户端开发经验，正在转向 Unreal Engine，并计划做一个可写入简历的 3D 模拟经营项目。  
> 总目标：不追求“读完 UE 文档”，而是建立 UE 的运行时心智模型，并完成一个可演示、可打包的模拟经营原型。

UE 官方文档更像按系统组织的技术知识库，而不是从第一章读到最后一章的教材。学习主线应围绕 **Gameplay Framework、Blueprint 与 C++ 协作、持续扩展的小项目** 展开。

- [UE 5.8 官方文档首页](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-documentation)

---

## 学习方式与规则

每周建议投入约 **12–14 小时**：

- 白天碎片时间：每周 4 次，每次 30–40 分钟。用于读文档、画执行链路、整理疑问。
- 晚上实操：每周 4 次，每次约 2 小时。
- 周末：3–4 小时。用于复盘、整理代码、录制演示。

固定学习顺序：

```text
概览文档
→ 一个官方教程 / How-to
→ 在自己的项目里重做
→ 遇到具体问题时再查 API Reference
```

不要：

- 从文档首页一路读到最后。
- 一开始读 GAS、网络同步、Mass、Lyra 源码、完整渲染管线。
- 为了记住所有 `UPROPERTY` / `UFUNCTION` Specifier 而停滞。
- 把练习工程直接演变成最终简历项目。

---

# 阶段一：建立 UE 的运行时地图（第 1–3 周）

学习工程：`UE_LearningLab`  
模板：**Third Person + C++ + Starter Content**

前几周优先使用 Blueprint。创建 C++ 工程的目的，是为后面加入 C++ 做准备，而不是立刻大量写代码。

---

## 第 1 周：编辑器、工程、资产与关卡

### 目标

熟悉 UE 的基本工作方式，不写复杂逻辑。

### 阅读

- [创建第一个 UE 项目](https://dev.epicgames.com/documentation/unreal-engine/create-your-first-project-in-unreal-engine)
- [UE 基础总览](https://dev.epicgames.com/documentation/unreal-engine/understanding-the-basics-of-unreal-engine)
- [Your First Hour in Unreal Engine](https://dev.epicgames.com/documentation/unreal-engine/first-hour-in-unreal-engine)
- [模板参考：Third Person / Top Down / First Person](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-templates-reference)

### 实操产出

1. 建立 Git 仓库，并提交初始工程。
2. 新建关卡：`L_TestRoom`。
3. 放入地面、光源、墙体、一个 Static Mesh。
4. 在 Content Browser 中建立并整理目录：

```text
Content/
├─ Blueprints/
├─ Characters/
├─ Input/
├─ UI/
├─ Data/
├─ Maps/
├─ Materials/
└─ Meshes/
```

5. 在 `Project Settings` 与 `World Settings` 中找到 GameMode 配置位置。
6. 录制一段约 30 秒视频：从编辑器启动 PIE，角色进入你制作的小房间。

### 本周验收

你能解释并实际操作：

- `Project`
- `Level`
- `World`
- `Asset`
- `Actor`
- PIE（Play In Editor）

你能独立创建地图、摆放资源、运行游戏。

---

## 第 2 周：Actor、Component 与 Gameplay Framework

### 目标

建立 UE 最重要的一张对象关系图。

### 阅读

- [Gameplay Framework](https://dev.epicgames.com/documentation/unreal-engine/gameplay-framework-in-unreal-engine)
- [Gameplay Framework Quick Reference](https://dev.epicgames.com/documentation/unreal-engine/gameplay-framework-quick-reference-in-unreal-engine)
- [Components](https://dev.epicgames.com/documentation/unreal-engine/components-in-unreal-engine)

### 必须画出的运行时关系图

```text
GameInstance
  └─ World / Level
      └─ GameMode
          └─ PlayerController
              └─ Possess
                  └─ Pawn / Character
                      ├─ CapsuleComponent
                      ├─ CharacterMovement
                      ├─ CameraComponent
                      └─ MeshComponent
```

### 实操产出

1. 新建 `BP_TestActor`。
2. 给它添加：
   - `SceneComponent`
   - `StaticMeshComponent`
   - `BoxCollision`
   - `RotatingMovementComponent`
3. 在 `BeginPlay` 打印对象名。
4. 在 `Tick` 中旋转或移动该 Actor。
5. 创建 `BP_TestGameMode`，替换默认 Pawn。
6. 新建一个 Character Blueprint，确认替换 GameMode 后实际生成的角色发生变化。

### 本周验收

你能回答：

- `GameMode` 与 `GameInstance` 的区别是什么？
- `PlayerController` 为什么不等于 Character？
- `ActorComponent`、`SceneComponent`、`PrimitiveComponent` 分别是什么？
- Mesh、碰撞、相机为什么通常是 Component，而不是独立 Actor？

### 与 Cocos 的粗略映射

```text
Cocos 节点 / 实体
≈ UE Actor

节点上的功能组件
≈ UE ActorComponent / SceneComponent

玩家可控制单位
≈ Pawn / Character

输入和玩家控制逻辑
≈ PlayerController

场景规则、出生规则、默认角色
≈ GameMode

跨场景常驻管理器
≈ GameInstance / Subsystem
```

---

## 第 3 周：Blueprint 基础与通信

### 目标

先掌握 UE 的可视化对象组合和事件流，再切入 C++。

### 阅读

- [Blueprint Foundations](https://dev.epicgames.com/documentation/unreal-engine/blueprint-foundations)
- [Blueprint Visual Scripting 概览](https://dev.epicgames.com/documentation/unreal-engine/blueprints-visual-scripting-in-unreal-engine)
- [Blueprint Communication Usage](https://dev.epicgames.com/documentation/unreal-engine/blueprint-communication-usage-in-unreal-engine)
- [Blueprint Interface](https://dev.epicgames.com/documentation/unreal-engine/blueprint-interface-in-unreal-engine)
- [Event Dispatchers](https://dev.epicgames.com/documentation/unreal-engine/event-dispatchers-in-unreal-engine)

### 实操产出

在测试房间完成：

```text
BP_Switch
→ 通过 Blueprint Interface
→ 控制 BP_Door 开门 / 关门
```

要求：

- 不在 `BP_Switch` 中硬编码 Door 的具体类逻辑。
- Door 自己持有开门状态。
- 添加 `OnDoorStateChanged` Event Dispatcher。
- 使用一个灯或 UI 文本订阅门状态变化。

### 本周验收

你能区分：

```text
直接引用：明确知道目标是谁。
Cast：确认目标具体类型后调用其能力。
Blueprint Interface：只要求“目标具备该能力”。
Event Dispatcher：一个对象广播，多个对象订阅。
```

---

# 阶段二：完成第一个 Gameplay 小闭环（第 4–5 周）

---

## 第 4 周：Enhanced Input、碰撞与交互

### 目标

完成“玩家看见物体 → 识别物体 → 触发交互”的完整链路。

### 阅读

- [Enhanced Input](https://dev.epicgames.com/documentation/unreal-engine/enhanced-input-in-unreal-engine)
- [Collision Overview](https://dev.epicgames.com/documentation/unreal-engine/collision-in-unreal-engine---overview)
- [Collision 文档入口](https://dev.epicgames.com/documentation/unreal-engine/collision-in-unreal-engine)

### 实操产出

1. 新建 `IA_Interact`，映射到 `E`。
2. 用 Camera Forward Vector 做 Line Trace。
3. 可交互物实现 `BPI_Interactable`。
4. 制作两个对象：
   - `BP_PickupResource`：拾取后消失。
   - `BP_Door`：交互后开关。
5. 创建自定义 Trace Channel：`Interactable`。
6. 用 `Draw Debug` 显示射线与命中结果。

### 必须理解的输入链路

```text
E 键
→ IMC_Default
→ IA_Interact
→ Character / PlayerController 输入事件
→ Line Trace
→ Hit Actor
→ BPI_Interactable
→ 目标对象执行 Interact
```

### 本周验收

你能解释：

- `Input Action` 与 `Input Mapping Context` 的职责。
- 为什么交互更适合使用 Trace，而不是仅用 Overlap。
- Object Type、Trace Channel、Block / Overlap / Ignore 分别控制什么。

---

## 第 5 周：UMG、状态更新与第一个纵切

### 目标

完成一个可演示的小型交互原型。

### 阅读

- [UMG UI Designer Quick Start](https://dev.epicgames.com/documentation/unreal-engine/umg-ui-designer-quick-start-guide-in-unreal-engine)
- [创建用户界面：UMG 与 Slate](https://dev.epicgames.com/documentation/unreal-engine/creating-user-interfaces-with-umg-and-slate-in-unreal-engine)
- [UMG Best Practices](https://dev.epicgames.com/documentation/unreal-engine/umg-best-practices-in-unreal-engine)

### 实操产出

完成以下纵切：

```text
移动
+ 视角
+ E 交互
+ 资源拾取
+ 门开关
+ 屏幕交互提示
+ 左上角资源数量 UI
```

### 实现要求

- UI 不要每帧 Tick 查询资源数量。
- 资源数量变化时，通过 Dispatcher 或函数主动更新 UI。
- 用一个简单 `BP_PlayerInventoryComponent` 保存资源数量。

### 本周验收

录制一段 1 分钟视频，展示完整流程。

完成这一周后，再去学习 First-Person Adventure C++ 教程会明显轻松许多。

---

# 阶段三：UE C++ 与数据驱动（第 6–8 周）

> 前置：你已经能用 Blueprint 完成移动、交互、拾取和 UI 的小闭环。

官方教程：

- [Code a First-Person Adventure Game in Unreal Engine](https://dev.epicgames.com/documentation/unreal-engine/code-a-firstperson-adventure-game-in-unreal-engine)

---

## 第 6 周：UE C++ 基本工作流

### 目标

理解 UE C++ 不是“普通 C++ 直接写进项目”，而是和反射、编辑器、Blueprint 协作的工作流。

### 阅读

- [UE C++ Quick Start](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-cpp-quick-start)
- [Programming with C++](https://dev.epicgames.com/documentation/unreal-engine/programming-with-cplusplus-in-unreal-engine)
- [First-Person Adventure：Set Up and Compile](https://dev.epicgames.com/documentation/unreal-engine/coder-01-set-up-and-compile-a-cplusplus-project-in-unreal-engine)
- [First-Person Adventure：Create a Player Character With Input Actions](https://dev.epicgames.com/documentation/unreal-engine/coder-02-create-a-player-character-with-input-actions-in-cplusplus)

### 实操产出

创建一个 C++ 类：

```cpp
AResourcePickup : public AActor
```

至少包含：

```text
UStaticMeshComponent
USphereComponent

UPROPERTY(EditAnywhere)
DisplayName
ResourceAmount
```

再创建 Blueprint 子类：

```text
BP_ResourcePickup
```

要求：

- 能在 Blueprint 的 Details 面板中配置资源数量。
- 能配置 Mesh。
- 放到地图后可以正常运行。

### 本周重点

只要求理解：

```text
UCLASS
UPROPERTY
UFUNCTION
.h / .cpp
Build.cs
C++ 父类
Blueprint 子类
```

暂时不要深挖：

```text
GC
CDO
Soft Reference
UHT 的完整细节
反射系统底层实现
```

---

## 第 7 周：输入、角色与生命周期

### 目标

把已有 Blueprint 功能的一部分迁移到 C++，理解哪些逻辑适合放在哪里。

### 阅读

- [First-Person Adventure：Configure Character Movement](https://dev.epicgames.com/documentation/unreal-engine/coder-03-configure-character-movement-with-cplusplus-in-unreal-engine)
- [First-Person Adventure：Add a First-Person Camera, Mesh, and Animation](https://dev.epicgames.com/documentation/unreal-engine/coder-04-adding-a-firstperson-camera-mesh-and-animation)
- [Actor Lifecycle](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-actor-lifecycle)

### 实操产出

将第 4 周 Blueprint 交互系统逐步迁移一部分到 C++：

```text
C++：
- 交互射线检测
- 可交互对象基类或 C++ Interface
- 资源数量数据

Blueprint：
- 具体资源表现
- Mesh / 材质 / 音效配置
- 门的动画与关卡摆放
```

### 本周验收

你能解释：

```text
Constructor：创建默认子对象、设置默认值。
BeginPlay：游戏运行时初始化。
Tick：每帧逻辑，只在确实需要时使用。
SpawnActor：运行时生成 Actor。
UPROPERTY：让 UE 的反射、序列化、编辑器与 GC 体系认识变量。
```

---

## 第 8 周：数据驱动、物品与存档

### 目标

让物品和资源数据脱离硬编码，并能够跨游戏会话保存状态。

### 阅读

- [First-Person Adventure：Manage Items and Data](https://dev.epicgames.com/documentation/unreal-engine/coder-05-manage-item-and-data-in-an-unreal-engine-game)
- [Data-Driven Gameplay Elements](https://dev.epicgames.com/documentation/unreal-engine/data-driven-gameplay-elements-in-unreal-engine)
- [Saving and Loading Your Game](https://dev.epicgames.com/documentation/unreal-engine/saving-and-loading-your-game-in-unreal-engine)

### 实操产出

1. 定义 `FResourceDefinition` 或 `FItemDefinition`。
2. 建立一个 DataTable，至少包含：

```text
Id
DisplayName
Icon
Mesh
BaseValue
StackLimit
```

3. 将资源 Actor 改成只持有 `RowName` 或 Id。
4. 制作 `USaveGame`：
   - 当前资源数量；
   - 玩家位置；
   - 已拾取资源列表。
5. 完成 Save / Load 按钮或快捷键测试。

### 本周验收

你能解释：

- DataTable 为什么能够降低逻辑代码与数值配置的耦合。
- `RowName` 在数据表驱动设计中的作用。
- `SaveGame` 中应该保存“数据”，而不是直接保存整个 Actor 对象。
- 加载时为什么需要重新生成或恢复世界状态。

---

# 阶段四：简历原型——俯视角模拟经营（第 9–12 周）

从第 9 周开始，**新建一个干净工程**：

```text
OutpostPrototype
```

模板：

- [Top Down Template](https://dev.epicgames.com/documentation/unreal-engine/top-down-template-in-unreal-engine)

建议项目名称：

```text
《前哨基地 / Outpost Prototype》
```

核心循环限定为：

```text
采集资源
→ 消耗资源建造设施
→ 设施按时间生产
→ UI 展示库存与产出
→ 保存并恢复世界状态
```

明确不要加入：

```text
战斗
联网
复杂动画
开放世界
程序化地形
复杂经济系统
大量建筑种类
```

---

## 第 9 周：俯视角控制、资源节点与点击选取

### 实操产出

1. 镜头移动、缩放、旋转。
2. 鼠标点击地面与资源节点。
3. 资源节点显示选中状态。
4. 建立三个基础 Actor：
   - `ResourceNode`
   - `Storage`
   - `Workshop`
5. 用 DataTable 描述资源和建筑配置。

### 本周验收

玩家能选中矿石节点，UI 显示：

```text
资源名称
剩余量
采集价值
```

---

## 第 10 周：建筑放置与生产循环

### 实操产出

1. 建筑预览 Ghost。
2. 地面合法性检查。
3. 消耗资源建造。
4. 建筑使用 Timer 自动生产。
5. UI 显示：

```text
木材 / 矿石 / 金属
当前建筑
每分钟产量
```

### 架构要求

```text
C++：
- BuildingBase
- ResourceInventoryComponent
- ProductionComponent
- 数据结构与基础状态

Blueprint：
- 各具体建筑
- Mesh、特效、音效
- 建筑配置与展示
```

### 本周验收

完整流程可运行：

```text
选择建筑
→ 预览摆放
→ 检查是否合法
→ 扣除资源
→ 建筑生成
→ Timer 驱动产出
→ UI 更新库存
```

---

## 第 11 周：基础 AI、导航与世界保存

### 阅读

- [Behavior Trees](https://dev.epicgames.com/documentation/unreal-engine/behavior-trees-in-unreal-engine)
- [Gameplay Tutorials](https://dev.epicgames.com/documentation/unreal-engine/gameplay-tutorials-for-unreal-engine)
- [Saving and Loading Your Game](https://dev.epicgames.com/documentation/unreal-engine/saving-and-loading-your-game-in-unreal-engine)

### 实操优先级

1. 保存建筑类型、位置、旋转、库存、生产状态。
2. Load 后正确恢复建筑。
3. 添加一个 Worker：
   - 寻路到资源点；
   - 采集；
   - 运回仓库。
4. Worker AI 使用最简单状态机或 Behavior Tree。

### 本周验收

至少能展示：

```text
保存游戏
→ 退出 / 重启
→ 读取存档
→ 建筑、库存、资源状态恢复
```

Worker AI 只需要能表现一个可视化循环，不要求复杂决策。

---

## 第 12 周：调试、打包、作品集整理

### 阅读

- [Unreal Insights](https://dev.epicgames.com/documentation/unreal-engine/unreal-insights-in-unreal-engine)
- [Trace Quick Start](https://dev.epicgames.com/documentation/unreal-engine/trace-quick-start-guide-in-unreal-engine)
- [Packaging Unreal Engine Projects](https://dev.epicgames.com/documentation/unreal-engine/packaging-your-project)
- [Samples and Tutorials](https://dev.epicgames.com/documentation/unreal-engine/samples-and-tutorials-for-unreal-engine)

### 实操产出

1. 用 `stat unit`、`stat fps` 检查基础性能。
2. 用 Unreal Insights 抓一次运行 Trace。
3. 清理无用 Tick。
4. 打包 Windows 可执行版本。
5. 编写 `README.md`，至少包含：
   - 项目简介；
   - 核心循环；
   - 类图；
   - C++ 与 Blueprint 的职责划分；
   - DataTable 设计；
   - 存档结构；
   - 已知问题；
   - 下一步计划。
6. 录制 2–3 分钟演示视频。

### 最终交付物

```text
OutpostPrototype/
├─ 可运行 Windows 打包版本
├─ Git 仓库
├─ README.md
├─ 架构图
├─ 2–3 分钟演示视频
└─ 若干关键功能截图
```

---

# 12 周后应达到的能力

```text
1. 能解释 UE Gameplay Framework 的对象职责和创建链路。
2. 能用 Blueprint 快速搭建 Gameplay 功能。
3. 能用 C++ 定义可复用系统，再用 Blueprint 配置与扩展。
4. 能实现输入、交互、UI、碰撞、数据表、存档。
5. 能完成一个最小但完整的 3D 模拟经营 Gameplay Loop。
6. 能打包项目、录制演示，并讲清楚自己的架构取舍。
```

---

# 延后学习的内容

在完成单机原型前，以下内容先不作为主线：

```text
GAS
多人网络复制
Lyra 完整源码
Mass Entity
World Partition
复杂动画系统 / Motion Matching
Nanite、Lumen 深度调优
插件开发
UE 源码编译与引擎层修改
```

它们都值得学习，但应该建立在你已经能独立完成单机 Gameplay 原型之后。

---

# 每篇文档的固定阅读模板

以后打开任意 UE 文档时，都先回答这五个问题：

```text
1. 这个系统解决什么问题？
2. 它的核心对象有哪些？
3. 谁创建它、谁持有它、什么时候销毁？
4. 它在运行时的调用链是什么？
5. 我能立刻做什么小实验验证它？
```

示例：Enhanced Input

```text
解决什么：
把设备输入映射为游戏语义行为。

核心对象：
Input Action、Input Mapping Context、
Enhanced Input Component、Local Player Subsystem。

调用链：
键盘 → IMC → IA_Move → 绑定函数
→ AddMovementInput → CharacterMovement。

立即实验：
删掉 IMC，确认角色为什么无法移动。
```

---

# 遇到卡点时的规则

当一篇教程中连续出现 **三个你解释不清的术语** 时，暂停继续抄代码。

例如：

```text
LocalPlayerSubsystem
Input Mapping Context
TObjectPtr
```

此时只补其中 **一个最底层概念**，再回到原教程继续。

不要同时打开十几个链接，否则很容易被文档分支带走。
