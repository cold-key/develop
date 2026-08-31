# page_hero 图片同步工具

修改 `img\page_hero` 后，在当前目录执行：

```bat
python img_sync.py
```

脚本会显示菜单：

- 全量同步：目标目录严格跟随源目录，目标中多余文件会在确认后删除。
- 增量同步：只新增源目录文件或覆盖内容已变化的同名文件，不删除目标独有文件。

也可以直接指定模式：

```bat
python img_sync.py --mode incremental
python img_sync.py --mode full
python img_sync.py --mode full --yes
```

`--yes` 仅用于全量同步，表示跳过删除确认。每次执行的日志会写入脚本旁的 `logs\` 目录，文件名包含执行时间，并按目标目录记录 `ADD`、`MODIFIED`、`DELETE` 和错误项。

需要修改路径时，直接编辑 `img_sync.py` 顶部的 `SOURCE_DIR`、`TARGET_DIRS` 和 `LOG_DIR` 配置。

## 测试

```bat
python test_img_sync.py -v
```
