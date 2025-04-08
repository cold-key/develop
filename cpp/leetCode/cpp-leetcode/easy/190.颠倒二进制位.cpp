/*
 * @lc app=leetcode.cn id=190 lang=cpp
 *
 * [190] 颠倒二进制位
 */
#include<cstdint>
#include<iostream>
// @lc code=start
class Solution {
public:
    uint32_t reverseBits(uint32_t n) {
        uint32_t rev = 0;
        for (int i = 0; i < 32 && n > 0; ++i) {
            // std::cout << "shouwei:" << ((n & 1) << (31 - i)) << '\n';
            rev |= (n & 1) << (31 - i);
            // std::cout << "rev:" << rev << '\n';
            n >>= 1;
            // std::cout << "n:" << n << '\n';
        }
        return rev;
    }
};
// @lc code=end

// int main(){
//     uint32_t a = 127;
//     Solution s;
//     s.reverseBits(a);
//     return 0;
// }
