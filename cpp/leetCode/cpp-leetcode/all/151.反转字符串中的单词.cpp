/*
 * @lc app=leetcode.cn id=151 lang=cpp
 *
 * [151] 反转字符串中的单词
 */

#include<string>
#include<vector>
#include<algorithm>
#include<iostream>

using namespace std;

// @lc code=start
class Solution {
public:
    string reverseWords(string s) {
        std::reverse(s.begin(), s.end());
        int head = 0;
        for(int i = 0; i < s.size(); ++i) {
            if(s[i] != ' ') {
                if(head != 0) s[head++] = ' ';
                int j = i;
                while(j < s.size() && s[j] != ' ') {
                    s[head++] = s[j++];
                }
                std::reverse(s.begin() + head - (j - i), s.begin() + head);
                i = j;
            }
        }
        s.erase(s.begin() + head, s.end());

        return s;
    }
};
// @lc code=end

int main() {
    Solution s;
    std::string result = s.reverseWords("  hello world!  ");
    std::cout << result << std::endl;
    return 0;
}