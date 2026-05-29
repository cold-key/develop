# Copilot Instructions

## Build and run commands

This repository is a personal graphics/C++ monorepo. There is **no repo-wide build, test, or lint command**; use the commands for the specific subproject you are touching.

### LearnOpenGL (`graphicsAPI\LearnOpenGL\TutorialProjectSln\LearnOpenGLProject`)

Use Visual Studio/MSBuild, not CMake.

```powershell
# Build the configured target
msbuild graphicsAPI\LearnOpenGL\TutorialProjectSln\LearnOpenGLProject\LearnOpenGLProject.sln /t:Build /p:Configuration=Debug /p:Platform=x64

# Clean build outputs
msbuild graphicsAPI\LearnOpenGL\TutorialProjectSln\LearnOpenGLProject\LearnOpenGLProject.sln /t:Clean /p:Configuration=Debug /p:Platform=x64

# Open in Visual Studio
devenv graphicsAPI\LearnOpenGL\TutorialProjectSln\LearnOpenGLProject\LearnOpenGLProject.sln

# Run from the project root so relative shader/texture paths resolve
Set-Location graphicsAPI\LearnOpenGL\TutorialProjectSln\LearnOpenGLProject
.\x64\Debug\LearnOpenGLProject.exe
```

`Debug|x64` is the only configuration with the external OpenGL environment wired in through the `.vcxproj` (`D:\SoftWare\OpenGL\GLEnvironment\include` and `D:\SoftWare\OpenGL\GLEnvironment\lib`, linking `glfw3.lib` and `opengl32.lib`).

There is no automated test or lint setup for this project. Validation is done by building the selected demo and running it from the project root.

### GAMES101 assignments (`games101\homework\...`)

Each assignment is an independent CMake project.

```powershell
Set-Location games101\homework\Assignment1\code
cmake -G "MinGW Makefiles" -S . -B build
cmake --build build
```

There is no unified test target here either; build the specific assignment you changed.

### Python tooling (`tool\sync_res`)

```powershell
python tool\sync_res\svn_sync.py log --start 2026-03-01 --end 2026-03-23 --output logs\changes.json
python tool\sync_res\svn_sync.py sync --input logs\changes.json --dry-run
python tool\sync_res\svn_sync.py sync --input logs\changes.json --sync-delete
```

## High-level architecture

The repository is a collection of mostly independent learning projects rather than a single integrated application. The main code areas are:

- `graphicsAPI\LearnOpenGL`: a Visual Studio OpenGL tutorial project with one executable.
- `games101`: separate CMake-based course assignments.
- `cpp`: standalone C++ exercises and LeetCode solutions.
- `tool`: utility scripts, including SVN resource sync tooling.
- `note`: structured study notes that describe the learning roadmap and related concepts.

Within the LearnOpenGL project, the architecture is:

- `main.cpp` is the manual entry selector. It instantiates exactly one demo class and calls `run()`. Switching demos is done by commenting/uncommenting those lines. The current default is `CameraTest`.
- `src\base` contains shared runtime helpers, not a framework. `BaseComponent` is a namespace with GLFW/GLAD bootstrap code (`initWidget`) and basic ESC handling (`processInput`). `Shader.h` is a header-only shader loader/compiler/linker. `Camera.h` is a header-only camera math/input helper.
- `src\chapterOne` contains standalone demo classes such as `HelloTriangle`, `ShaderTest`, `TextureTest`, `TransformationsTest`, `CoordinatesTest`, and `CameraTest`. Each demo owns its own buffers, textures, render loop, and OpenGL state, while reusing helpers from `src\base`.
- `src\shaderSrc` contains GLSL files loaded at runtime, and `res\img` contains runtime textures. These assets are not copied next to the executable; they are loaded by relative path from the project root.

## Key conventions

- Keep Windows-style paths in commands and documentation.
- For LearnOpenGL work, assume the current working directory at runtime must be `graphicsAPI\LearnOpenGL\TutorialProjectSln\LearnOpenGLProject`; otherwise shader and texture loads like `src\shaderSrc\...` and `res\img\...` will fail.
- Do not assume LearnOpenGL examples share a base class. New demo logic should usually stay inside its own `run()` implementation and reuse `BaseComponent`, `Shader`, `Camera`, and `stb_image` as helpers.
- Most demos load shader source from external `.vs` and `.fs` files through `Shader.h`; `HelloTriangle` is the main exception because it keeps shader source inline.
- Texture-based demos typically call `stbi_set_flip_vertically_on_load(true)` before loading images.
- The LearnOpenGL `.vcxproj` explicitly lists source, header, and shader files. When adding a new demo, shader, or source file, update both `LearnOpenGLProject.vcxproj` and `LearnOpenGLProject.vcxproj.filters`; Visual Studio will not discover them automatically.
- There is no repository-wide CI, test harness, or lint configuration. Prefer the smallest project-specific build/run flow that exercises the code you changed.
- Repository-wide line endings are normalized with `.gitattributes` using `* text=auto`.
