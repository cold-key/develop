/*
 * @lc app=leetcode.cn id=67 lang=cpp
 *
 * [67] 二进制求和
 */
#include<iostream>
#include<string>
using namespace std;
// @lc code=start
class Solution {
public:
    string addBinary(string a, string b) {
        int aIndex = a.length() - 1;
        int bIndex = b.length() - 1;
        int jw = 0;
        string result = "";
        // result.reserve(max(a.length(),b.length())); 
        while(aIndex >= 0 && bIndex >= 0){
            int sum = (a[aIndex] -'0') + (b[bIndex] -'0');
            cout << "sum: " << sum << '\n';
            sum+=jw;
            cout << "sum: " << sum << '\n';
            jw = sum / 2;
            cout << "jw: " << jw << '\n';
            sum = sum % 2;
            cout << "sum: " << sum << '\n';
            result = to_string(sum) + result;

            aIndex--;
            bIndex--;
        }
        cout << result;
        while(aIndex >= 0){
            int sum = (a[aIndex] -'0');
            sum+=jw;
            jw = sum / 2;
            sum = sum % 2;
            result = to_string(sum) + result;
            aIndex--;
        }
        while(bIndex >= 0){
            int sum = (b[bIndex] -'0');
            sum+=jw;
            jw = sum / 2;
            sum = sum % 2;
            result = to_string(sum) + result;
            bIndex--;
        }
        if(jw > 0){
            result = to_string(jw) + result;
        }
        return result;
    }

};
// @lc code=end

// int main(){
//     string a = "11";
//     string b = "1";
//     Solution s;
//     s.addBinary(a,b);
//     return 0;
// }