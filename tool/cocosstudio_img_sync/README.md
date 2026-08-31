# CocosStudio 图片增量同步工具

这个工具用于把 CocosStudio 工程中发生变化的资源，同步到游戏实际工程的 `res` 目录。

默认配置：

- 源目录：`D:\a2\assets\branches\dragon_ball_hero\cocos_studio\cocosstudio`
- 目标目录：`D:\a2\client\dragon_ball_hero\res`
- 同步目录：`bg`、`sprite`

目标目录使用与源目录相同的相对路径。例如：

```text
cocosstudio\bg\login_bg.jpg   ->   res\bg\login_bg.jpg
cocosstudio\sprite\hero\a.png ->   res\sprite\hero\a.png
```

## 使用方式

### 按 SVN 提交号同步

`revision` 模式使用 SVN 提交号筛选变更路径，文件内容取源 working copy 当前状态：

```bat
python cocosstudio_img_sync.py revision --revision 83672 --dry-run
python cocosstudio_img_sync.py revision --revision 83672
```

该模式执行的 SVN 查询相当于：

```bat
svn diff --summarize --xml -c 83672 <source>\bg <source>\sprite
```

### 按本地 working copy 变更同步

`local` 模式读取 SVN working copy 状态，处理已修改、已新增、已删除、缺失以及未版本控制文件。
因此刚生成但尚未执行 `svn add` 的图片也会被识别为新增文件：

```bat
python cocosstudio_img_sync.py local --dry-run
python cocosstudio_img_sync.py local
```

目标中未出现在本次变更列表里的文件不会被删除。源端明确为删除的文件会直接删除目标对应文件，实际运行前建议先使用 `--dry-run`。

## 参数

两个模式都支持：

```text
--source PATH       覆盖源 cocosstudio 根目录
--target PATH       覆盖目标 res 根目录
--sync-dir NAME     覆盖同步目录，可重复传入
--log-dir PATH      覆盖日志目录
--dry-run           只显示和记录操作，不修改目标
```

例如只同步另一个目录：

```bat
python cocosstudio_img_sync.py local --sync-dir bg --sync-dir sprite --dry-run
```

后续增加默认同步目录时，修改脚本顶部的 `SYNC_DIRS` 配置即可。

每次运行会在 `logs\` 下生成日志，记录检测到的 SVN 状态、复制、删除、跳过和错误信息。工具不会执行 SVN update、commit、revert，也不会修改源 working copy。

## 测试

```bat
python test_cocosstudio_img_sync.py -v
```
