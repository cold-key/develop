/*
 * @lc app=leetcode.cn id=55 lang=cpp
 *
 * [55] 跳跃游戏
 */

#include<vector>
#include<iostream>

using namespace std;

// @lc code=start
class Solution {
public:
    bool canJump(vector<int>& nums) {
        int curFarIndex = nums[0];
        for(int i = 1; i < nums.size(); ++i){
            if(i > curFarIndex){
                return false;
            }
            if(curFarIndex >= nums.size() - 1){
                return true;
            }
            curFarIndex = std::max(curFarIndex,i+nums[i]);
        }
        return true;
    }
};
// @lc code=end

// int main(){
//     Solution s;
//     vector<int> nums = {3,2,1,0,4};
//     cout << s.canJump(nums) << endl;
//     return 0;
// }