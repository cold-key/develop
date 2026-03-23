# SVN 资源同步工具（svn_sync.py）

本工具用于将**国内 SVN 工程指定时间段内的文件变更**同步到**海外工程**（两个目录结构需保持一致）。

## 环境前提

1. 本机已安装并可在命令行执行 `svn`。
2. `svn_sync.py` 中的默认源目录 `DEFAULT_SOURCE_PATH` 需指向国内工程（SVN working copy 或本地可访问路径）。
3. `sync` 时会把源目录当前工作区内容拷贝到目标目录，因此源目录需要包含区间末端对应的最终文件状态。

## 命令使用

### 1) 生成变更日志（JSON）

默认输出目录：`./logs/`

```powershell
python svn_sync.py log --start 2026-03-01 --end 2026-03-23 --output logs\changes_2026_03.json
```

如果你仍想指定不同输出文件名/目录，也可以继续使用 `--output`。

输出 JSON 结构为“按文件组织”的聚合结果：
- `summary`
- `added` / `modified` / `deleted`
- 每个文件的 `history`（revision/date/author/action/message）

### 2) 执行同步（拷贝新增/修改；可选删除）

干运行（只打印将执行的操作，不实际写文件）：

```powershell
python svn_sync.py sync --input logs\changes_2026_03.json --dry-run
```

默认行为：**不拷贝新增的 `.csd` 文件**（仅拷贝新增/修改的非 `.csd` 文件）。如果你确实需要拷贝“新增的 `.csd`”，请加：

```powershell
python svn_sync.py sync --input logs\changes_2026_03.json --dry-run --copy-added-csd
```

实际执行（默认不删除）：

```powershell
python svn_sync.py sync --input logs\changes_2026_03.json
```

包含删除操作（需要 `--sync-delete`）：

```powershell
python svn_sync.py sync --input logs\changes_2026_03.json --sync-delete
```

## 默认目标目录

`sync` 的默认目标目录在代码中配置为：
`D:\dbSpace\dragon_ball_abroad_trunk\cocos_studio`

如需临时覆盖目标目录，可继续使用 `--target` 参数。

