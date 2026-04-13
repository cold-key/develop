/*
 * @lc app=leetcode.cn id=45 lang=cpp
 *
 * [45] 跳跃游戏 II
 */

#include<vector>
#include<iostream>

using namespace std;

// @lc code=start
class Solution {
public:
    int jump(vector<int>& nums) {
        int ans = 0;
        if(nums.size() <= 1){
            return ans;
        }
        for(int i = 0; i < nums.size(); ){
            if(i >= nums.size() - 1){
                break;
            }
            int farIndex = i + nums[i];
            if(farIndex >= nums.size() - 1){
                ++ans;
                break;
            }
            for(int j = i; j <= i + nums[i] && j < nums.size(); ++j){
                farIndex = nums[j] + j > farIndex + nums[farIndex] ? j :farIndex;
            }
            i = farIndex;
            ++ans;
        }
        return ans;
    }
};
// @lc code=end

// int main(){
//     Solution s;
//     vector<int> nums = {2,3,0,1,4};
//     cout << s.jump(nums) << endl;
//     return 0;
// }