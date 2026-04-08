/*
 * @lc app=leetcode.cn id=189 lang=cpp
 *
 * [189] 轮转数组
 */

#include<vector>
#include<iostream>
// #include "lib/tool.h"

using namespace std;

// @lc code=start
class Solution {
public:
    void rotate(vector<int>& nums, int k) {
        int len = nums.size();
        k = k % len;
        if(k == 0){
            return;
        }
        int swapCount = 0;
        int startIndex = 0;
        int index = (startIndex + k) % len;
        int cacheValue = nums[startIndex];
        while(swapCount < len){
            int temp = nums[index];
            nums[index] = cacheValue;
            cacheValue = temp;
            index = (index + k) % len;
            ++swapCount;

            if(index == (startIndex + k) % len){
                ++startIndex;
                index = (startIndex + k) % len;;
                cacheValue = nums[startIndex];
            }

            // printVector(nums);
        }
    }
};
// @lc code=end

// int main(){
//     Solution solution;
//     std::vector<int> nums = {1,2,3,4,5,6,7};
//     int k = 2;
//     solution.rotate(nums,k);
//     for(auto num : nums){
//         std::cout << num << " ";
//     }
// }