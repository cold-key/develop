#include <iostream>

// int getAdd(int a, int b);

// int getAdd(int a, char b) = delete;
// =delete表示“我禁止这样做”，而不是“这不存在”。
//删除的函数参与函数重载决议的所有阶段（不仅仅是精确匹配阶段）。如果匹配到已删除的函数，则会导致编译错误。

// 不允许返回值不一样的函数重载
// double getAdd(int a, int b){
//     return a + b;
// }

template<typename T>
T getAdd(T a, T b){
    return a + b;
}

template<>
int getAdd(int a, int b) = delete;

int main(){
    // std::cout<< getAdd(1, 2) <<'\n';
    // std::cout<< getAdd(1, '2') <<'\n';
    std::cout<< getAdd(1.0, 2.0) <<'\n';
    return 0;
}

// int getAdd(int a, int b){
//     return a + b;
// }
