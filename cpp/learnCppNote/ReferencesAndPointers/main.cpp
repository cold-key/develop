#include <iostream>

#define isSmall(T) (sizeof(T) <= 2 * sizeof(void*))

struct Point {
    int x;
    int y;
    int z;
};

void scalePoint(Point& p, double factor);
void addOne(int& i);
void printPoint(const Point& p);
void foo(int*& p);
void twoLevelPointer(int** pp);

int main(){
    // int i = 42;
    // int& ri = i;
    // i = 13;
    // std::cout << "i = " << i << " ri = " << ri << std::endl;
    // ri = 100;
    // std::cout << "i = " << i << " ri = " << ri << std::endl;

    // const int ci = i;
    // const int& rci = i;
    // i = 13;
    // std::cout << "i = " << i << " ri = " << ri << std::endl;
    // ri = 100;
    // std::cout << "i = " << i << " ri = " << ri << std::endl;


    // int newX = 1;
    // addOne(newX);
    // std::cout << "newX = " << newX << std::endl;

    // Point a = {1, 2};
    // scalePoint(a, 2);
    // printPoint(a);

    // std::cout << isSmall(int) << std::endl;
    // std::cout << isSmall(Point) << std::endl;
    // std::cout << sizeof(Point) << std::endl;
    // std::cout << sizeof(void*) << std::endl;

    // static int a = 1;
    // const int& ra = a;
    // int* pa = &a;
    // constexpr int* cpa = &a;

    // std::cout << pa << std::endl;
    // std::cout << &ra << std::endl;
    // std::cout << &a << std::endl;

    // int b1 = 1;
    // int * pb = &b1;
    // {
    //     int b = 2;
    //     pb = &b;
    // }
    // std::cout << *pb << std::endl;

    // int* a {};
    // int** pa = &a;
    // std::cout << a << std::endl;
    // std::cout << pa << std::endl;
    // std::cout << *pa << std::endl;

    // // 指向常量的指针
    // const int c = 1;
    // const int* p = &c;
    // const int c2 = 2;
    // p = &c2;
    // // 常量指针
    // int c3 = 3;
    // int* const p2 = &c3;
    // // p2 = &c; error

    int a {};
    int* pa = &a;
    // foo(pa);
    twoLevelPointer(&pa);
    std::cout << a << std::endl;
    std::cout << (pa == nullptr) << std::endl;


    return 0;
}

void foo(int*& p) {
    *p = 101;
    p = nullptr;
}

void twoLevelPointer(int** pp){
    **pp = 1000001;
    *pp = nullptr;
}

void addOne(int& i){
    i++;
}

void scalePoint(Point& p, double factor){
    p.x *= factor;
    p.y *= factor;
}

void printPoint(const Point& p){
    std::cout << "Point: " << p.x << ", " << p.y << std::endl;
}