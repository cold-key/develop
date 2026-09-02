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
    int jump2(vector<int>& nums) {
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

    int jump(vector<int>& nums){
        if(nums.size() <= 2){
            return std::max(int(nums.size() - 1),0);
        }
        if(nums[0] >= nums.size() - 1){
            return 1;
        }
        int curDealStep = 1;
        int curStepFarIndex = nums[0];
        int nextStepFarIndex = 0;
        for(int i = 1; i < nums.size(); ++i){
            nextStepFarIndex = std::max(nextStepFarIndex,i+nums[i]);
            if(nextStepFarIndex >= nums.size() - 1){
                break;
            }
            if(curStepFarIndex == i){
                ++curDealStep;
                curStepFarIndex = nextStepFarIndex;
                nextStepFarIndex = 0;
            }
        }
        return curDealStep + 1;
    }
};
// @lc code=end

int main(){
    Solution s;
    vector<int> nums = {2,3,1,1,4};
    cout << s.jump2(nums) << endl;
    return 0;
}