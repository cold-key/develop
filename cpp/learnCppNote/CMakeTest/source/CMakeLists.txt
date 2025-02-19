cmake_minimum_required(VERSION 3.10)

project(CMakeTest)

# 如果不设置C++标准，会不会有问题 ,(不会)
set(CMAKE_CXX_STANDARD 17)

add_executable(CMakeTest main.cpp)