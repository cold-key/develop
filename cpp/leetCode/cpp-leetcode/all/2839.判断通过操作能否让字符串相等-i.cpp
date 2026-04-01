/*
 * @lc app=leetcode.cn id=2839 lang=cpp
 *
 * [2839] 判断通过操作能否让字符串相等 I
 */

#include<vector>
#include<string>
#include<iostream>

using namespace std;

// @lc code=start
class Solution {
public:
    bool canBeEqual(string s1, string s2) {
        return checkStrings(s1, s2);
    }

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

