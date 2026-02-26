/*
 * @lc app=leetcode.cn id=3634 lang=cpp
 *
 * [3634] 使数组平衡的最少移除数目
 */

#include<vector>
#include<iostream>
#include<algorithm>

using namespace std;

// @lc code=start
class Solution {
public:
    int minRemoval(vector<int>& nums, int k) {
        sort(nums.begin(),nums.end());
        int removeNums = 0;
        int startIndex = 0;
        int removeTimes = 0;
        int endIndex = nums.size() - 1;
        return removeTimes;
    }
};
// @lc code=end

