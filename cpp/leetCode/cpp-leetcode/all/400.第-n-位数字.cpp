/*
 * @lc app=leetcode.cn id=400 lang=cpp
 *
 * [400] 第 N 位数字
 */

#include<cmath>
#include<iostream>

// @lc code=start
class Solution {
public:
    int findNthDigit(int n) {
        if(n <= 9) return n;
        int ans = 0;
        long long sum = 9;
        for(int i = 2 ;; ++i){
            long long count = 9 * std::pow(10,i-1) * i;
            // std::cout << "count : " << count << std::endl;
            if(sum + count < n){
                sum +=count;
                continue;
            }
            else if(sum + count > n){
                int r = n - sum;
                int rMod = r % i;
                int rR = r / i;
                long long the_num = rMod == 0 ? std::pow(10, i-1) + rR - 1 : std::pow(10, i-1) + rR;
                rMod = rMod == 0 ? i : rMod;
                char c = std::to_string(the_num)[rMod - 1];
                // std::cout << "the_num : " << the_num << std::endl;
                // std::cout << "i : " << i << " r : " << r << " rMod : " << rMod << " rR : " << rR << " c : " << c << std::endl;
                ans = c - '0';
                break;
            }
            else{
                ans = 9;
                break;
            }
        }
        return ans;
    }
};
// @lc code=end

// int main(){
//     Solution sol;
//     int n = 11;
//     int result = sol.findNthDigit(n);
//     std::cout << "result : " << result << std::endl;
//     return 0;
// }

// 个人思路：
// 1. 首先确定n所在的数字的位数i，和n之前的数字的总位数sum
// 2. 确定n所在的数字the_num，和n在the_num中的位置rMod
// 3. 从the_num中取出第rMod位的数字，即为答案