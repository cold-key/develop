#include "Constant.h"
#include <iostream>

namespace Constants
{
    int z {1};
    int value = 5; // 在源文件中定义
    // 由于编译器单独编译每个源文件，因此它只能看到出现在正在编译的源文件中的变量定义（包括任何包含的头文件）。
    // 例如，当编译器编译main.cpp时，constants.cpp中的变量定义不可见。因此，constexpr变量不能分为头文件和源文件，它们必须在头文件中定义。
}

void constantPrint(){
    std::cout<< "constantPrint ------------------ " <<'\n';
}