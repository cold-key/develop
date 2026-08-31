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
        int curIndex = 0;
        int startIndex = curIndex;
        int cacheValue = nums[curIndex];
        while(swapCount < len){
            int nextIndex = (curIndex + k) % len;
            int temp = nums[nextIndex];
            nums[nextIndex] = cacheValue;
            cacheValue = temp;
            curIndex = nextIndex;
            ++swapCount;

            // std::cout << "temp:" << temp << std::endl;

            if(curIndex == startIndex){
                curIndex = ++curIndex % len;
                cacheValue = nums[curIndex];
                startIndex = curIndex;
            }

            // std::cout << curIndex << "," << cacheValue << "," << swapCount << std::endl;
        }
    }
};
// @lc code=end

int main(){
    Solution solution;
    std::vector<int> nums = {-1,-100,3,99};
    std::vector<int> nums2 = {1,2,3,4,5,6,7};
    int k = 3;
    solution.rotate(nums,k);
    for(auto num : nums){
        std::cout << num << " ";
    }
}