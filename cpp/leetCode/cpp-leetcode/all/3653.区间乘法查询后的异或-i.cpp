/*
 * @lc app=leetcode.cn id=3653 lang=cpp
 *
 * [3653] 区间乘法查询后的异或 I
 */

#include<vector>
#include<iostream>

using namespace std;

// @lc code=start
class Solution {
public:
    int xorAfterQueries(vector<int>& nums, vector<vector<int>>& queries) {
        int MOD = 1e9 + 7;
        for(auto query : queries){
            int left = query[0];
            int right = query[1];
            int key = query[2];
            int value = query[3];
            for(int i = left; i <= right; i+=key){
                long long temp = ((long long)(nums[i] % MOD) * (long long)(value % MOD)) % MOD;
                nums[i] = temp;
            }
        }
        int result = 0;
        for(auto num : nums){
            result ^= num;
        }
        return result;
    }
};
// @lc code=end

// int main(){
//     Solution solution;
//     std::vector<int> nums = {2,3,1,5,4};
//     std::vector<std::vector<int>> queries = {{1,4,2,3},{0,2,1,2}};
//     int result = solution.xorAfterQueries(nums,queries);
//     std::cout << "result: " << result << std::endl;
//     return 0;
// }