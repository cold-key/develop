/*
 * @lc app=leetcode.cn id=220 lang=cpp
 *
 * [220] 存在重复元素 III
 */

#include<cmath>
#include<vector>

using namespace std;

// @lc code=start
class Solution {
public:
    bool containsNearbyAlmostDuplicate(vector<int>& nums, int indexDiff, int valueDiff) {
        for(int i = 0; i < nums.size(); i++){
            int leftIndex = i - indexDiff > 0 ? i - indexDiff : 0;
            for(int j = i - 1; j >= leftIndex; j--){
                if(std::abs(nums[j] - nums[i]) <= valueDiff){
                    return true;
                }
            }
        }
        return false;
    }
};
// @lc code=end

