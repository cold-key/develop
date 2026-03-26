/*
 * @lc app=leetcode.cn id=11 lang=cpp
 *
 * [11] 盛最多水的容器
 */

#include<iostream>
#include<vector>

using namespace std;

// @lc code=start
class Solution {
public:
    int maxArea(vector<int>& height) {
        int ans = 0;
        int left = 0;
        int right = height.size() - 1;
        while(left < right){
            int curCapa = (right - left) * std::min(height[left],height[right]);
            ans = std::max(ans,curCapa);
            if(height[left] < height[right]){
                ++left;
            }else{
                --right;
            }
        }
        return ans;
    }
};
// @lc code=end

