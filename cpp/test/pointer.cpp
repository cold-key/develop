#include<iostream>

int main() {
    int var = 1234;
    int* p = reinterpret_cast<int*>(&var);
    std::cout << "*p:" << *p << std::endl;
    double* q = reinterpret_cast<double*>(&var);  
    std::cout << "*q:" << *q << std::endl;
    void* r = reinterpret_cast<void*>(&var);
    // std::cout << "*r:" << *r << std::endl;
    return 0;
}