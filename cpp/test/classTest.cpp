#include<iostream>
#include<memory>
#include<string>
#include<vector>

class A {
public:
    A() = delete;
    A(int v, const std::string& n) : value(v), name(n) {}
    int value;
    std::string name;
};

class B {
public:
    A a = {42, "example"};
    std::vector<int> data;
};

int main(){
    B b;
    std::cout  << "B.a.value: " << b.a.value << std::endl;
    std::cout  << "B.a.name: " << b.a.name << std::endl;
}