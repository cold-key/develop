cmake_minimum_required(VERSION 3.10)

project(CMakeTest)

# 如果不设置C++标准，会不会有问题
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_C_COMPILE C:\msys64\mingw64\bin\gcc.exe)
set(CMAKE_CXX_COMPILE C:\msys64\mingw64\bin\g++.exe)

add_executable(CMakeTest main.cpp)