/*
 * @lc app=leetcode.cn id=1404 lang=cpp
 *
 * [1404] 将二进制表示减到 1 的步骤数
 */
#include "lib/tool.h"
#include<bitset>

using namespace std;

// @lc code=start
class Solution {
public:
    int numSteps(string s) {
        int len = s.size();
        int ans = 0;
        int carry = 0;
        for(int i = len - 1; i >= 0; i--){
            if(i == 0 && carry == 0){
                break;
            }
            if(s[i] == '0'){
                if(carry == 0){
                    ++ans;
                    carry = 0;
                }else{
                    ans+=2;
                    carry = 1;
                }
            }else{
                if(carry == 0){
                    ans += 2;
                    carry = 1;
                }else{
                    ++ans;
                    carry = 1;
                }
            }
        }
        return ans;
    }
};
// @lc code=end

