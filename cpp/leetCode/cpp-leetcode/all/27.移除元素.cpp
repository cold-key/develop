/*
 * @lc app=leetcode.cn id=27 lang=cpp
 *
 * [27] 移除元素
 */

#include <iostream>
#include <vector>
using namespace std;

// @lc code=start
class Solution {
public:
    int removeElement(vector<int>& nums, int val) {
        int front = 0;
        for(int i = 0; i < nums.size(); ++i){
            if(nums[i] == val) continue;
            nums[front++] = nums[i];
        }
        nums.resize(front);
        return front;
    }
};
// @lc code=end

int main(){
    std::vector nums {1,2,4,5,1,2,3,4,6,89,54,21,325,1,1};
    Solution s;
    std::cout << s.removeElement(nums,1) << std::endl;
    for(auto v : nums){
        std::cout << v << " , "; 
    }
}