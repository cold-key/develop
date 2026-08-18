#include <iostream>
#include <string>
#include <vector>

class Base{

public:
    Base() {
        std::cout << "Base constructor" << std::endl;
        name = "Base";
    }
    virtual ~Base() { std::cout << "Base destructor" << std::endl; }
public:
    std::string name;
};

class Derived : public Base{
public:
    Derived() {
        std::cout << "Derived constructor" << std::endl;
        data = {1, 2, 3, 4, 5};
    }
    ~Derived() { std::cout << "Derived destructor" << std::endl; }
public:
    std::vector<int> data;
};

int main() {
    Base* obj = new Derived();
    std::string* name = &obj->name;
    std::vector<int>* data = nullptr;
    if (Derived* derivedObj = dynamic_cast<Derived*>(obj)) {
        data = &derivedObj->data;
    }
    delete obj; // This will call the destructor of Derived followed by Base
    return 0;
}