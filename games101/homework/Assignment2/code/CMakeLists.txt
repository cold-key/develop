cmake_minimum_required(VERSION 3.10)
project(Rasterizer)

find_package(OpenCV REQUIRED)

set(CMAKE_CXX_STANDARD 17)

# include_directories(/usr/local/include)

# 将路径中的反斜杠替换为双反斜杠或正斜杠
set(EIGEN3_INCLUDE_DIR "C:\\Program Files (x86)\\Eigen3\\include")
# set(EIGEN3_INCLUDE_DIR "C:/Program Files (x86)/Eigen3/include")
message(STATUS "EIGEN3_INCLUDE_DIR: ${EIGEN3_INCLUDE_DIR}")

find_package(Eigen3 REQUIRED)
include_directories(${EIGEN3_INCLUDE_DIR})

add_executable(Rasterizer main.cpp rasterizer.hpp rasterizer.cpp global.hpp Triangle.hpp Triangle.cpp)
target_link_libraries(Rasterizer ${OpenCV_LIBRARIES})

