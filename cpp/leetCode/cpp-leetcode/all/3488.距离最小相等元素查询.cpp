/*
 * @lc app=leetcode.cn id=3488 lang=cpp
 *
 * [3488] 距离最小相等元素查询
 */

#include<vector>
#include<unordered_map>
#include<set>

using namespace std;

// @lc code=start
class Solution {
public:
    vector<int> solveQueries(vector<int>& nums, vector<int>& queries) {
        std::unordered_map<int,std::set<int>> map;
        for(int i = 0; i < nums.size(); ++i){
            map[nums[i]].insert(i);
        }
        std::vector<int> ans (queries.size(), 0);
        
    }
};
// @lc code=end

