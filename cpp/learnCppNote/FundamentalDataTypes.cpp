#include<iostream>
#include <string>

int main(){
    std::string input{};
    std::cin>>input;
    std::getline(std::cin>>std::ws,input);

    // std::string::length() 返回无符号整数值（很可能是size_t类型）。如果要将长度分配给int变量，则应将其static_cast，以避免编译器对有符号/无符号转换发出警告:
    std::cout<<"string length :" << input.length()<<'\n';
    // 在C++20中，您还可以使用std::ssize() 函数来获取std::string的长度作为有符号整数值
    // std::cout<<"string length :" << std::ssize(input)<<'\n'; //现在我的这个环境不支持C++20

    // 每当初始化std::string时，都会生成用于初始化它的字符串的副本。复制字符串的成本很高，因此应注意将复制的数量降至最低。
    // 不要按值传递std::string，因为它会生成昂贵的副本。在大多数情况下，请改用std::string_view参数

    //

    return 0;
}