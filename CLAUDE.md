# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 仓库概述

个人学习 monorepo，围绕计算机图形学、C++ 和游戏开发。学习路线（见 `note/TODAY_PLAN.md`）：LearnOpenGL → (Vulkan) → GAMES101 → 软光栅渲染器 → GAMES104 → UE，同时巩固 C++ 基础。

## 顶层目录

| 目录 | 用途 |
|------|------|
| `book/` | 计算机图形学参考书（Fundamentals of Computer Graphics 中文翻译版、Game Programming Patterns） |
| `cpp/` | C++ 学习笔记代码 + LeetCode 题解（按 easy/medium/hard 分类） |
| `games101/` | GAMES101 课程作业（CMake + C++，依赖 OpenCV + Eigen3） |
| `graphicsAPI/LearnOpenGL/` | LearnOpenGL 教程项目（Visual Studio/MSBuild 构建，GLFW + GLAD + GLM） |
| `note/` | 结构化学习笔记：game（Unity/Shader/热更新等）、learCpp、lua、games101、leetCode |
| `tool/` | 实用工具脚本（SVN 资源同步、图片搜索、资源合并） |

## 构建系统

### Visual Studio / MSBuild — LearnOpenGL 项目

解决方案：`graphicsAPI/LearnOpenGL/TutorialProjectSln/LearnOpenGLProject/LearnOpenGLProject.sln`。单可执行程序，入口在 `main.cpp`，通过手动注释/取消注释切换要运行的示例类。

```powershell
# 构建（Debug|x64 是唯一完整配置了依赖的配置）
msbuild graphicsAPI\LearnOpenGL\TutorialProjectSln\LearnOpenGLProject\LearnOpenGLProject.sln /t:Build /p:Configuration=Debug /p:Platform=x64

# 在 VS 中打开
devenv graphicsAPI\LearnOpenGL\TutorialProjectSln\LearnOpenGLProject\LearnOpenGLProject.sln
```

**关键约束**：程序运行时工作目录必须是 LearnOpenGL 项目根目录（`graphicsAPI/LearnOpenGL/TutorialProjectSln/LearnOpenGLProject/`），shader 和纹理资源通过相对路径加载（`src/shaderSrc/...`、`res/img/...`）。

外部依赖路径（`Debug|x64` 在 `.vcxproj` 中配置）：
- 头文件：`D:\SoftWare\OpenGL\GLEnvironment\include`
- 库：`D:\SoftWare\OpenGL\GLEnvironment\lib`
- 链接：`glfw3.lib`、`opengl32.lib`

新增示例文件时需同步更新 `.vcxproj` 和 `.vcxproj.filters`。

### CMake + MinGW — GAMES101 作业 & C++ 学习

GAMES101 作业在各自目录下有 `CMakeLists.txt`，需要 OpenCV 和 Eigen3。

```powershell
# 以 Assignment1 为例
cd games101\homework\Assignment1\code
mkdir build && cd build
cmake -G "MinGW Makefiles" ..
cmake --build .
```

Eigen3 路径：`C:\Program Files (x86)\Eigen3\include`

### VS Code 单文件编译/调试 — C++ 零散代码

通过 VS Code tasks.json 配置，使用 MinGW-w64 g++（位于 `D:/SoftWare/mingw64/bin/g++.exe`），标准为 C++20。快捷键 `Ctrl+Shift+B` 构建当前文件，输出 `main.exe` 到当前文件所在目录。F5 调试。

## 工具脚本

### SVN 资源同步 (`tool/sync_res/svn_sync.py`)

将 SVN 源目录在指定时间段内的文件变更同步到目标目录。详见 `tool/sync_res/README.md`。

```powershell
# 导出变更日志
python tool/sync_res/svn_sync.py log --start 2026-03-01 --end 2026-03-23 --output logs\changes.json

# 干运行
python tool/sync_res/svn_sync.py sync --input logs\changes.json --dry-run

# 实际同步（含删除）
python tool/sync_res/svn_sync.py sync --input logs\changes.json --sync-delete
```

## 注意事项

- Git 配置了 `text=auto` 行尾规范化（`.gitattributes`）
- `.windsurfrules` 为空文件
- 无测试框架、无 CI/CD、无 lint/format 配置
- 构建验证方式：构建后在 VS 或命令行直接运行观察输出
