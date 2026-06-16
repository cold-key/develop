# Unreal Gameplay Engineer 转型计划（12周）

# 阶段目标

## 第一阶段（Week1~Week4）

目标：

成为合格的 Unreal 初级开发者

掌握：

* UE编辑器
* Gameplay Framework
* Blueprint
* C++
* 基础AI
* UI系统

最终成果：

完成一个资源采集Demo

---

## 第二阶段（Week5~Week8）

目标：

掌握Gameplay系统设计

掌握：

* 建造系统
* 数据驱动
* AI任务系统
* 存档系统
* 资源系统

最终成果：

完成殖民地模拟器核心框架

---

## 第三阶段（Week9~Week12）

目标：

达到求职级项目能力

掌握：

* 系统架构
* 性能优化
* 工具开发
* AI行为设计

最终成果：

完成Project Colony Alpha

---

# Week1

主题：

Unreal基础架构

学习内容：

* UObject
* UClass
* Reflection System
* Garbage Collection
* Actor
* Component
* Pawn
* Character

目标：

理解：

UE不是Unity

UE是：

Actor + Component

重点问题：

1. UObject与普通C++类区别？
2. 为什么UE需要反射系统？
3. Actor生命周期有哪些阶段？
4. Component解决了什么问题？
5. Pawn和Character区别？

实操：

实现：

* 自定义Actor
* 自定义Component
* 自定义Character

---

# Week2

主题：

Gameplay Framework

学习内容：

* GameMode
* GameState
* PlayerState
* PlayerController
* Enhanced Input
* Camera

目标：

理解：

UE如何管理整个游戏世界

重点问题：

1. GameMode和GameState区别？
2. 为什么PlayerController存在？
3. 输入为什么不直接写Character？
4. 多人游戏时谁拥有GameMode？
5. Character死亡后PlayerController怎么办？

实操：

实现：

* WASD移动
* Camera控制
* 基础交互系统

---

# Week3

主题：

Blueprint核心

学习内容：

* Blueprint Class
* Blueprint Function
* Blueprint Interface
* Event Dispatcher
* Timeline
* Blueprint Communication

目标：

掌握：

Blueprint+C++混合开发

重点问题：

1. Interface和EventDispatcher区别？
2. Blueprint什么时候比C++更适合？
3. 什么逻辑应该放Blueprint？
4. 什么逻辑应该放C++？

实操：

实现：

* 开门系统
* 拾取系统
* 简单UI交互

---

# Week4

主题：

AI基础

学习内容：

* NavMesh
* AIController
* Blackboard
* Behavior Tree
* EQS（了解）

目标：

实现NPC自主行动

重点问题：

1. AIController职责是什么？
2. Blackboard为什么存在？
3. Behavior Tree和状态机区别？
4. 为什么行为树适合游戏AI？

实操：

资源采集Demo：

工人：

发现资源
↓
移动
↓
采集
↓
返回仓库

阶段成果：

Resource Collection Demo

---

# Week5

主题：

数据驱动开发

学习内容：

* DataTable
* Struct
* PrimaryDataAsset
* Config系统

目标：

理解：

策划配置与代码解耦

重点问题：

1. 为什么不能把数值写死？
2. DataTable和DataAsset区别？
3. MMO为什么大量使用数据驱动？

实操：

建筑配置系统

---

# Week6

主题：

建造系统

学习内容：

* Grid System
* Placement System
* Building Actor
* Building Preview

目标：

实现：

类似戴森球计划建造

重点问题：

1. 为什么建造系统需要Grid？
2. 建筑数据应该存在哪里？
3. 如何实现建筑预览？

实操：

基础建造系统

---

# Week7

主题：

任务系统

学习内容：

* Task Queue
* Scheduler
* Job System

目标：

实现：

工人自动接任务

重点问题：

1. Task和Command区别？
2. Scheduler如何设计？
3. 多工人如何避免抢任务？

实操：

任务调度系统

---

# Week8

主题：

资源物流

学习内容：

* Inventory
* Resource Manager
* Storage
* Resource Transport

目标：

实现：

完整资源循环

资源
↓
采集
↓
运输
↓
存储
↓
消耗

重点问题：

1. Inventory应该放哪里？
2. ResourceManager职责是什么？
3. 如何避免资源同步问题？

阶段成果：

Colony Framework V1

---

# Week9

主题：

Save System

学习内容：

* SaveGame
* Serialization
* World State

目标：

实现：

完整存档

重点问题：

1. 为什么不能直接保存Actor？
2. 世界状态如何恢复？
3. 大型游戏如何设计存档？

实操：

存档系统

---

# Week10

主题：

项目架构

学习内容：

* Subsystem
* GameInstance
* Manager Pattern
* Service Pattern

目标：

开始工程化

重点问题：

1. 什么逻辑应该放Subsystem？
2. Manager过多有什么问题？
3. 如何避免God Object？

实操：

重构项目架构

---

# Week11

主题：

性能优化

学习内容：

* Tick优化
* Object Pool
* Profiling
* Unreal Insights

目标：

理解：

大型项目如何运行

重点问题：

1. Tick为什么昂贵？
2. 什么情况必须关闭Tick？
3. 对象池为什么有效？

实操：

优化100+工人模拟

---

# Week12

主题：

项目整合

学习内容：

* 系统复盘
* 架构整理
* GitHub整理

目标：

完成：

Project Colony Alpha

包含：

* 建造系统
* 工人系统
* 资源系统
* 调度系统
* 存档系统
* UI系统

阶段成果：

能够作为简历项目展示

---

# 三个月结束时能力要求

必须达到：

UE基础：

✓ Gameplay Framework

✓ Blueprint

✓ C++

✓ AI Controller

✓ Behavior Tree

✓ SaveGame

✓ Data Driven

系统能力：

✓ 建造系统

✓ 任务系统

✓ 调度系统

✓ 存档系统

✓ 项目架构设计

项目成果：

✓ GitHub项目

✓ 可运行Demo

✓ 项目架构图

✓ 技术文档

---

# 第四个月开始

正式进入AI Agent

学习：

* Python
* FastAPI
* OpenAI SDK
* Tool Calling
* MCP
* LangGraph

目标：

将Agent接入Project Colony

实现：

AI Colony Manager

玩家输入：

“优先发展能源产业”

Agent自动：

分析资源
↓
规划建筑
↓
分配工人
↓
执行任务

这将成为你的核心求职项目。
