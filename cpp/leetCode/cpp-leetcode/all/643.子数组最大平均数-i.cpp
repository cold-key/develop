/*
 * @lc app=leetcode.cn id=643 lang=cpp
 *
 * [643] 子数组最大平均数 I
 */

#include<iostream>
#include<vector>

using namespace std;

// @lc code=start
class Solution {
public:
    double findMaxAverage(vector<int>& nums, int k) {
        int leftIndex = 0;
        int rightIndex = 0;
        double maxAvg = -2147483648;
        double sum = 0;
        for(int i = 0; i < nums.size(); i++){
            if(i - leftIndex <= k - 1){
                sum += nums[i];
                maxAvg = sum / k;
                continue;
            }
            sum = sum - nums[leftIndex] + nums[i];
            maxAvg = maxAvg > (sum / k) ? maxAvg : (sum / k);

            leftIndex++;
            rightIndex = i;
        }
        return maxAvg;
    }
};
// @lc code=end

