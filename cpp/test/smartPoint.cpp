#ifdef _MSC_VER
// 使用 Visual Studio 编译时，在程序退出时自动输出 CRT 内存泄漏报告。
#define _CRTDBG_MAP_ALLOC
#include <cstdlib>
#include <crtdbg.h>
#endif

#include <iostream>
#include <memory>
#include <string>
#include <utility>

class Resource {
public:
    explicit Resource(std::string name) : name_(std::move(name)) {
        std::cout << "create: " << name_ << '\n';
    }

    ~Resource() {
        std::cout << "destroy: " << name_ << '\n';
    }

private:
    std::string name_;
};

void testUniquePtr() {
    std::cout << "\n[unique_ptr]\n";
    {
        auto resource = std::make_unique<Resource>("unique resource");
        std::cout << "resource is owned by unique_ptr\n";
    } // 离开作用域，Resource 的析构函数会自动执行
}

void testSharedPtr() {
    std::cout << "\n[shared_ptr]\n";
    auto first = std::make_shared<Resource>("shared resource");
    std::cout << "count = " << first.use_count() << '\n';

    {
        auto second = first;
        std::cout << "count = " << first.use_count() << '\n';
    } // second 释放，引用计数回到 1

    std::cout << "count = " << first.use_count() << '\n';
} // first 释放，Resource 的析构函数会执行

struct Node {
    explicit Node(std::string name) : name(std::move(name)) {
        std::cout << "create node: " << this->name << '\n';
    }

    ~Node() {
        std::cout << "destroy node: " << name << '\n';
    }

    std::string name;
    std::shared_ptr<Node> child;
    std::weak_ptr<Node> parent; // weak_ptr 不增加引用计数，不参与所有权
};

void testWeakPtr() {
    std::cout << "\n[weak_ptr: break the cycle]\n";
    {
        auto parent = std::make_shared<Node>("parent");
        auto child = std::make_shared<Node>("child");

        parent->child = child;
        child->parent = parent; // 如果这里使用 shared_ptr，就会形成循环引用

        if (auto owner = child->parent.lock()) {
            std::cout << "child's parent is alive: " << owner->name << '\n';
        }
    }
    // parent 和 child 都应该打印 destroy node
}

#ifdef DEMO_SHARED_CYCLE
void testSharedPtrCycle() {
    std::cout << "\n[shared_ptr: intentional cycle]\n";
    auto left = std::make_shared<Node>("left");
    auto right = std::make_shared<Node>("right");

    left->child = right;
    right->child = left; // 两个对象互相持有，引用计数永远不会变成 0

    std::cout << "left count = " << left.use_count() << '\n';
    std::cout << "right count = " << right.use_count() << '\n';
} // 不会打印 left/right 的析构信息
#endif

#ifdef DEMO_RAW_LEAK
void testRawPointerLeak() {
    std::cout << "\n[raw pointer: intentional leak]\n";
    auto* leaked = new Resource("raw leaked resource");
    (void)leaked; // 故意不 delete
}
#endif

int main() {
#ifdef _MSC_VER
    int flags = _CrtSetDbgFlag(_CRTDBG_REPORT_FLAG);
    _CrtSetDbgFlag(flags | _CRTDBG_ALLOC_MEM_DF | _CRTDBG_LEAK_CHECK_DF);
#endif

    testUniquePtr();
    testSharedPtr();
    testWeakPtr();

#ifdef DEMO_SHARED_CYCLE
    testSharedPtrCycle();
#endif

#ifdef DEMO_RAW_LEAK
    testRawPointerLeak();
#endif

    return 0;
}
