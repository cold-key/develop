#include <cstdint>
#include <iostream>
#include <vector>

struct Point{
    double x;
    double y;
    double z;
};

enum Color{
    Red,
    Green,
    Blue
};

enum Feeling : std::uint8_t{
    Happy,
    Sad,
    Angry,
};

enum class Size{
    Small,
    Medium,
    Large,
};

struct Nothing {
    int x;
    int y {};
    int z {121};
};

void printStruct(const Point& p){
    std::cout << p.x << ", " << p.y << ", " << p.z << std::endl;
}

void printStruct(const Nothing& p){
    std::cout << p.x << ", " << p.y << ", " << p.z << std::endl;
}

int main(){
    Point p {}; // 列表初始化（推荐）
    printStruct(p);

    Point p2 = {1, 2, 3}; // 拷贝列表初始化（不推荐）
    printStruct(p2);

    Point p3 {1,2};
    printStruct(p3);

    Nothing n {};
    printStruct(n);

    Color c = Red;
    std::cout << (Blue == 2) << std::endl;

    // Feeling f = Angry;
    // std::cout << static_cast<std::uint8_t>(f) << std::endl;
    // std::cout << Happy << std::endl;

    Size s = Size::Small;
    std::cout << static_cast<int>(s) << std::endl;

    std::cout << __cplusplus << std::endl;
    // for(int i = 0; i < 10; i++){
    //     using enum Size;
    //     if(i == static_cast<int>(Size::Small)){
    //         std::cout << "Small" << std::endl;
    //     }
    // }
    return 0;
}