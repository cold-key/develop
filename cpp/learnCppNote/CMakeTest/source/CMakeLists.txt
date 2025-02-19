cmake_minimum_required(VERSION 3.10)

project(CMakeTest VERSION 1.0.0)

# 如果不设置C++标准，会不会有问题 ,(不会)
set(CMAKE_CXX_STANDARD 17)

option(USE_MYMATH "Use tutorial provided math implementation" OFF)

message(STATUS "USE_MYMATH: ${USE_MYMATH}")

configure_file(CMakeTestConfig.h.in CMakeTestConfig.h)

set(SOURCES
    main.cpp
)

if(USE_MYMATH)
    add_subdirectory(Util)
    list(APPEND EXTRA_LIBS Util)
endif()

add_executable(${PROJECT_NAME} ${SOURCES})

target_link_libraries(CMakeTest PUBLIC ${EXTRA_LIBS})

target_include_directories(${PROJECT_NAME} PUBLIC
                           ${PROJECT_BINARY_DIR}
                           )