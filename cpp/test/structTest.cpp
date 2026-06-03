#include<iostream>

struct TestStruct {
    char b;
    char c;
    int a;
};

class TestClass {
public:
    int x;
    double y;
    char z;

    int getX() const {
        return x;
    }
};

int main() {
    int structSize = sizeof(TestStruct);
    int classSize = sizeof(TestClass);
    std::cout << "Size of TestStruct: " << structSize << " bytes" << std::endl;
    std::cout << "Size of TestClass: " << classSize << " bytes" << std::endl;
    return 0;
}