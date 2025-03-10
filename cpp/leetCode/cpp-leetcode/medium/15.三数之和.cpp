/*
 * @lc app=leetcode.cn id=15 lang=cpp
 *
 * [15] 三数之和
 */

// @lc code=start
#include<vector>
#include <algorithm>
using namespace std;

class Solution {
public:
    vector<vector<int>> threeSum(vector<int>& nums) {
        vector<vector<int>> result;
        unique(nums.begin(),nums.end());
        sort(nums.begin(),nums.end());
        for(int i = 0; i < nums.size(); i++){
            int j = 0;
            int k = nums.size() - 1;
            while(j != k){
                if(i==j){
                    j++;
                    continue;
                }else if(i==k){
                    k--;
                }
                if(nums[i] + nums[j] + nums[k] == 0){
                    vector<int> temp {nums[i],nums[j],nums[k]};
                    result.push_back(temp);
                    j++;
                    k--;
                }else if(nums[i] + nums[j] + nums[k] < 0){
                    j++;
                }else{
                    k--;
                }
            }
        }
        return result;
    }
};
// @lc code=end

