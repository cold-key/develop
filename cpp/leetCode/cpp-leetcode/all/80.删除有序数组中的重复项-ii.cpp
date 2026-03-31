/*
 * @lc app=leetcode.cn id=80 lang=cpp
 *
 * [80] 删除有序数组中的重复项 II
 */
#include "lib/tool.h"
#include<iostream>
#include<vector>

using namespace std;

// @lc code=start
class Solution {
public:
    int removeDuplicates(vector<int>& nums) {
        int leftIndex = 0;
        int rightIndex = 1;
        int curNumCount = 1;
        int lastNum = nums[0];
        for(; rightIndex < nums.size(); ++rightIndex){
            if(nums[rightIndex] == lastNum){
                ++curNumCount;
            }else{
                lastNum = nums[rightIndex];
                curNumCount = 1;
            }
            if(curNumCount <= 2){
                nums[++leftIndex] = nums[rightIndex];
            }
        }
        return leftIndex + 1;
    }
};
// @lc code=end

int main(){
    std::vector<int> nums {0,0,1,1,1,1,2,3,3};
    Solution s;
    int len = s.removeDuplicates(nums);

    for(int i = 0; i < len; ++i){
        std::cout << nums[i] << " , ";
    }
}