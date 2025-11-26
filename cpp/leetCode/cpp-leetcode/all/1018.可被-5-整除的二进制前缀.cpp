/*
 * @lc app=leetcode.cn id=1018 lang=cpp
 *
 * [1018] 可被 5 整除的二进制前缀
 */

#include<iostream>
#include<vector>
#include<queue>

using namespace std;

// @lc code=start
class Solution {
public:
    vector<bool> prefixesDivBy5(vector<int>& nums) {
        int mn = 0;
        vector<bool> result;
        for(int i = 0; i < nums.size(); i++){
            mn = (mn * 2 + nums[i]) % 5;
            result.push_back(mn == 0);
        }
        return result;
    }
};
// @lc code=end

// int main(){
//     vector<int> nums = {1,1,1};
//     Solution s;
//     vector<bool> result = s.prefixesDivBy5(nums);
//     for(int i = 0; i < result.size();i++){
//         std::cout << result[i] << ",";
//     }
// }