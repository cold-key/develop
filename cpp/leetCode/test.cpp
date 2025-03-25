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
#include<unordered_map>
#include<algorithm>
#include<cmath>
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

class Spreadsheet {
    public:
        unordered_map<int,int> data;
        Spreadsheet(int rows) {
            
        }
        
        void setCell(string cell, int value) {
            int decodeNum = decode(cell);
            this->data[decodeNum] = value;
        }
    
        int decode(string cell){
            cout << "cell:" << cell << "\n";
            int startIndex = 0;
            int rolNum = 0;
            int sub = cell[0] - 'A';
            cout << "sub:" << sub << "\n";
            if(cell[0] - 'A'<0 ||cell[0] - 'A'>25){
                rolNum = 0;
            }else{
                cout << "cell[0] : " << cell[0] << "\n";
                cout << "cell[0] - 'A' : " << (cell[0] - 'A') << "\n";
                rolNum = (cell[0] - 'A' + 1) * 1000;
                startIndex = 1;
            }
            int colNum = 0;
            for(int i = startIndex; i < cell.size(); i++){
                if(cell[i] - '0' == 0) continue;
                startIndex = i;
                break;
            }
            for(int i = startIndex; i < cell.size(); i++){
                colNum += (cell[i] - '0') * (pow(10,cell.size() - i -1));
            }
            cout << "rolNum:" << rolNum << "colNum:" << colNum << "\n";
            return rolNum + colNum;
        }
        
        void resetCell(string cell) {
            setCell(cell,0);
        }
        
        int getValue(string formula) {
            int index = 0;
            for(int i = 1; i < formula.size(); i++){
                if(formula[i] == '+'){
                    index = i;
                    break;
                }
            }
            string s1 = formula.substr(1, index-1);
            int value1 = decode(s1);
            int trueValue1 = value1>1000?this->data[value1]:value1;
            string s2 = formula.substr(index+1);
            int value2 = decode(s2);
            int trueValue2 = value2>1000?this->data[value2]:value2;
            cout << value1 << "%"<<value2<<"\n";
            return trueValue1 + trueValue2;
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
    // vector<int> test {1,2,3};
    // Solution s;
    // s.sumOfBeauties(test);

    Spreadsheet s(12);
    s.decode("0126");

    return 0;
}