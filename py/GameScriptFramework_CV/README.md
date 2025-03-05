# 游戏自动化视觉框架 (Game Automation Vision Framework)

这是一个基于计算机视觉的游戏自动化框架，专注于游戏信息的提取和智能模拟输入。框架提供了一系列强大的工具，用于分析游戏画面、识别游戏元素，并模拟人类般的输入行为。

## 主要特性

### 1. 游戏画面分析 (GameAnalyzer)
- **文字识别**
  - 支持中英文识别
  - 多种预处理方法
  - 返回文字位置和置信度
  
- **对象检测**
  - 基于模板匹配
  - 支持多目标检测
  - 返回位置和匹配度
  
- **运动检测**
  - 基于帧差法
  - 可配置最小检测面积
  - 返回运动物体的位置和大小
  
- **颜色分析**
  - 主要颜色提取
  - 目标颜色占比计算
  - 支持颜色容差设置

### 2. 智能输入控制 (InputController)
- **人类行为模拟**
  - 贝塞尔曲线鼠标轨迹
  - 可配置的随机时间扰动
  - 支持组合键和连续操作
  
- **反外挂机制**
  - 随机延迟
  - 自然的操作轨迹
  - 可扩展的钩子系统

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 基础用法示例

```python
from core.game_analyzer import GameAnalyzer
from core.input_controller import InputController

# 创建分析器和控制器
analyzer = GameAnalyzer()
controller = InputController()

# 提取文字信息
texts = analyzer.extract_text()
# 返回格式：
# [
#     {
#         'text': '开始游戏',
#         'confidence': 98.5,
#         'box': (100, 200, 80, 30)  # x, y, 宽, 高
#     }
# ]

# 检测游戏对象
objects = analyzer.detect_objects('templates/character.png')
# 返回格式：
# [
#     {
#         'position': (150, 300),  # 中心位置
#         'confidence': 0.92,      # 匹配度
#         'box': (130, 280, 40, 40)  # 边界框
#     }
# ]

# 模拟人类输入
controller.move_to((500, 300), human_like=True)
controller.click((500, 300), human_like=True)
controller.key_press(['ctrl', 'c'], human_like=True)
```

### 3. 高级功能示例

```python
# 1. 检测运动物体
motion = analyzer.detect_motion(min_area=1000)
# 返回格式：
# [
#     {
#         'center': (200, 300),    # 运动物体中心
#         'box': (180, 280, 40, 40),  # 边界框
#         'area': 1600            # 运动区域面积
#     }
# ]

# 2. 分析颜色分布
colors = analyzer.analyze_color_distribution(
    target_color=(255, 0, 0),  # BGR格式
    tolerance=20
)
# 返回格式：
# {
#     'dominant_colors': [[255, 0, 0], [0, 255, 0]],
#     'color_ratio': 0.3  # 目标颜色占比
# }

# 3. 自定义输入行为
def my_pre_input():
    time.sleep(random.uniform(0.1, 0.3))

controller.add_pre_input_hook(my_pre_input)
```

## 项目结构

```
GameScriptFramework_CV/
├── core/                    # 核心功能模块
│   ├── game_analyzer.py    # 游戏画面分析器
│   └── input_controller.py # 输入控制器
├── utils/                  # 工具类
│   ├── logger.py          # 日志工具
│   └── config.py          # 配置管理
├── examples/              # 示例脚本
│   ├── simple_game_bot.py
│   └── advanced_game_bot.py
├── templates/             # 模板图片目录
├── tests/                # 单元测试
├── requirements.txt      # 项目依赖
└── README.md            # 项目说明
```

## 应用场景

1. **回合制游戏**
   - 使用文字识别读取游戏信息
   - 通过模板匹配识别按钮
   - 模拟点击操作

2. **动作游戏**
   - 使用运动检测跟踪目标
   - 分析颜色识别血量/能量
   - 模拟连续按键操作

3. **卡牌游戏**
   - 使用图像匹配识别卡牌
   - 分析颜色区分卡牌类型
   - 模拟拖拽操作

## 性能优化

1. **图像处理**
   - 帧缓存机制
   - 区域检测
   - 多种预处理方法

2. **输入控制**
   - 可配置的时间范围
   - 自然的移动轨迹
   - 智能的延迟策略

## 注意事项

1. 使用前请确保已安装所有依赖包
2. 建议在游戏窗口化模式下使用
3. 根据游戏特点选择合适的分析方法
4. 适当调整时间参数避免触发反外挂
5. 定期检查和更新模板图片

## 未来计划

- [ ] 添加深度学习模型支持
- [ ] 优化文字识别准确率
- [ ] 添加更多反外挂策略
- [ ] 开发配置界面
- [ ] 支持更多输入设备

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进框架。在提交代码前，请确保：

1. 代码符合PEP 8规范
2. 添加适当的注释和文档
3. 包含必要的测试用例
4. 更新相关文档
