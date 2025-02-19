# 控制流
## Constexpr if
考虑以下代码
```cpp
    constexpr int x {9};
    if(x == 9){
        std::cout << "true";
    }else{
        std::cout << "true";
    }
```
在运行时计算constexpr条件表达式是浪费的（因为结果永远不会变化）。将代码编译为永远无法执行的可执行文件也是浪费的。

C++17引入了 constexpr if 语句，该语句要求条件是常量表达式。将在**编译时计算constexpr if语句的条件表达式的结果**。如果constexpr条件的计算结果为true，则整个If-else将替换为true语句。如果constexpr条件的计算结果为false，则整个If-else将替换为false语句（如果存在else）或直接删除（如果没有else）。
```cpp
    constexpr int x {9};
    if constexpr (x == 9){
        std::cout << "true";
    }else{
        std::cout << "true";
    }
```

出于优化目的，现代编译器通常将具有常量条件的非constexpr-if语句视为constexpr-if语句。然而，这并不意味着一定会这样做。遇到具有常量条件的非constexpr-if语句，编译器可能会发出警告，建议您改用constexpr-if语句。这将确保发生编译时计算（即使禁用编译优化）。

