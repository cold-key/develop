# CMake

## Windows下

### 项目构建和生成
```
cmake -G "MinGW Makefiles" ..\source\
```
这条命令主要用于项目生成，其中 -G 表示指定生成器（Generator），“..\source\”是项目的源文件（source 文件夹）路径。CMake 会根据此路径中的 CMakeLists.txt 文件来生成项目的构建文件，（在当前目录生成）。

```
cmake --build .
```
这条命令会调用之前生成的构建文件（如 Makefile），并使用相应的构建工具（如 make）来编译和构建项目。这一步在生成构建文件后执行，用于实际构建项目。

### CMake语法

[参考教程](https://zhuanlan.zhihu.com/p/500002865)