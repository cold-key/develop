#include <iostream>
#include<algorithm>

// 前向声明
class MyClass;
void foo(MyClass* obj);

class MyClass {
public:
    void bar() {
        std::cout << "hi" << "\n";
    }
};

void foo(MyClass* obj) {
    obj->bar();
}

using namespace std;
#include <vector>
class Solution {
    public:
        int sumOfBeauties(vector<int>& nums) {
        vector<int> left (nums.size());
        int maxNum = nums[0];
        for(int i = 1; i < nums.size() - 1; i++){
            if(nums[i] > maxNum){
                left[i] = 1;
                maxNum = nums[i];
            }
        }
        int sum = 0;
        int minNum = nums[nums.size() - 1];
        for(int i = nums.size() - 2 ; i > 0; i--){
            if(nums[i] < minNum){
                minNum = nums[i];
                if(left[i] == 1){
                    sum += 2;
                }else if(nums[i] < nums[i + 1] && nums[i - 1] < nums[i]){
                    sum += 1;
                }
            }else if(nums[i] < nums[i + 1] && nums[i - 1] < nums[i]){
                sum += 1;
            }
        }
        return sum;
    }
};

int main()
{
    // MyClass m = MyClass();
    // int a {0};
    // foo(&m);

    // char c {};
    // std::cout << a-- << "\n";
    // c = 123;
    // std::cout << --a << "\n";

    // // 类型转换：优先使用static_cast<T>, 避免使用c风格的类型转换 int(5.5)
    // // static_cast在编译期就会进行类型检查，而函数式转换则是在运行时进行的。
    // // 静态转换在编译期就确保了类型转换的合法性，而函数式转换则允许在运行时进行更灵活的转换，尽管这种灵活性可能会带来运行时错误的风险。
    // std::cout << static_cast<int>(3.1415) << '\n';
    // // int three = int(3.1415);
    // // int* p = (int*) three; // warning: cast to pointer from integer of different size [-Wint-to-pointer-cast]
    // // std::cout << p << '\n';

    // //任何在初始化后不修改，且其初始值在编译时已知的变量都应声明为constexpr。任何在初始化后不修改，且其初始值在编译时未知的变量都应声明为const。


    // test
    vector<int> test {1,2,3};
    Solution s;
    s.sumOfBeauties(test);

    return 0;
}