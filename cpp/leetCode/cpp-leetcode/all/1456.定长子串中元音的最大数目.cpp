/*
 * @lc app=leetcode.cn id=1456 lang=cpp
 *
 * [1456] 定长子串中元音的最大数目
 */

#include<iostream>
#include<string>
#include<unordered_set>

using namespace std;

// @lc code=start
class Solution {
public:
    int maxVowels(string s, int k) {
        std::unordered_set<char> aimSet {'a','e','i','o','u'};
        int result = 0;
        int maxResult = 0;
        for(int i = 0; i < k; i++){
            if(aimSet.count(s[i])){
                ++result;
            }
        }
        maxResult = maxResult > result ? maxResult : result;
        int left = 0;
        int right = k-1;
        for(int i = k; i < s.size(); i++){
            if(aimSet.count(s[left])){
                result--;
            }
            if(aimSet.count(s[i])){
                result++;
            }
            maxResult = maxResult > result ? maxResult : result;
            left++;
            right++;
        }
        return maxResult;
    }
};
// @lc code=end

