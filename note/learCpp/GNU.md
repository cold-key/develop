# MSVC、MINGW、gcc、g++、msys、msys2、qmake、cmake的联系和区别是什么？
**参考链接：有没有大佬给我讲解一下MSVC、MINGW，gcc、g++，qmake、cmake的联系和区别是什么？ - 周旋机器视觉的回答 - 知乎https://www.zhihu.com/question/333560253/answer/2282723843**
## 前言
```cpp
#include <stdio.h>
int main()
{
    printf("Hello World");
    return 0;
}
```
要想这段代码在Linux上运行，我们需要使用GCC
1. 预编译：将hello.c和stdio.h预编译为hello.i
2. 编译：将hello.i编译为hello.s
3. 汇编：将hello.s翻译为机器指令hello.o（.o目标文件）链接：
4. 链接各种需要的库和其他目标文件（该hello程序不需要）得到可执行文件hello.out（相当于windows的.exe）

整个过程将高级语言翻译成了机器语言，而编译器，就是这样的一个工具。**GCC可以完成从预编译编译，汇编，链接整个过程**。但是平时使用Visual Studio等软件时并没有接触到这个过程，因为VS是高度集成开发环境（IDE、Integrated Development Environment），集成了代码编辑器，编译器，调试器和图像化用户界面，上述所有程序编译和链接过程都用一步build构建带过了。

## GNU
GNU是指一个由理查德·斯托曼在1983年发起的项目，旨在创造一套完全自由的操作系统。其名称源于递归缩写“GNU’s Not Unix”，旨在强调它不同于Unix操作系统，同时也象征着软件自由的精神。

具体来说，GNU包括了一系列核心软件工具，如文本编辑器Emacs、**C语言编译器GCC（GNU Compiler Collection）**、以及大量遵循GNU通用公共许可证（GPL）的程序库和实用工具。这一系列工具构成了自由软件运动的基础，**其中GCC是最著名的组成部分之一，它不仅用于编译C语言程序，还能处理多种编程语言**。

## MinGW
MinGW是指Minimalist GNU for Windows，它是一个可自由使用和自由发布的Windows特定头文件和使用GNU工具集导入库的集合，允许你在Windows平台上生成本地的Windows程序而不需要第三方C运行时(C Runtime)库。

具体来说，MinGW是一个开发环境，它允许开发者在Windows系统上使用GCC（GNU Compiler Collection）来编译和运行C/C++程序。GCC是一个广泛使用的编译器套件，支持多种编程语言，包括C、C++、Objective-C、Fortran、Ada等。MinGW提供了一个精简的版本，使得GCC能够在Windows上运行，而不需要依赖额外的第三方库，如Microsoft Visual C++运行时库。

MinGW-w64是MinGW的一个扩展版本，它支持64位编译，而不仅仅是32位。这意味着开发者可以使用MinGW-w64来编译适用于现代Windows系统的64位应用程序。

MinGW相比Visual Studio（通常使用的MSVC，Microsoft Visual C++编译器）提供了更多的灵活性和开源特性。它适合于需要跨平台开发、开源软件项目以及对编译器和开发工具没有特定依赖的开发者。对于初学者来说，MinGW可能是一个不错的选择，因为它简单、免费且不需要复杂的配置。然而，对于大型企业级项目或需要特定Windows功能的开发者来说，MSVC可能是更好的选择，因为它提供了更紧密的集成和更全面的Windows API支持。

## MSVC
MSVC编译器是指由微软开发的Visual C++编译器，它是Visual Studio集成开发环境（IDE）中默认集成的C/C++编译器。MSVC编译器主要用于Windows平台上的应用程序开发，支持C++标准，并与Windows SDK紧密集成。它是微软专为Windows平台优化的编译工具，常用于开发Windows桌面应用、Windows服务和Windows API相关的项目。

## MSVC编译器的具体含义和特点
- **开发背景**：MSVC是由微软开发的，专注于Windows平台的C++编译器。
- **集成环境**：它是Visual Studio IDE的一部分，用户通常通过安装Visual Studio来获得MSVC。
- **平台兼容性**：MSVC仅限于Windows平台，不支持跨平台开发。
- **C++标准支持**：MSVC支持C++标准，包括C++11、C++14、C++17和C++20等，但具体支持情况可能因版本而异。
- **功能特性**：MSVC不仅支持C++，还支持C语言，尽管其C语言支持不如GCC和Clang成熟。
- **编译速度和优化**：在某些情况下，MSVC的编译速度和代码优化可能优于GCC和Clang，尤其是在针对Windows平台的优化方面。
- **库支持**：MSVC附带了一套完整的C++标准库和Windows API库，使得开发Windows应用更加便捷。

### 与MinGW的对比
- **MinGW（Minimalist GNU for Windows）**是一个使用GCC编译器的Windows开发环境，它提供了类似于GCC的编译工具链，但不依赖于Windows SDK。
- **跨平台性**：MinGW支持跨平台开发，可以编译出可在Windows、Linux和macOS上运行的代码，而MSVC则主要针对Windows。
- **库兼容性**：MinGW可以使用GNU工具链生成的库，而MSVC生成的库通常无法直接与GNU工具链兼容。

### 与其他编译器的对比
- **GCC（GNU Compiler Collection）**是一个开源的编译器集合，支持多种语言，包括C、C++、Fortran等，广泛用于Linux和macOS开发。
- **Clang**是另一个开源的C/C++编译器，由LLVM项目提供，以高效的编译速度和优秀的错误诊断能力著称。
- **G++**是GCC的C++编译器前端，专门用于C++语言的编译。

### 总结
MSVC编译器是微软为Windows平台开发的C/C++编译器，它与Visual Studio紧密集成，提供了一套完整的开发工具链。虽然它在Windows平台上具有优势，但不支持跨平台开发。在选择编译器时，开发者需要根据项目的具体需求来决定使用MSVC还是其他编译器。


## Cygwin、MSYS、MSYS2

Cygwin是指一个可原生运行于Windows系统上的POSIX兼容环境，它提供了一个大型的GNU和开源工具集合，使Windows用户能够使用类似Linux的功能和体验。具体来说，Cygwin包括：

- 一个动态链接库（DLL，cygwin1.dll），作为POSIX API的兼容层，用于将部分POSIX调用转换成Windows系统调用。
- 一系列软件工具和应用程序，提供类似于Unix的外观和操作感。

Cygwin并非一个支持运行原生Linux应用的工具，也不使Windows应用感知Unix功能，而是通过其兼容层和工具集合，让用户在Windows上运行许多原本只能在Unix或Linux系统上运行的软件。例如，用户可以在Cygwin中使用bash、gcc、less等工具，进行软件开发和系统管理。

**Cygwin的核心目的是让Windows用户在不安装Linux系统的情况下，运行大量基于POSIX标准的开源工具，如bash、grep、sed、gcc等**。它的实现逻辑和实际应用可以从以下几个层面展开：

---

### 1. **核心机制：POSIX兼容层**
   - **动态链接库（cygwin1.dll）**：这是Cygwin的“心脏”。当你在Cygwin中运行一个Linux工具时，该工具会调用POSIX API（例如文件操作`open()`、进程管理`fork()`），而Cygwin的DLL会将这些调用实时翻译为Windows系统能理解的API（例如`CreateFile()`或`CreateProcess()`）。
   - **文件路径转换**：Linux使用`/home/user`格式，而Windows用`C:\Users\user`。Cygwin会自动将路径转换为Windows格式，例如将`/home`映射到`C:\cygwin64\home`。
   - **进程和权限模拟**：Windows没有原生的fork()函数，Cygwin通过复杂的内存复制和进程管理来模拟这一行为；类似地，Linux的权限系统（如`chmod 755`）也会被映射到Windows的ACL（访问控制列表）。

---

### 2. **Cygwin vs MSYS/MSYS2**
   - **MSYS（Minimal SYStem）**：最初为MinGW（Windows版GCC工具链）设计的极简环境。它删除了Cygwin中与开发无关的工具，仅保留编译工具链所需的最小POSIX支持。
   - **MSYS2**：可以视为“现代版Cygwin”，特点包括：
     - 使用Arch Linux的包管理器`pacman`，支持超过3000个预编译软件包（如Python、Node.js）。
     - 默认支持64位程序，且能与Windows原生程序混合调用（例如在MSYS2终端中直接运行`cmd.exe`）。
     - 更活跃的社区维护，许多开源项目（如FFmpeg、OpenSSL）已原生适配MSYS2环境。

---

### 3. **Cygwin的典型使用场景**
   - **跨平台开发**：例如在Windows上编译Linux兼容的C/C++代码，但需注意某些底层API（如信号处理）可能与原生Linux存在差异。
   - **脚本和自动化**：用Bash脚本替代Windows批处理（.bat），利用`awk`、`sed`等工具处理文本。
   - **替代缺失的Windows工具**：例如用`rsync`同步文件、`ssh`连接服务器、`curl`测试API。
   - **学习Linux命令**：对新手友好，无需安装虚拟机即可练习Linux命令。

---

### 4. **局限性**
   - **性能损失**：POSIX API的翻译层可能导致程序运行速度比原生Linux慢10-20%（例如多线程程序）。
   - **兼容性问题**：依赖Linux内核特性的工具无法运行（例如Docker、systemd）。
   - **路径混淆**：Cygwin路径（如`/cygdrive/c/Users`）与Windows路径（`C:\Users`）需要手动处理，混用时易出错。

---

### 5. **与WSL的对比**
   - **WSL（Windows Subsystem for Linux）**：直接运行Linux内核二进制文件，几乎无兼容性问题，性能接近原生Linux。
   - **Cygwin的优势**：
     - 无需启用Hyper-V虚拟机（对老旧硬件或某些企业环境更友好）。
     - 与Windows原生程序交互更方便（例如在Cygwin中直接调用`notepad.exe`）。
     - 适合轻量级需求（例如仅需几个命令行工具）。

---

### 6. **实际案例**
   - **场景1**：开发者需在Windows上编译一个依赖`autotools`（如`./configure && make`）的开源项目。使用Cygwin安装`gcc`、`make`、`automake`后，可直接运行Linux风格的编译脚本。
   - **场景2**：系统管理员编写一个Bash脚本，用于批量重命名文件（借助`find`和`xargs`），然后在Cygwin中运行。
   - **陷阱案例**：在Cygwin中编译的程序如果依赖`cygwin1.dll`，分发到其他Windows机器时需携带此DLL，否则无法运行。

---

如果需要进一步实践，可尝试安装Cygwin或MSYS2后，运行以下命令体验：
```bash
# 查看Cygwin的Linux风格系统信息
uname -a
# 使用Linux工具处理Windows文件
grep "error" /cygdrive/c/Logs/system.log
```

## CMake