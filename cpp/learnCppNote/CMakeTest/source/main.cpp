#include <iostream>
#include <cmath>
#include "CMakeTestConfig.h"

#ifdef USE_MYMATH
    #include "MathFunctions.h"
#endif


int main() {

    std::cout << "Version" << VERSION_MAJOR << std::endl;
    double x = 2;
    
    #ifdef USE_MYMATH
        std::cout << "myMath" << std::endl;
        std::cout << "mysqrt(" << x << ") = " << MathFunctions::mysqrt(x) << std::endl;
    #else
        std::cout << "cmath" << std::endl;
        std::cout << "mysqrt(" << x << ") = " << sqrt(x) << std::endl;
    #endif

    return 0;
}