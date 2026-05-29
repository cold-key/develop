/*
 * @lc app=leetcode.cn id=14 lang=cpp
 *
 * [14] 最长公共前缀
 */

#include<string>
#include<vector>
#include<ranges>
#include<algorithm>

using namespace std;

// @lc code=start
class Solution {
public:
    string longestCommonPrefix(vector<string>& strs) {
        if(strs.empty()) return "";
        int minIndex = 0;
        int maxIndex = 0;
        for(int i = 1; i < strs.size(); ++i) {
            if(strs[i] < strs[minIndex]) {
                minIndex = i;
            }
            if(strs[i] > strs[maxIndex]) {
                maxIndex = i;
            }
        }
        const string& min = strs[minIndex];
        const string& max = strs[maxIndex];
        int i = 0;
        while(i < min.size() && i < max.size() && min[i] == max[i]) {
            ++i;
        }
        return min.substr(0, i);
    }
};
// @lc code=end

