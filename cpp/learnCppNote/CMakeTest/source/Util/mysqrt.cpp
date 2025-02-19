#include "MathFunctions.h"
namespace MathFunctions
{
    double mysqrt(double x){
        if (x <= 0)
        {
            return 0;
        }
        double result = x;
        double delta = 0;
        while (true)
        {
            delta = (result * result - x) / (2 * result);
            result -= delta;
            if (delta < 0.0001 && delta > -0.0001)
            {
                break;
            }
        }
        return result;
    }
}

