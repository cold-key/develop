/*
 * @lc app=leetcode.cn id=2840 lang=cpp
 *
 * [2840] 判断通过操作能否让字符串相等 II
 */

#include<vector>
#include<string>
#include<iostream>
// #include "lib/tool.h"
using namespace std;

// @lc code=start
class Solution {
public:
    bool checkStrings(string s1, string s2) {
        std::vector<int> bucket (26,0);
        for(int i = 0; i < 2 ;++i){
            for(int j = i; j < s1.size(); j += 2){
                ++bucket[s1[j] - 'a'];
            }
            // printVector(bucket);
            for(int j = i; j < s2.size(); j += 2){
                --bucket[s2[j] - 'a'];
            }
            // printVector(bucket);
            for(int j = 0; j < bucket.size(); ++j){
                if(bucket[j] != 0){
                    return false;
                }
            }
        }
        return true;
    }
};
// @lc code=end

// int main(){
//     Solution sol;
//     string s1 = "abe";
//     string s2 = "bea";
//     bool result = sol.checkStrings(s1, s2);
//     std::cout << "result : " << result << std::endl;
//     return 0;
// }