#include <iostream>

int g_x = 1;
int g_y = 2;

void externTestPrint(){
    std::cout << "x: " << g_x << " y: " << g_y << std::endl;
}