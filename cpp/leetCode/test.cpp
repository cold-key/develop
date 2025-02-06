#include <iostream>

// 前向声明
class MyClass;

// 使用前向声明的类
void foo(MyClass* obj); // 合法，因为只需要知道MyClass的存在

// 定义MyClass
class MyClass {
public:
    void bar() {
        std::cout << "hi";
    }
};

// 使用MyClass
void foo(MyClass* obj) {
    obj->bar(); // 合法，因为MyClass已经定义
}

int main()
{
    MyClass m = MyClass();
    int a {0};
    foo(&m);
    return 0;
}