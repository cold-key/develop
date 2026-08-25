
# UE Advanced Client Engineer V4 — Curriculum

> **角色**：24 周课程导航与验收表。  
> **它不负责**：在这里把 Reflection、GAS、Replication 等机制讲完。  
> **配套文件**：`V4_02_Textbook.md`（为什么/机制）与 `V4_03_Lab_Manual.md`（怎么做/实验）。  
> **目标版本**：Unreal Engine 5.8 源码构建。  
> **贯穿项目**：Networked Outpost。  
> **建议投入**：每周 30–40 小时；24 周总计约 720–960 小时。

## 0. V4 的三层阅读规则

遇到任何一周，都按下面顺序，而不是从 Curriculum 直接开始写代码：

```text
Curriculum：本周学到什么程度、验收什么
      ↓
Textbook：先建立概念模型与工程理由
      ↓
Lab Manual：按步骤实现、观察、破坏、调试
      ↓
Epic Docs / Sample / Engine Source：针对明确问题验证
      ↓
回到 Lab 重构
      ↓
按 Curriculum DoD 验收
```

如果你看到一个术语但不知道“为什么现在出现”，先回 Textbook；如果知道概念但不知道“打开 UE 后第一步做什么”，直接去 Lab Manual；如果功能已经跑通但无法证明工程质量，回 Curriculum 看 DoD。

## 1. 课程能力主线

A 线（约 35%）：GAS + Gameplay 架构，是主标签。  
B 线（约 25%）：网络 + Dedicated Server，达到独立完成服务器权威原型。  
C 线（约 15%）：UI + Editor Tooling，达到事件驱动 UI 与生产工具能力。  
D 线（约 15%）：AI + 性能，达到可调度、可保存、可复制、可量化优化。  
底层与工程质量（约 10%）：Object Model、Build、Debug、Test、Cook、Profiling、文档与源码阅读。

## 2. 每周固定节奏

- 6h：Textbook + Epic 官方资料，先建立模型。
- 14h：Lab Manual 主实验，要求持续提交而不是一口气写完。
- 3h：故障注入、断点、日志、Debugger。
- 3h：Standalone/Package/Trace/Network 测试。
- 2h：Lyra 或引擎源码对照。
- 2h：技术笔记、架构图、口述复盘。
- 可选 10h：进阶实验、源码深挖、重构、模拟面试。

## 3. 全程 Definition of Done

任何系统只有同时满足下列条件才算“学会并完成”：

1. PIE 可运行；关键周必须有 Standalone 或 Packaged Build 验证。
2. 成功路径与失败路径都有可观察结果；不能只做 happy path。
3. 核心状态不放在 Widget、Level Blueprint 或临时全局变量里。
4. 写清楚状态 owner、lifetime、修改者、网络 authority、持久化策略。
5. 至少存在一种可重复验证：Automation Test、Functional Test 或脚本化 checklist。
6. 涉及网络、加载、性能时必须留下测试条件和 Trace/指标。
7. Git 提交应按可独立回滚的实验步骤拆分。
8. 能解释“为什么选择这个 UE 系统，以及为什么不选替代方案”。

## 4. 24 周映射表

| Week | 主轴 | Textbook | Lab | 本周核心产出 | Exit Criteria |
|---:|---|---|---|---|---|
| 1 | 工程与构建底座 | C01–C03 | L01 | 源码 UE5.8、Module/Target、UBT/UHT、Git、首次打包 | 能从干净项目重新生成、编译、打包，并解释 Editor/Runtime 模块边界 |
| 2 | Unreal 对象模型 | C04–C07 | L02 | Reflection、UObject/UClass/CDO、GC、指针、Actor/Component 生命周期 | 能通过日志与源码入口解释对象创建、引用、销毁与 GC |
| 3 | Gameplay Framework 与对象职责 | C08–C10 | L03 | GameInstance/World/GameMode/GameState/PC/PS/Pawn、Component、Subsystem、Delegate/Interface | 能按状态生命周期和网络可见性选择对象，而不是创建万能 Manager |
| 4 | 输入、交互与权威边界 | C11–C12 | L04 | Enhanced Input、Query/Command、最小 RPC/RepNotify 冒烟测试 | 输入层与业务层解耦；客户端请求与权威执行边界清楚 |
| 5 | 数据驱动设计 | C13–C15 | L05 | DataAsset/DataTable、Gameplay Tags、Primary Asset、依赖图 | Definition 与 Instance 分离；Tag 命名、资产 ID 与依赖可审计 |
| 6 | 资源加载与 Cook | C16–C17 | L06 | Asset Manager、Soft Reference、异步加载、Asset Bundle、Cook | 打包版本按需加载资源；加载失败可恢复且可诊断 |
| 7 | 核心 Gameplay 纵切 | C18–C19 | L07 | Inventory、Building、Production、事务式修改、Timer、事件驱动 UI | 完成“选择→建造→生产→库存→UI”的单机纵切 |
| 8 | 存档与内容质量 | C20–C21 | L08 | SaveGame、Stable ID、版本迁移、Data Validation | 重启打包程序仍可恢复；错误数据能在编辑器阶段被阻断 |
| 9 | GAS 架构与初始化 | C22–C23 | L09 | ASC、Owner/Avatar、AttributeSet、初始化与复制 | PlayerState 持有 ASC；Respawn 后 Ability/Attribute 生命周期正确 |
| 10 | Ability / Effect / Cost / Cooldown | C24–C25 | L10 | Gameplay Ability 生命周期、Effect、Cost、Cooldown、Cue | 三个完整 Ability；失败不扣费、取消不残留、Cue 不拥有权威状态 |
| 11 | Ability Task / Target Data / Event | C26 | L11 | 异步 Ability、Target Data、Gameplay Event、取消模型 | 自定义 AbilityTask；成功/取消/目标失效/Owner 销毁均有闭环 |
| 12 | 数据驱动 Ability 与输入 | C27 | L12 | Ability Set、Input Tag、Tag Relationship、Grant/Remove | 输入不知道 Ability Class；授予来源可追踪、移除无残留 |
| 13 | GAS 网络预测与安全 | C28 | L13 | Prediction Key、Local Predicted、复制、拒绝与回滚 | 150ms 延迟与丢包下无重复扣费/Spawn，能用 GAS Debugger 解释 |
| 14 | 网络模型基础 | C29–C30 | L14 | Authority、Role、Ownership、RPC、Property Replication、RepNotify | Server + 2 Client 一致；能解释 Owning Connection 和 OnRep 边界 |
| 15 | 复制容器与网络规模 | C31–C33 | L15 | Replicated Component/Subobject、Fast Array、Relevancy、Dormancy | 至少一个 Fast Array；Dormancy 唤醒正确；网络流量有基线 |
| 16 | 网络化 Gameplay 与安全 | C34 | L16 | 幂等、服务器校验、非法请求、GAS 与普通 RPC 协作 | 作弊测试全部由服务器拒绝且能给出原因 |
| 17 | Dedicated Server 与扩展 | C35–C36 | L17 | Server Target、Network Insights、Replication Graph、Iris 定位 | 脚本启动独立 Server+Clients；能定位带宽热点并解释扩展策略 |
| 18 | Worker AI 与行为模型 | C37–C38 | L18 | StateTree/BT/C++ FSM、Navigation、Animation 基础 | Worker 完成采集运输；目标失效、路径失败、任务中断可恢复 |
| 19 | 任务调度、保存与复制 | C39 | L19 | 任务池、优先级、取消、集中调度、服务器 AI | 从“每 Worker 扫描”重构为集中调度，并保存/复制必要任务状态 |
| 20 | 性能分析与并发边界 | C40–C42 | L20 | Unreal Insights、线程模型、UE::Tasks、批处理、ISM/HISM | 有优化前后 Trace；能区分 Game/Render/GPU Bound；无跨线程 UObject 误用 |
| 21 | UI 架构 | C43–C44 | L21 | UMG 生命周期、事件驱动、Presenter/MVVM、CommonUI | UI 不轮询 Gameplay；页面栈、输入路由、焦点恢复稳定 |
| 22 | Editor Tooling | C45 | L22 | Slate、Asset Registry、Editor Tab、Validation、定位资产 | Outpost Data Inspector 可扫描、筛选、定位、导出，并与 Runtime 隔离 |
| 23 | 测试与构建自动化 | C46–C47 | L23 | Automation、Functional Test、UnrealEditor-Cmd、RunUAT、CI | 一条命令编译→测试→验证→Cook→Client/Server 构建，失败码正确 |
| 24 | 收口、源码复盘与作品集 | C48 | L24 | 性能/网络最终基线、架构文档、Lyra 对照、面试表达 | 2–3 分钟演示 + 10–15 分钟技术讲解；README 可让新环境复现 |


## 5. 七个阶段里程碑

### M1 — Week 4：工程底座 + 最小纵切

必须能够从源码引擎启动项目，解释 Module/Target/UHT，完成 Character/Input/Interaction/Command，并用 Listen Server + Client 证明一次最小 Server RPC → Replicated Property → RepNotify 链路。此时不要求“联网游戏做完”，只要求网络模型不再是抽象名词。

### M2 — Week 8：数据与内容管线

必须完成 Definition → Primary Asset → Async Load → Inventory/Building/Production → Save/Restore → Validation 的闭环。关键检查点是：运行时实例与静态定义分离；打包版本能找到资产；存档保存的是稳定数据而不是 Actor 指针。

### M3 — Week 13：GAS 深度验收

必须展示 ASC/AttributeSet、至少三个完整 Ability、Cost/Cooldown/Effect/Cue、自定义 AbilityTask、Ability Set、Input Tag、Tag Relationship，以及预测/网络实验。能解释 Owner/Avatar、Ability 与普通 Component 的边界、取消清理、预测为何不等于信任客户端。

### M4 — Week 17：网络验收

必须展示两客户端、Dedicated Server、Authority/Ownership、Fast Array、Dormancy/Relevancy、Network Insights、最小 Replication Graph；能在 150ms 延迟下完成核心循环并指出服务器拒绝非法请求的证据。

### M5 — Week 20：AI / Performance 验收

必须展示 Worker 任务系统、目标失效恢复、服务器决策、任务保存/复制、100 Worker 压力场景以及优化前后 Trace。不能用“感觉更流畅”作为性能结论。

### M6 — Week 22：UI / Tooling 验收

必须展示事件驱动 UMG、一个 Presenter/MVVM 页面、CommonUI 页面栈/输入导航、Slate Data Inspector、Data Validation 与 UI 性能检查。Runtime Build 不得包含 Editor 依赖。

### M7 — Week 24：可交付工程

必须有可构建源码、最终 Client/Server、README、架构图、测试脚本、Trace、Demo Video、Known Limitations 与 Interview Talking Points。作品集重点不是系统数量，而是可以证明设计、诊断、网络、安全与性能决策。

## 6. 阅读与跳过规则

- **已经会操作但解释不清**：跳过 Tutorial 操作，Textbook 仍需读。
- **能解释且能从零实现**：做 Lab 的验证/故障注入即可，不必重复基础代码。
- **第三方教程与本课程冲突**：以 UE 5.8 Epic 文档、实际源码和实验结果为准。
- **Lyra 看不懂**：不要硬读。先在 Networked Outpost 做一版简化实现，再带着问题对照 Lyra。
- **本周未通过 Exit Criteria**：不要靠“先学后面再说”长期滚债；最多允许一个 Week 的技术债，并在下一里程碑前清零。

## 7. 版本与资料策略

固定 UE 5.8 Release/Tag/Commit、VS、MSVC Toolset、Windows SDK。引擎升级必须独立分支验证编译、核心测试、Cook 和 Package 后再合并。Epic 官方资料按“Concept/Guide → API → Sample → Source”使用；Source 是验证机制的最后一层，不是第一层阅读材料。
