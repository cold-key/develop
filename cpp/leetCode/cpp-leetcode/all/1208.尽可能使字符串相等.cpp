/*
 * @lc app=leetcode.cn id=1208 lang=cpp
 *
 * [1208] 尽可能使字符串相等
 */

#include<iostream>
#include<string>

using namespace std;

// @lc code=start
class Solution {
public:
    int equalSubstring(string s, string t, int maxCost) {
        int leftIndex = 0;
        int maxLen = -1;
        for(int i = 0; i < s.size(); i++){
            int cost = abs(s[i] - t[i]);
            if(cost <= maxCost){
                maxCost -= cost;
                int newLen = i - leftIndex + 1;
                maxLen = maxLen > newLen ? maxLen : newLen;
                continue;
            }else{
                maxCost -= cost;
                while(maxCost < 0){
                    maxCost += abs(s[leftIndex] - t[leftIndex]);
                    leftIndex++;
                }
                int newLen = i - leftIndex + 1;
                maxLen = maxLen > newLen ? maxLen : newLen;
            }
        }
        return maxLen;
    }
};
// @lc code=end

