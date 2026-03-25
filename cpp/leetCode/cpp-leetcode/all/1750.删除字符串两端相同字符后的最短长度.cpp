/*
 * @lc app=leetcode.cn id=1750 lang=cpp
 *
 * [1750] 删除字符串两端相同字符后的最短长度
 */

#include<string>
#include<iostream>

using namespace std;

// @lc code=start
class Solution {
public:
    int minimumLength(string s) {
        int left = 0;
        int right = s.size() - 1;
        while(left < right && s[left] == s[right]){
            char curChar = s[left];
            while(s[left] == curChar && left <= right){
                ++left;
            }
            while(s[right] == curChar && left <= right){
                --right;
            }
        }
        return right - left + 1;
    }
};
// @lc code=end

// int main(){
//     Solution s;
//     std::string str = "cabaabac";
//     std::cout << s.minimumLength(str);
// }
