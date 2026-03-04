/*
 * @lc app=leetcode.cn id=1545 lang=cpp
 *
 * [1545] 找出第 N 个二进制字符串中的第 K 位
 */

#include<iostream>

// @lc code=start
class Solution {
public:
    char findKthBit(int n, int k) {
        int result = 0;
        int s_n_len = 1;
        for(int i = 1 ; i < n; i++){
            s_n_len = 2 * s_n_len + 1;
        }
        // std::cout << s_n_len << std::endl;
        bool isReverseCode = false;
        int reverseCnt = 0;
        while(s_n_len != 1){
            if(k == int(s_n_len / 2) + 1){
                result = 1;
                break;
            }else if (k < int(s_n_len / 2) + 1){
                s_n_len = (s_n_len - 1) / 2;
            }else{
                ++reverseCnt;
                k = s_n_len - k + 1;
                s_n_len = (s_n_len - 1) / 2;
            }
            // std::cout << s_n_len << " , " <<  k << " , " << reverseCnt << std::endl;
        }

        return '0' + ((result + reverseCnt) % 2);
    }
};
// @lc code=end

// int main(){
//     Solution s;
//     std::cout << s.findKthBit(3,2);
// }