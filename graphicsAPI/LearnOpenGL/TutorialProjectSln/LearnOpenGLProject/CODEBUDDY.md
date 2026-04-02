# CODEBUDDY.md This file provides guidance to CodeBuddy when working with code in this repository.

## 常用命令

- `devenv LearnOpenGLProject.sln`
  在 Visual Studio 2022 中打开解决方案。这个仓库是单可执行程序工程，最常见的开发方式是直接在 VS 中切换当前示例、调试 OpenGL 上下文，并同步维护 `.vcxproj` 与 `.vcxproj.filters`。

- `msbuild LearnOpenGLProject.sln /t:Build /p:Configuration=Debug /p:Platform=x64`
  推荐的命令行构建方式。优先使用 `Debug|x64`：该配置在项目文件中显式配置了外部 OpenGL 环境的头文件/库目录，并链接 `glfw3.lib` 与 `opengl32.lib`。其他配置没有同等完整的依赖设置。

- `msbuild LearnOpenGLProject.sln /t:Clean /p:Configuration=Debug /p:Platform=x64`
  清理 `Debug|x64` 输出。适合在修改项目文件、着色器路径或外部库设置后排查旧产物导致的构建/运行问题。

- `.\x64\Debug\LearnOpenGLProject.exe`
  从项目根目录运行已构建程序。必须保持当前工作目录为仓库根目录，否则 `src/shaderSrc/...` 的 shader 文件和 `res/img/...` 的纹理资源会因相对路径失效而加载失败。

- `N/A（未配置）`
  仓库没有自动化测试框架，因此不存在“运行全部测试”或“运行单个测试”的命令。当前验证方式是切换 `main.cpp` 中实例化的示例类，重新构建后直接运行观察窗口输出与控制台日志。

- `N/A（未配置）`
  仓库没有独立的 lint/format 命令，也没有 `.clang-tidy`、`.clang-format` 或测试工程。当前最接近静态检查的方式就是执行一次 `Debug|x64` 构建，依赖 MSVC 的 `WarningLevel=Level3`、`SDLCheck=true` 和 `ConformanceMode=true`。

## 高层架构

这是一个面向 LearnOpenGL 教程的单解决方案、单可执行程序仓库。`LearnOpenGLProject.sln` 只包含一个 `LearnOpenGLProject.vcxproj`；入口在 `main.cpp`，通过手动注释/取消注释来选择当前要运行的示例类，然后调用其 `run()`。当前默认入口是 `TextureTest`。

代码按“共享基础设施 + 教程示例 + 运行时资源”组织：

- `src/base/` 放共享基础代码。`BaseComponent` 不是可继承基类，而是一个命名空间工具层：`initWidget()` 负责初始化 GLFW、创建 `800x600` 窗口、加载 GLAD、设置 viewport 和 framebuffer callback；`processInput()` 只处理 ESC 退出。`Shader.h` 是 header-only 的 shader 封装，负责从磁盘读取顶点/片段 shader、编译链接 program，并提供少量 uniform 设置函数。`stb_image.h` 用于纹理加载。
- `src/chapterOne/` 放教程示例类。每个示例都是一个独立类，通常只暴露 `run()`，自己管理 VAO/VBO/EBO、纹理、shader 和渲染循环；它们不继承统一基类，只是复用 `BaseComponent` 和 `Shader`。
- `src/shaderSrc/` 放运行时加载的 GLSL 文件，按示例成对存在。shader 不会被嵌入二进制，而是在运行时通过相对路径读取。
- `res/` 放运行时资源；当前主要是 `res/img/container.jpg` 和 `res/img/awesomeface.png` 两张纹理图。

示例之间体现了从基础绘制到更复杂渲染的递进关系：

- `HelloTriangle` 是最原始的 OpenGL 练习，shader 源码直接写在 `.cpp` 中，不依赖外部 shader 文件，也不使用纹理资源。
- `ShaderTest` 引入 `Shader` 封装和 `src/shaderSrc/shaderTest.vs/.fs`，演示把 GLSL 挪到外部文件，并在渲染循环里通过 uniform 驱动颜色和位置变化。
- `TextureTest` 在 `ShaderTest` 基础上增加 `stb_image` 和两张纹理，使用 `texture_test_shader.vs/.fs` 混合两张图片，并通过 `scale` uniform 控制采样效果。它是当前 `main.cpp` 默认运行的示例，也是理解资源路径约束时最重要的样例。
- `TransformationsTest` 继续沿用纹理管线，并引入 GLM 进行矩阵计算，目标是做变换示例；但当前代码还没有把 `transform` 矩阵真正上传到 shader，且 `main.cpp` 也没有切换到它，所以它更像是进行中的实验示例。

这个仓库的关键运行约束是“工作目录必须是项目根目录”。示例代码直接以相对路径读取 `src/shaderSrc/...` 和 `res/img/...`，没有资源复制步骤，也没有把 shader 打包进输出目录。因此，无论在 VS 里调试还是命令行直接运行，都要确保进程从仓库根目录启动。

构建体系完全依赖 Visual Studio/MSBuild，而不是 CMake。`LearnOpenGLProject.vcxproj` 明确列出了所有 `.cpp`、`.h` 和 shader 文件；仓库不会自动发现新文件。因此新增示例时，除了添加源码和 shader 文件本身，还需要同步更新 `LearnOpenGLProject.vcxproj` 与 `LearnOpenGLProject.vcxproj.filters`，否则 VS 里不会正确编译或显示这些文件。

依赖方面，仓库并非完全自包含。`glad.c` 被直接纳入工程，但 `glad/glad.h`、GLFW 头文件/库以及 GLM 头文件来自本机外部环境。项目文件里 `Debug|x64` 显式指向 `D:\SoftWare\OpenGL\GLEnvironment\include` 和 `D:\SoftWare\OpenGL\GLEnvironment\lib`，并链接 `glfw3.lib`、`opengl32.lib`。因此后续改动应优先假设 `Debug|x64` 是主开发目标；如果需要改依赖路径或新增库，应先检查 `.vcxproj` 中这一配置。

仓库没有测试目录、测试框架或专门的 lint 配置。当前“验证改动”的方式主要是：选择一个示例、构建、运行，然后观察窗口渲染结果、控制台输出和 MSVC 编译告警。