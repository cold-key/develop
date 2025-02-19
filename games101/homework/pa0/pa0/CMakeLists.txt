cmake_minimum_required (VERSION 2.8.11)
project (Transformation)

# 将路径中的反斜杠替换为双反斜杠或正斜杠
set(EIGEN3_INCLUDE_DIR "C:\\Program Files (x86)\\Eigen3\\include")
# set(EIGEN3_INCLUDE_DIR "C:/Program Files (x86)/Eigen3/include")
message(STATUS "EIGEN3_INCLUDE_DIR: ${EIGEN3_INCLUDE_DIR}")

find_package(Eigen3 REQUIRED)
include_directories(${EIGEN3_INCLUDE_DIR})

add_executable (Transformation main.cpp)
