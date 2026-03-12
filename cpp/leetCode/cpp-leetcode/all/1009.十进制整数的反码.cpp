/*
 * @lc app=leetcode.cn id=1009 lang=cpp
 *
 * [1009] 十进制整数的反码
 */

#include<bitset>
#include<string>

using namespace std;

// @lc code=start
class Solution {
public:
    int bitwiseComplement(int n) {
        if(n == 0){
            return 1;
        }
        int ans = 0;
        int bitPower = 1;
        while(n>0){
            int rightBit = n % 2;
            ans += ((rightBit + 1) % 2) * bitPower;
            bitPower <<= 1;
            n >>= 1;
        }
        return ans;
    }
};
// @lc code=end

// bit_ceil (C++20) : 计算不小于 x 的最小的 2 的整数次幂
// template< class T >
// constexpr T bit_ceil( T x );
