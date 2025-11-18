/*
 * @lc app=leetcode.cn id=2048 lang=cpp
 *
 * [2048] 下一个更大的数值平衡数
 */

#include<stdio.h>
#include<iostream>
#include<vector>
#include<unordered_set>
#include<cstdlib>
#include<float.h>

// @lc code=start
class Solution {
public:
    int nextBeautifulNumber(int n) {
        for(int i = n + 1; i < 10^6; i++){
            if(isBanlance(i)){
                return i;
            }
        }
        return n;
    }

    bool isBanlance(int n){
        std::vector<int> bucket(10);
        while(n >0){
            int f = n % 10;
            bucket[f]++;
            n = n / 10;
        }
        for(int i = 0; i < bucket.size(); i++){
            if(bucket[i] != i && bucket[i] != 0){
                return false;
            }
        }
        return true;
    }
};
// @lc code=end

// int main(){
//     Solution s;
//     std::cout << s.nextBeautifulNumber(1);
// }