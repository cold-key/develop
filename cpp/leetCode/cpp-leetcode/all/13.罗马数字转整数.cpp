/*
 * @lc app=leetcode.cn id=13 lang=cpp
 *
 * [13] 罗马数字转整数
 */

#include<string>
#include<unordered_map>

using namespace std;

// @lc code=start
class Solution {
public:
    int romanToInt(string s) {
        int ans = 0;
        std::unordered_map<char, int> m = {
            {'I', 1},
            {'V', 5},
            {'X', 10},
            {'L', 50},
            {'C', 100},
            {'D', 500},
            {'M', 1000}
        };
        for(int i  = 0; i < s.size() - 1; ++i) {
            int l = m[s[i]];
            int r = m[s[i + 1]];
            if(l < r) {
                ans -= l;
            } else {
                ans += l;
            }
        }
        ans += m[s.back()];
        return ans;
    }
};
// @lc code=end

