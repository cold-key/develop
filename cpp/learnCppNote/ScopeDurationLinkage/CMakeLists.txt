cmake_minimum_required(VERSION 3.10)

# 设置项目名称
project(ScopeDurationLinkage)

# 设置C++标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# 添加源文件
set(SOURCES
    ScopeDurationLinkage.cpp
    ExternTest.cpp
    Constant.cpp
)

# 添加可执行文件
add_executable(ScopeDurationLinkage ${SOURCES})

