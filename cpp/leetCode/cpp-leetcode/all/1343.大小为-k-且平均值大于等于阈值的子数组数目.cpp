/*
 * @lc app=leetcode.cn id=1343 lang=cpp
 *
 * [1343] 大小为 K 且平均值大于等于阈值的子数组数目
 */

#include<iostream>
#include<vector>

using namespace std;

// @lc code=start
class Solution {
public:
    int numOfSubarrays(vector<int>& arr, int k, int threshold) {
        int leftIndex = 0;
        int rightIndex = 0;
        long sum = 0;
        int avg = 0;
        int result = 0;
        for(int i = 0; i < arr.size(); i++){
            if(i - leftIndex <= k - 1){
                sum += arr[i];
                avg = i - leftIndex == k - 1 ? sum / k : threshold - 1;
                if(avg >= threshold){
                    result++;
                }
                continue;
            }
            sum = sum - arr[leftIndex] + arr[i];
            avg = sum / k;
            if(avg >= threshold){
                result++;
            }

            leftIndex++;
            rightIndex = i;
        }
        return result;
    }
};
// @lc code=end

