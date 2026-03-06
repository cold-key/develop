/*
 * @lc app=leetcode.cn id=1784 lang=cpp
 *
 * [1784] 检查二进制字符串字段
 */

#include"lib/tool.h"
using namespace std;

// @lc code=start
class Solution {
public:
    bool checkOnesSegment(string s) {
        bool isHaveZero = false;
        for(int i = 0; i < s.size(); i++){
            if(s[i] == '1' && isHaveZero){
                return false;
            }
            if(s[i] == '0'){
                isHaveZero = true;
            }
        }

        return true;
    }
};
// @lc code=end

