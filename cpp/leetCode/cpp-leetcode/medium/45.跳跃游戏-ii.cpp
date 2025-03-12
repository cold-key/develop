/*
 * @lc app=leetcode.cn id=45 lang=cpp
 *
 * [45] 跳跃游戏 II
 */

// @lc code=start
#include<vector>
using namespace std;
class Solution {
public:
    int jump(vector<int>& nums) {
        vector<int> minJumpArray (nums.size());
        minJumpArray[0] = 0;
        for(int i = 1; i < nums.size(); i++){
            int value = nums[i];
            for(int j = 1; j <= value; j++){
                if(minJumpArray[i + j] > minJumpArray[i] + 1){
                    minJumpArray[i + j] = minJumpArray[i] + 1;
                }
            }
        }
        return minJumpArray[nums.size() - 1];
    }
};
// @lc code=end

