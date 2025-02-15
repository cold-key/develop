#pragma once
namespace Constants
{
    constexpr int x = 1;
    inline constexpr int y = 2;
    extern int z;
    extern int value; // 将定义改为声明

    // int error = 5; // 在头文件中定义变量时，如果不使用extern关键字，则会导致多次定义错误
}