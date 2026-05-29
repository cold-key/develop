/*
 * @lc app=leetcode.cn id=58 lang=cpp
 *
 * [58] 最后一个单词的长度
 */

#include<string>

using namespace std;

// @lc code=start
class Solution {
public:
    int lengthOfLastWord(string s) {
        bool flag = false;
        int ans = 0;
        for(int i = s.size() - 1; i >= 0; --i) {
            if(s[i] == ' ') {
                if(flag) {
                    break;
                }
            } else {
                flag = true;
                ++ans;
            }
        }
        return ans;
    }
};
// @lc code=end

