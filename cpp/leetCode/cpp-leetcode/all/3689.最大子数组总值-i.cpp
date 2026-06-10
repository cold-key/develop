/*
 * @lc app=leetcode.cn id=3689 lang=cpp
 *
 * [3689] 最大子数组总值 I
 */

#include <vector>
#include <iostream>
#include <algorithm>
#include <ranges>

using namespace std;

// @lc code=start
class Solution {
public:
    long long maxTotalValue(vector<int>& nums, int k) {
        auto [mn, mx] = ranges::minmax(nums);
        return 1LL * (mx - mn) * k;
    }
};
// @lc code=end

