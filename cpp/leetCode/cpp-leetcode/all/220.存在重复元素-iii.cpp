/*
 * @lc app=leetcode.cn id=220 lang=cpp
 *
 * [220] 存在重复元素 III
 */

#include<cmath>
#include<vector>
#include<set>

using namespace std;

// @lc code=start
class Solution {
public:
    bool containsNearbyAlmostDuplicate(vector<int>& nums, int indexDiff, int valueDiff) {
        std::set<int> s;
        for(int i = 0; i < nums.size(); i++){
            auto it = s.lower_bound(nums[i] - valueDiff);
            if(it != s.end() && *it <= valueDiff + nums[i]) return true;
            s.insert(nums[i]);
            if(i - indexDiff >= 0) s.erase(nums[i - indexDiff]);
        }
        return false;
    }
};
// @lc code=end

// 希望使用一个「有序集合」去维护长度为 k 的滑动窗口内的数，该数据结构最好支持高效「查询」与「插入/删除」操作
// TODO AVL树和红黑树