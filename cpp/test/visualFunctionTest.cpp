#include<iostream>

class A {
public:
    int a;
    virtual void Foo() {
        std::cout << "A::Foo()" << std::endl;
    }
};

class B {
public:
    int b;
    virtual void Bar() {
        std::cout << "B::Bar()" << std::endl;
    }
};

class C : public A, public B {
public:
    int c;

    void Foo() override {
        std::cout << "C::Foo()" << std::endl;
    }
    void Bar() override {
        std::cout << "C::Bar()" << std::endl;
    }
};

int main(){
    // A objA;
    // B objB;
    // C objC;

    // A* pa = &objC;
    // B* pb = &objC;
    // C* pc = &objC;
    
    // std::cout << "pa:" << pa << " pb:" << pb << " pc:" << pc << std::endl;
    // pa->Foo();
    // pb->Bar();
    // pc->Foo();
    // pc->Bar();

    // objA.Foo();

    C objC;
    objC.A::a = 1;
    std::cout << objC.a;
}