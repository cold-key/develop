/*
 * @lc app=leetcode.cn id=238 lang=cpp
 *
 * [238] 除了自身以外数组的乘积
 */

#include<iostream>
#include<vector>

using namespace std;

// @lc code=start
class Solution {
public:
    vector<int> productExceptSelf(vector<int>& nums) {
        if(nums.size() == 1){
            return nums;
        }
        vector<int> answer (nums.size(),1);
        answer[0] = nums[0];
        for(int i = 1; i < nums.size(); ++i){
            answer[i] = nums[i] * answer[i - 1];
        }
        int product = nums[nums.size() - 1];
        answer[answer.size() - 1] = answer[answer.size() - 2];
        for(int i = answer.size() - 2; i > 0; --i){
            answer[i] = answer[i - 1] * product;
            product *= nums[i];
        }
        answer[0] = product;
        return answer;
    }
};
// @lc code=end

int main(){
    vector<int> nums = {1,2};
    Solution s;
    vector<int> answer = s.productExceptSelf(nums);
    for(auto v : answer){
        std::cout << v << " , ";
    }
}