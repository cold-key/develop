/*
 * @lc app=leetcode.cn id=45 lang=cpp
 *
 * [45] 跳跃游戏 II
 */

// @lc code=start
#include<vector>
#include<iostream>
using namespace std;
class Solution {
public:
    int jump(vector<int>& nums) {
        vector<int> minJumpArray (nums.size(),nums.size());
        minJumpArray[0] = 0;
        for(int i = 0; i < nums.size(); i++){
            int value = nums[i];
            for(int j = 1; j <= value; j++){
                if(i + j >= nums.size()){
                    break;
                }
                if(minJumpArray[i + j] > minJumpArray[i] + 1){
                    minJumpArray[i + j] = minJumpArray[i] + 1;
                }
            }
        }
        return minJumpArray[nums.size() - 1];
    }
};
// @lc code=end

// int main(){
//     vector<int> test {2,3,1,1,4};
//     Solution s;
//     cout << s.jump(test);
//     return 0;
// }