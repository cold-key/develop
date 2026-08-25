
# UE Advanced Client Engineer V4 — Networked Outpost Lab Manual

> **职责**：告诉你“打开电脑以后具体做什么”。  
> 每个 Lab 都必须先阅读 Curriculum 对应周的 Exit Criteria，再读 Textbook 对应章节。  
> 这里的步骤不是让你机械照抄；每一步都包含可观察结果和故障注入。完成实验后必须能脱离步骤重新实现核心链路。

## 通用实验纪律

1. 每个 Lab 建独立 Git branch 或至少使用可回滚 commit 序列。
2. 先跑现有测试/打包，确认起点是绿色；再开始改动。
3. 每完成 1–3 个有意义步骤就提交一次，不把一周工作压成一个 commit。
4. 新系统首先建立日志 category / debug display / test seam，再增加 UI。
5. 故障注入不是可选项：主动破坏生命周期、网络条件、数据或资源，验证诊断能力。
6. Lab 结束必须填写 `Docs/WeekXX_Retrospective.md`：做了什么、踩了什么坑、为什么这样设计、如果规模扩大如何演进。

---

# L01 — Week 1: 工程底座与第一次可运行包

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 1，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 确认 UE 5.8 源码分支/Tag/Commit，并记录 VS、MSVC、Windows SDK。
2. 运行 Setup.bat、GenerateProjectFiles.bat；用 Development Editor/Win64 编译 UE5 并从源码目录启动 UnrealEditor。
3. 创建 Networked Outpost C++ 项目；只建 `OutpostRuntime` 与 `OutpostEditor` 两模块。
4. 为两模块配置 Public/Private 与最小依赖；Runtime 不依赖 UnrealEd/Slate editor modules。
5. 创建 `LogOutpost`、`LogOutpostEditor`；加入启动地图和最小 GameMode。
6. 建立 `.gitignore`、Git LFS 规则与提交约定；Builds/SavedProfiling/TestReports 默认忽略。
7. 编写 `BuildDevelopment.bat`；再写 `VerifyWeek01.bat`：清理→编译 Editor→BuildCookRun→检查 exit code/exe/editor binary leakage。
8. 执行一次干净验证并保存终端日志。

## 本周故障注入

- 删掉项目 Binaries/Intermediate 后重建。
- 故意让 OutpostRuntime include UnrealEd 类型，观察 Game/Package 构建失败并修复。
- 故意写错项目路径，确认脚本返回非 0。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/00_EnvironmentAndEngineVersion.md`
- `Docs/01_ProjectBuildAndSourceControl.md`
- `Scripts/BuildDevelopment.bat`
- `Scripts/VerifyWeek01.bat`


## 推荐 Commit 切分

```text
week01/01-scaffold-or-model
week01/02-core-path
week01/03-failure-handling
week01/04-tests-and-debug
week01/05-package-or-trace
week01/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L02 — Week 2: 对象模型实验：Reflection → CDO → GC → Lifecycle

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 2，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 创建 `Experiments/OutpostObjectExperiment.h/.cpp`，先写普通 `FNormalItem`，再写 `USTRUCT FOutpostItemStack`。
2. 编译后在 Intermediate generated code 中定位 `StaticStruct`/注册信息；只记录结构，不要求读懂全部宏。
3. 创建 `UOutpostItemDefinition : UPrimaryDataAsset`，打印对象名、Class、Flags、Outer、是否 CDO。
4. 创建 `AOutpostPickupActor`：构造函数、PostInitializeComponents、BeginPlay、EndPlay 写带对象名的日志。
5. 在构造函数创建默认组件；运行时再动态 NewObject/SpawnActor，对比 Outer/Owner/World。
6. 分别用 `TObjectPtr`、`TWeakObjectPtr`、`TSoftObjectPtr` 保存合适引用；制造 Actor Destroy 后 Weak 失效。
7. 做 5 组 Actor 生命周期实验：Editor 放置、PIE、Runtime Spawn、Destroy、Level 切换。
8. 把观察结果画成 Object/Lifecycle 图，并明确“Destroy 与 GC 不是同一步”。

## 本周故障注入

- 把依赖 World 的逻辑故意放构造函数，记录为什么结果不可靠。
- 移除一个强引用并触发 GC，观察对象可达性变化。
- 在异步/Timer 回调前销毁 Actor，验证弱引用防护。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/02_ObjectModel.md`
- `Docs/02_ActorComponentLifecycle.md`
- `Tests/ObjectPointerExperiment`


## 推荐 Commit 切分

```text
week02/01-scaffold-or-model
week02/02-core-path
week02/03-failure-handling
week02/04-tests-and-debug
week02/05-package-or-trace
week02/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L03 — Week 3: Gameplay Framework、Component、Subsystem 与诊断

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 3，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 创建 OutpostGameMode/GameState/PlayerController/PlayerState/Character。
2. 为每类写 `Owner / Lifetime / Network Visibility / Responsibilities` 注释，不超过 5 条职责。
3. 创建 GameInstanceSubsystem、WorldSubsystem、InteractionComponent、ProductionComponent；解释每个宿主选择。
4. InteractionComponent 不直接认识 Widget；先用日志输出交互目标。
5. 为运行时状态变化使用 Native Delegate；为跨类型交互定义明确 Interface。
6. 给 Interaction 添加 Visual Logger 信息；Gameplay Debugger 显示当前目标/资源。
7. 故意制造一个空目标/错误配置，用 ensure + 日志 + 调用栈写一份排错记录。

## 本周故障注入

- 把玩家资源暂时放 Character，模拟 Respawn，观察为什么需要重新判断状态归属。
- 把 World 级服务错误放 GameInstanceSubsystem，再做地图切换分析生命周期差异。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/03_GameplayFrameworkAndDiagnostics.md`
- `Docs/03_ObjectOwnershipDiagram.png`


## 推荐 Commit 切分

```text
week03/01-scaffold-or-model
week03/02-core-path
week03/03-failure-handling
week03/04-tests-and-debug
week03/05-package-or-trace
week03/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L04 — Week 4: Enhanced Input、Interaction Query、Command 与网络冒烟

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 4，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 创建 IA_Interact、IA_Build 与 IMC_Gameplay；通过 LocalPlayerSubsystem 安装 Context。
2. 实现 `UOutpostInputConfig`，让输入代码只输出语义 Action/Tag。
3. 实现 `FOutpostInteractionQuery/Result` 和 `UOutpostInteractableInterface`；InteractionComponent 负责 Trace/候选优先级。
4. 实现 `FOutpostCommandRequest/Result` 与 `UOutpostCommandComponent`；把 Request/Validate/Execute 分开。
5. 单机先跑 `Input → Query → Command → Result`，加入目标无效/距离不足/条件不满足三类失败。
6. 建最小网络测试 Actor/PC：Client 在 owned actor 发 Server RPC；Server 改 Replicated int；Client OnRep 打日志。
7. 临时让 RPC 从非 owned actor 发出，观察失败并记录 Ownership 结论。
8. 运行命令行 Automation Test 或 Editor Automation Test 验证 Interaction Query。

## 本周故障注入

- 删除 IMC，确认业务逻辑本身不依赖硬件键。
- 重复请求 Command，观察现阶段是否会重复执行，记录 Week16 需要解决的幂等问题。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/04_InputInteractionCommandAuthority.md`
- `Docs/04_NetworkSmokeTest.md`
- `Tests/InteractionQuery`


## 推荐 Commit 切分

```text
week04/01-scaffold-or-model
week04/02-core-path
week04/03-failure-handling
week04/04-tests-and-debug
week04/05-package-or-trace
week04/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L05 — Week 5: Definition、Gameplay Tags 与 Primary Assets

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 5，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 创建 Item/Building/Worker/Ability Definition DataAsset 类。
2. 字段至少含 ID、DisplayName、Description、GameplayTags、RuntimeClass、VisualClass、Costs、Soft References。
3. 建立 Native Gameplay Tag 命名：Item/Building/Ability/State/Failure 五大树。
4. 把原有字符串类型判断替换为 Tag/ID；保留真正封闭状态的 enum。
5. 为 Definition 实现/配置稳定 PrimaryAssetId。
6. 使用 Reference Viewer/Size Map 检查每类 Definition；修掉至少一个不必要硬引用。
7. 此时再把 Runtime 拆为 OutpostCore + OutpostGameplay，证明依赖方向后再拆。

## 本周故障注入

- 故意添加一个大型 Blueprint 硬引用，比较依赖图。
- 建立错误 Tag 层级，写 Tag Query 测试暴露问题。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/05_DataDrivenDesignAndTags.md`
- `Content/Data/`


## 推荐 Commit 切分

```text
week05/01-scaffold-or-model
week05/02-core-path
week05/03-failure-handling
week05/04-tests-and-debug
week05/05-package-or-trace
week05/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L06 — Week 6: AssetManager、异步加载与 Cook 失败恢复

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 6，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 实现 `UOutpostAssetManager` 并配置 Primary Asset Types to Scan。
2. 实现 `FOutpostAssetLoadRequest` 或等价请求对象，保存 Handle、请求上下文与取消状态。
3. 启动只加载轻量 Definition；打开建筑菜单加载 Icon bundle；确认放置加载 World/Gameplay bundle。
4. 同一资产发两个请求，决定合并/复用策略并记录。
5. 关闭 UI/销毁调用者后再让加载完成，确保回调不会访问无效对象。
6. 记录 Load Start/Success/Failure/Duration。
7. 执行 Development Cook+Package，确认 Primary Asset 可发现。
8. 故意去掉一项 Cook/Scan 配置复现 Package 缺资产，然后按 AssetRegistry/Cook/Stage/Runtime request 四层排查。

## 本周故障注入

- 强制加载一个不存在的 soft path，UI 必须从 Loading 转 Failed。
- 比较同步加载与异步加载 Trace。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/06_AssetManagerAsyncLoadingAndCook.md`
- `SavedProfiling/Week06_AssetLoading.utrace`
- `Builds/Week06/`


## 推荐 Commit 切分

```text
week06/01-scaffold-or-model
week06/02-core-path
week06/03-failure-handling
week06/04-tests-and-debug
week06/05-package-or-trace
week06/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L07 — Week 7: Inventory、Building、Production 与第一个纵切

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 7，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 实现 InventoryComponent：CanAdd/Add/CanRemove/Remove/CanAfford/ConsumeCost，内部容器不外露。
2. 给 Inventory 操作返回结构化 Result/FailureTag；写 stack、overflow、insufficient、rollback 测试。
3. 实现 Building/ProductionComponent 与 Building Actor、ResourceNode。
4. 实现本地 Building Preview，但 Preview 不改权威库存/世界。
5. 流程：Validate config/location → ConsumeCost → Spawn building；任何中间失败可回滚。
6. Production 用 Timer/明确状态，不用每建筑无条件 Tick；完成后产物进入 Inventory。
7. Delegate 推送资源/进度/失败给最小 UMG；Widget 不写 Inventory。
8. Standalone + Package 完整跑一次从选择到生产。

## 本周故障注入

- 把生产 Timer 改成依赖帧计数，制造不同帧率结果，再恢复。
- 让 Spawn 失败在扣费之后发生，验证事务/回滚。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/07_CoreGameplayVerticalSlice.md`
- `Tests/InventoryAndBuildingCost`
- `Demo/Week07_VerticalSlice.mp4`


## 推荐 Commit 切分

```text
week07/01-scaffold-or-model
week07/02-core-path
week07/03-failure-handling
week07/04-tests-and-debug
week07/05-package-or-trace
week07/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L08 — Week 8: SaveGame、版本迁移与 Data Validation

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 8，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 定义 Building/Inventory/Production/Worker/World SaveData，只存纯数据和 Stable ID。
2. 为运行实例分配 Stable Instance ID；跨对象引用只保存 ID。
3. 实现保存：Definition ID、Transform、Inventory、Production Queue/剩余时间、Worker task data。
4. 实现加载分阶段：read/version→migrate→spawn shells→restore local state→resolve refs→broadcast refresh。
5. 退出 Packaged Build，重新启动并加载验证。
6. 制造 V1 Save；新增字段/结构为 V2，实现迁移。
7. 在 OutpostEditor 创建 Validator：重复 ID、必填空、负 Cost、Tag、RuntimeClass、软引用不存在。
8. 让 Validator 输出资产路径+字段+原因。

## 本周故障注入

- SaveData 中故意放 Actor pointer，说明为什么跨进程无意义。
- 删除一个 Definition 后加载旧存档，设计可诊断失败/降级策略。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/08_SaveVersioningAndDataValidation.md`
- `Tests/SaveLoadRoundTrip`
- `OutpostEditor/DataValidator`


## 推荐 Commit 切分

```text
week08/01-scaffold-or-model
week08/02-core-path
week08/03-failure-handling
week08/04-tests-and-debug
week08/05-package-or-trace
week08/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L09 — Week 9: GAS：ASC、AttributeSet、Owner/Avatar 与 Respawn

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 9，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 启用 GameplayAbilities/GameplayTags/GameplayTasks；拆 `OutpostAbilities` 模块。
2. 实现 OutpostASC、AttributeSet、GameplayAbility、AbilitySet 基类。
3. PlayerState 创建/拥有 ASC；Character 实现/转发 AbilitySystemInterface 并作为 Avatar。
4. 明确 Server/Client 初始化点，调用 InitAbilityActorInfo；日志记录 Owner/Avatar/NetRole。
5. 实现 Health/MaxHealth/Energy/BuildResource/CarryCapacity/MoveSpeed；基础初始化用 GE 或明确策略。
6. Attribute replication + RepNotify；Clamp/初始化写测试。
7. 销毁 Pawn 并 Respawn，验证 PlayerState ASC 和应持久 Ability 仍存在，Avatar 更新。
8. 对照 Lyra PlayerState/PawnExtension 只回答“它如何避免初始化顺序问题”。

## 本周故障注入

- 故意跳过 InitAbilityActorInfo，复现 Ability 激活失败。
- 把 ASC 暂时放 Character，做 Respawn 对照并写 trade-off。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/09_GASArchitectureAndInitialization.md`
- `Docs/09_ASC_Owner_Avatar_Diagram.png`
- `Tests/GASAttributeInitialization`


## 推荐 Commit 切分

```text
week09/01-scaffold-or-model
week09/02-core-path
week09/03-failure-handling
week09/04-tests-and-debug
week09/05-package-or-trace
week09/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L10 — Week 10: 三个完整 Ability：Build / Collect / Dash

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 10，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 实现 GA_Build、GA_Collect、GA_Dash(或 Interact)；每个先画 Activate→Commit→End/Cancel。
2. 配置 Instancing/NetExecution/Ability Tags/Required/Blocked。
3. 创建 GE_BuildCost、CollectReward、DashCost、DashCooldown。
4. Build 的资源不足必须 CanActivate/Commit 失败，不允许先扣费。
5. Dash cooldown UI 从 Tag/Active GE 读取，不另存一份倒计时真相。
6. Gameplay Cue 只做建造/采集表现。
7. 覆盖成功、条件失败、外部 Cancel、死亡取消、重复输入。
8. Automation Test 验证 Cost/Cooldown/Grant/Activate 的关键不变量。

## 本周故障注入

- Ability 中故意直接调用 Widget，再按依赖方向重构。
- 让 Ability 成功路径触发两次 Commit，写防重复规则。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/10_AbilityEffectCostCooldownCue.md`
- `Tests/AbilityActivationAndCost`


## 推荐 Commit 切分

```text
week10/01-scaffold-or-model
week10/02-core-path
week10/03-failure-handling
week10/04-tests-and-debug
week10/05-package-or-trace
week10/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L11 — Week 11: AbilityTask、TargetData 与取消模型

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 11，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. Build Ability 激活后创建本地 preview。
2. 实现/选择持续目标检测：Timer/trace 返回 candidate transform。
3. 创建 `UAbilityTask_WaitValidBuildingPlacement` 或 InteractionTarget task。
4. Task delegate 输出 Valid/Invalid/Confirmed/Cancelled；Ability 负责流程。
5. 确认时构造 TargetData；服务器重新验证 transform/resource/tag。
6. Commit 后 Server Spawn；Cue；EndAbility。
7. 在 Task OnDestroy/Ability End 清 timer、delegate、preview。
8. 测试 Owner 销毁、目标销毁、外部 Tag cancel、Esc cancel。

## 本周故障注入

- 让 callback 在 Ability 已结束后触发，确认清理阻止悬空执行。
- 篡改客户端 TargetData 为越界位置，服务器拒绝。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/11_AbilityTasksTargetDataAndCancellation.md`
- `Tests/AbilityCancelCleanup`


## 推荐 Commit 切分

```text
week11/01-scaffold-or-model
week11/02-core-path
week11/03-failure-handling
week11/04-tests-and-debug
week11/05-package-or-trace
week11/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L12 — Week 12: Ability Set、Input Tag、授予来源与 Tag Relationship

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 12，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 实现 AbilitySet/AbilityDefinition/GrantComponent/TagRelationshipMapping。
2. Player Definition 配 Build/Interact/Dash Ability Set；Worker Definition 配 Collect/Carry/Deposit。
3. Enhanced Input 映射到 InputTag；ASC 维护 Pressed/Released/held 状态并匹配 Spec。
4. 输入代码删除具体 Ability class 依赖。
5. Grant 时保存 handles/source；Remove 只撤销这一来源授予的 Ability/Effect/AttributeSet。
6. 用 TagRelationship 实现死亡取消 Action、菜单 exclusive 等阻塞关系。
7. 普通 Production 仍留 Component，写一页“为什么不 GAS 化”。
8. Package 验证数据资产和 Ability Set Cook 正确。

## 本周故障注入

- 同一 Ability 由两个来源授予，移除一个来源，验证另一个仍有效。
- 创建循环/冲突 TagRelationship，记录诊断。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/12_DataDrivenAbilityInputAndTags.md`
- `Tests/AbilityGrantRemove`


## 推荐 Commit 切分

```text
week12/01-scaffold-or-model
week12/02-core-path
week12/03-failure-handling
week12/04-tests-and-debug
week12/05-package-or-trace
week12/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L13 — Week 13: GAS Prediction / Replication / Security

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 13，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 选择 Dash 或 Build 设置 Local Predicted，先记录 0ms 行为。
2. 设置 150ms latency、jitter、packet loss，记录输入到本地反馈/服务器确认时序。
3. 区分可预测表现、预测 Attribute/Effect、必须 Server-only 的副作用。
4. 服务器资源滞后：客户端认为够，Server 判不足；清理本地预测。
5. 重复快速输入，确保只 Commit/Spawn 一次。
6. Ability 运行中销毁 Pawn，确认 Task/Cue/preview 清理。
7. 使用 Gameplay Debugger/GAS debug 命令观察 Spec、Tag、Effect。
8. 对照 Lyra Ability Set/ASC/Tag Relationship，写适用与过度设计两列。

## 本周故障注入

- 150ms + 3% loss。
- 故意构造错误客户端资源缓存。
- 重复按键/取消交叉。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/13_GASPredictionReplicationSecurity.md`
- `Docs/13_LyraGASComparison.md`
- `SavedProfiling/Week13_GASNetworkSession.utrace`


## 推荐 Commit 切分

```text
week13/01-scaffold-or-model
week13/02-core-path
week13/03-failure-handling
week13/04-tests-and-debug
week13/05-package-or-trace
week13/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L14 — Week 14: 网络基础：Server + ClientA + ClientB

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 14，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 建立独立网络测试地图和统一启动方式。
2. 在 GameMode/GameState/PC/PS/Pawn/Building 打印 NetMode、Role、Owner、Connection。
3. 网络化 PlayerState resource 与 GameState phase。
4. Building 只由 Server Spawn，客户端通过 Actor replication 出现。
5. Client 交互走 owned PC/Pawn/ASC 的 Server RPC；Server Validate。
6. Server 修改状态后调用 HandleStateChanged；Client OnRep 也调用相同 handler。
7. UI 只读取 replicated/presenter state，不直接发送任意 RPC。
8. 两客户端完整跑一次同一建筑/资源状态。

## 本周故障注入

- 从非 owned Building 发 Server RPC，观察失败。
- 让 Server 本地逻辑只依赖 OnRep，发现 Listen/Dedicated 差异并修复。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/14_NetworkAuthorityOwnershipRPC.md`
- `Tests/NetworkTestChecklist.md`


## 推荐 Commit 切分

```text
week14/01-scaffold-or-model
week14/02-core-path
week14/03-failure-handling
week14/04-tests-and-debug
week14/05-package-or-trace
week14/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L15 — Week 15: Fast Array、Subobject、Dormancy/Relevancy

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 15，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 选择 Inventory 或 Production Queue 改成 Fast Array；定义 item identity。
2. 实现 add/change/remove，正确 MarkItemDirty/MarkArrayDirty。
3. 客户端 PostReplicatedAdd/Change/Remove 只转换成业务/UI 事件。
4. 做一个 Replicated Component/Subobject 最小实验，验证动态创建/销毁。
5. 空闲 Building 进入 Dormancy；状态变化 Flush。
6. 远距离 ResourceNode 降更新频率/相关性；Owner-only 状态设条件复制。
7. 使用 Network Insights 做 baseline。
8. 分别以 50/200/500 item/actor 记录流量趋势。

## 本周故障注入

- 忘记 MarkItemDirty，观察客户端旧数据。
- Dormant 状态修改不 Flush，复现不同步。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/15_FastArraySubobjectDormancyRelevancy.md`
- `SavedProfiling/Week15_NetworkBaseline.utrace`


## 推荐 Commit 切分

```text
week15/01-scaffold-or-model
week15/02-core-path
week15/03-failure-handling
week15/04-tests-and-debug
week15/05-package-or-trace
week15/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L16 — Week 16: 服务器权威核心循环与作弊测试

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 16，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. Client 本地选择/预览 building。
2. 通过 Ability/RPC 发送 Definition ID + transform + request id 等必要意图。
3. Server 重新检查 Definition allowlist、distance、collision/placement、resource、tag/cooldown、ownership/team。
4. Server Commit/Consume/Spawn；Actor + FastArray 同步回 clients。
5. Worker command 服务器校验 ownership/team/target/state。
6. 为重复建造请求实现幂等：同 request id 不重复产生副作用。
7. 每个拒绝路径写结构化 Failure + Server log。
8. 150ms 下完成两客户端建造、采集、生产、Worker 指令。

## 本周故障注入

- 越距采集
- 修改客户端资源显示
- 伪造非己方 Worker
- 快速重复提交
- 非法 Definition ID
- 非法 Transform
- 已销毁目标

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/16_NetworkedGameplaySecurity.md`
- `Tests/ServerAuthorityFunctionalTests`
- `Demo/Week16_TwoClientGameplay.mp4`


## 推荐 Commit 切分

```text
week16/01-scaffold-or-model
week16/02-core-path
week16/03-failure-handling
week16/04-tests-and-debug
week16/05-package-or-trace
week16/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L17 — Week 17: Dedicated Server、Network Insights、Replication Graph

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 17，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 增加 Server Target；构建 Windows Dedicated Server。
2. 写 `BuildServerAndClients.bat` 与 `RunLocalMultiplayer.bat`，启动独立 Server/2 Clients。
3. Dedicated Server 下完整跑核心循环，排除 LocalPlayer/UI 假设。
4. 压力场景生成 200 Resource/50 Worker/100 Building。
5. 抓 Network Insights，排序带宽最高 Actor/property/RPC。
6. 先做低成本修正：频率/属性粒度/dormancy/relevancy。
7. 实现最小 Replication Graph：AlwaysRelevant player state + spatialized world actors。
8. 单独分支读/试 Iris，主分支保持 Generic Replication。

## 本周故障注入

- 禁用一个本地玩家依赖，确认 DS 不崩。
- 关闭 RepGraph 对照 CPU/网络。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/17_DedicatedServerAndNetworkScaling.md`
- `SavedProfiling/Week17_NetworkInsights.utrace`
- `Builds/Week17_ServerAndClients/`


## 推荐 Commit 切分

```text
week17/01-scaffold-or-model
week17/02-core-path
week17/03-failure-handling
week17/04-tests-and-debug
week17/05-package-or-trace
week17/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L18 — Week 18: Worker StateTree/BT、Navigation、Animation

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 18，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 创建 WorkerCharacter、AIController、TaskComponent、BrainComponent、FOutpostTaskData。
2. 先用纯 C++/图画定义任务状态与 transition，不先打开 StateTree。
3. 选择 StateTree 做生产执行器；Context 读取 TaskData/Worker state。
4. Navigation MoveToResource/Storage；处理 path failed。
5. Collect/Deposit 只在 Server task state 改权威资源。
6. Animation Blueprint locomotion + Collect Montage；Notify 只做表现/窗口信号。
7. 目标销毁、仓库满、worker interrupt、priority replacement 全部有 transition。
8. 小型 BT 对照同一任务，写为什么最终选择 StateTree。

## 本周故障注入

- 关闭/替换动画，确认 Gameplay 仍正确。
- 运行中删除资源目标。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/18_WorkerAIStateTreeAndAnimation.md`
- `Tests/WorkerTaskStateTransitions`


## 推荐 Commit 切分

```text
week18/01-scaffold-or-model
week18/02-core-path
week18/03-failure-handling
week18/04-tests-and-debug
week18/05-package-or-trace
week18/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L19 — Week 19: Task Scheduler：Before/After 性能实验

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 19，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 第一版故意让每个 Worker Tick 扫描全部 task。
2. 100 Worker + 固定任务数量抓 Insights baseline。
3. 实现 WorldSubsystem/Scheduler：Task publish event、索引、priority queue、budget。
4. Worker 只获取 assignment，不再全量扫描。
5. 实现 cancel/preempt/target invalid/requeue。
6. AI decision 只在 Server；客户端复制 task type/progress/target id 等表现必要数据。
7. TaskQueue 可选 Fast Array；Save 保存 type/target stable id/phase/params。
8. 加载后重新解析目标，无法解析则进入可恢复失败。

## 本周故障注入

- 随机删除 20% 目标。
- 高优先级任务批量插入。
- 服务器重载存档后继续任务。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/19_TaskSchedulerSaveReplication.md`
- `SavedProfiling/Week19_BeforeScheduler.utrace`
- `SavedProfiling/Week19_AfterScheduler.utrace`


## 推荐 Commit 切分

```text
week19/01-scaffold-or-model
week19/02-core-path
week19/03-failure-handling
week19/04-tests-and-debug
week19/05-package-or-trace
week19/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L20 — Week 20: Unreal Insights、UE::Tasks、批处理与 ISM

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 20，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 固定压力地图、build config、分辨率、actor 数，抓 baseline。
2. 用 stat unit/Insights 判定 Game/Render/GPU bound，不先猜。
3. 找一个纯 CPU 任务评分热点；复制纯数据快照到 UE::Tasks，GameThread apply。
4. 明确禁止后台任务直接改 Actor/UObject；加入 cancellation/lifetime guard。
5. 把低频系统 Tick 改事件/Timer/批处理，记录差异。
6. 选择大量静态表现改 ISM/HISM 对照 draw/CPU。
7. 只在 profile 证明必要时做简单 pool 实验。
8. 输出 before/after 指标表和 utrace。

## 本周故障注入

- 工作线程故意捕获 Actor raw pointer，分析 race/lifetime 风险后删除。
- 把测试条件改掉再比较，说明为什么不能得出结论。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/20_PerformanceProfilingAndTasks.md`
- `SavedProfiling/Week20_Before.utrace`
- `SavedProfiling/Week20_After.utrace`


## 推荐 Commit 切分

```text
week20/01-scaffold-or-model
week20/02-core-path
week20/03-failure-handling
week20/04-tests-and-debug
week20/05-package-or-trace
week20/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L21 — Week 21: 事件驱动 UMG、Presenter/MVVM、CommonUI

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 21，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 拆 OutpostUI runtime module（若边界已稳定）。
2. 给 Resource/Build/Production 页面定义 ViewData 和 UI Intent。
3. Presenter 订阅 Gameplay delegate，把状态转 ViewData；Widget 只渲染。
4. 移除 UI Tick 与复杂 Property Binding；用事件/FieldNotify 或明确刷新。
5. 做一个 MVVM 页面并记录它减少/增加了什么复杂度。
6. 启用 CommonUI：Root layout / activatable stack / HUD / BuildMenu / Pause。
7. 统一键鼠/手柄输入路由、焦点、Back action；页面关闭恢复 Game input。
8. 高频页面创建一次并复用或由 stack 管理，验证重开后 delegate 不重复绑定。

## 本周故障注入

- 连续开关页面 100 次，检查重复回调/焦点丢失。
- 角色 Respawn 后 UI 仍订阅旧对象，复现并修复。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/21_UIArchitectureCommonUI.md`
- `SavedProfiling/Week21_SlateTrace.utrace`


## 推荐 Commit 切分

```text
week21/01-scaffold-or-model
week21/02-core-path
week21/03-failure-handling
week21/04-tests-and-debug
week21/05-package-or-trace
week21/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L22 — Week 22: Outpost Data Inspector 编辑器工具

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 22，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 复用 Week8 Validator core，不在 Slate 里重写规则。
2. 创建 Editor Tab / ToolMenus 入口。
3. 用 AssetRegistry 扫描 Item/Building/Worker/Ability Definition 元数据。
4. 列表支持 error/warning/info、搜索筛选、类型/Tag filter。
5. 选中项显示字段和 validation messages；双击定位/打开 asset。
6. 显示 Primary Asset ID、soft reference 摘要、AbilitySet/Cost 信息。
7. 支持“一键全部验证”与 CSV/JSON 导出。
8. 打包 Runtime，确认不包含 OutpostEditor/Slate editor code。

## 本周故障注入

- 重命名/删除资产后刷新。
- 扫描空项目/坏软引用。
- 1000+ asset 元数据扫描，不允许无脑同步 Load 所有资产。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/22_SlateEditorDataInspector.md`
- `Demo/Week22_EditorTool.mp4`
- `OutpostEditor/DataInspector`


## 推荐 Commit 切分

```text
week22/01-scaffold-or-model
week22/02-core-path
week22/03-failure-handling
week22/04-tests-and-debug
week22/05-package-or-trace
week22/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L23 — Week 23: Automation、Functional Test、RunUAT 与本地 CI

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 23，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 整理低层测试：Inventory、Cost、TagQuery、Clamp、Ability grant/cost、Save roundtrip/migration、Task transition、FastArray logic。
2. 整理 Functional：Build success/fail、out-of-range collect、two clients building、worker collect/deposit、save restore、ability cancel cleanup。
3. 用 UnrealEditor-Cmd 脚本化运行核心 Automation/Functional。
4. Data Validation 接入 pre-build。
5. RunUAT BuildCookRun 构建 Development Client/Server。
6. 所有脚本捕获 exit code，失败即停止；保存 log/report。
7. 在干净 clone/清理目录验证 README 构建步骤。
8. 可选再接 GitHub Actions/Jenkins/TeamCity。

## 本周故障注入

- 故意让一个 test fail，验证 CI/脚本返回失败。
- 删除一个 asset 触发 validation fail。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `Docs/23_TestingBuildAutomation.md`
- `Scripts/RunTests.bat`
- `Scripts/BuildCookRun.bat`
- `TestReports/`


## 推荐 Commit 切分

```text
week23/01-scaffold-or-model
week23/02-core-path
week23/03-failure-handling
week23/04-tests-and-debug
week23/05-package-or-trace
week23/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# L24 — Week 24: 冻结功能、最终验证、作品集与源码复盘

## 开始前

- 打开 `V4_01_Curriculum.md` 的 Week 24，确认 Exit Criteria。
- 阅读 `V4_02_Textbook.md` 对应章节；不理解核心对象关系时先不要写代码。
- `git status` 必须干净，记录当前 commit。

## 主实验步骤

1. 创建 release branch/tag，停止加新系统。
2. 跑全部 tests/validation；修 flaky/known failures。
3. 最终 Package Client/Server；脚本启动 2-client demo。
4. 抓 Final Gameplay/Network/Performance trace，并记录测试条件。
5. 清理 Public API、模块依赖、unused assets/log spam。
6. 完成 Architecture Overview：状态 ownership、input→ability→server→replication→UI、save、AI scheduler。
7. 源码复盘 5 条：UObject creation、Actor lifecycle、Lyra PS/Pawn/ASC、Input→Ability、Replication。
8. 录 2–3 分钟 demo；准备 10–15 分钟技术讲解和 Known Limitations。

## 本周故障注入

- 新机器/干净环境按 README 复现。
- 随机挑一个模块，要求不看代码解释 trade-off 和 failure path。

## 每一步都要观察的证据

- Output Log / dedicated log 中是否出现预期状态。
- 对象名、NetRole、Owner、生命周期或资源 ID 是否与设计一致。
- 对失败路径是否返回明确 Failure/Exit Code，而不是静默失败。
- 需要时保存截图、trace、test report；不要只记录“成功”。

## 必须产出

- `README.md`
- `Docs/24_ArchitectureOverview.md`
- `Docs/24_InterviewTalkingPoints.md`
- `Docs/24_KnownLimitationsAndNextSteps.md`
- `DemoVideo.mp4`
- `Builds/FinalClient/`
- `Builds/FinalServer/`


## 推荐 Commit 切分

```text
week24/01-scaffold-or-model
week24/02-core-path
week24/03-failure-handling
week24/04-tests-and-debug
week24/05-package-or-trace
week24/06-docs-refactor
```

## 离开本 Lab 前的口述检查

不看代码，用 5–10 分钟说明：

1. 本周引入的状态由谁拥有，何时创建/销毁？
2. 哪一条路径是权威修改入口？
3. 最重要的失败路径是什么，如何定位？
4. 为什么当前实现没有选择另一个 UE 系统？
5. 如果对象/玩家/资产数量扩大 10–100 倍，当前瓶颈最可能在哪里？

---

# 附录 — 每周 Retrospective 模板

```markdown
# Week XX Retrospective

## 1. 本周最终可运行链路
用 5–10 行描述输入/数据/状态/输出路径。

## 2. 状态所有权表
| State | Owner | Lifetime | Writer | Replication | Save |
|---|---|---|---|---|---|

## 3. 本周最重要 Bug
- Symptom:
- Reproduction:
- Wrong assumption:
- Diagnostic evidence:
- Fix:
- Regression test:

## 4. Trade-off
为什么用了当前系统；替代方案是什么；规模扩大后是否仍合适。

## 5. Epic / Source Reading
记录实际回答了哪个问题，不写“读了 XX 文档”。

## 6. Next Week Debt
只允许列最多 3 项，并标记必须在何时清零。
```
