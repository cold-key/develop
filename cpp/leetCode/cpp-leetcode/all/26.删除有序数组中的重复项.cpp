/*
 * @lc app=leetcode.cn id=26 lang=cpp
 *
 * [26] 删除有序数组中的重复项
 */

#include<iostream>
#include<vector>

using namespace std;

// @lc code=start
class Solution {
public:
    int removeDuplicates(vector<int>& nums) {
        int leftIndex = 0;
        int rightIndex = 1;
        for(; rightIndex < nums.size(); ++rightIndex){
            if(nums[rightIndex] == nums[rightIndex-1]){
                continue;
            }else{
                nums[++leftIndex] = nums[rightIndex];
            }
        }
        return leftIndex+1;
    }
};
// @lc code=end

