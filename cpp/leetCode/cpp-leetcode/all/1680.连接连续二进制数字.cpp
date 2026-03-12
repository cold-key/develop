/*
 * @lc app=leetcode.cn id=1680 lang=cpp
 *
 * [1680] 连接连续二进制数字
 */

#include<stdint.h>
#include<bit>
#include<iostream>

using namespace std;

// @lc code=start
class Solution {
public:
    int concatenatedBinary(int n) {
        int MODNUM = 1'000'000'007;
        long long ans = 0;
        for(int i = 1 ; i <= n; i++){
            int bitLen = bit_width((uint32_t)i);
            ans = (ans << bitLen | i) % MODNUM;
        }
        return ans;
    }
};
// @lc code=end

// 加法和乘法可以中间取模
// (a + b) % MOD = (a % MOD + b % MOD) % MOD

int main(){
    Solution s;
    std::cout << s.concatenatedBinary(12);
}