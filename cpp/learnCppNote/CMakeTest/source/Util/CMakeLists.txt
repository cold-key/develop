add_library(Util mysqrt.cpp)

target_include_directories(Util
          INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}
          )