/*
 * @lc app=leetcode.cn id=1016 lang=cpp
 *
 * [1016] 子串能表示从 1 到 N 数字的二进制串
 */

#include<string>
#include <bit>
#include<iostream>
#include<unordered_set>
#include "lib/tool.h"

using namespace std;

// @lc code=start
class Solution {
public:
    bool queryString(string s, int n) {
        int max_width = std::bit_width((unsigned int)n);
        std::unordered_set<int> set;
        for(int w = 1; w <= max_width; w++){
            int temp = 0;
            int rightIndex = 0;
            while(rightIndex < s.size()){
                int leftIndex = rightIndex - w + 1;
                if(leftIndex < 0){
                    temp = (temp << 1) + (s[rightIndex] - '0');
                }else{
                    temp = (temp << 1) + (s[rightIndex] - '0');
                    if(temp <= n && temp > 0) set.insert(temp);
                    temp -= (s[leftIndex] - '0') * (1<<(w-1));
                }
                ++rightIndex;
            }
            // printUnorderedSet(set);
            if(w < max_width){
                if (set.size() != ((1 << w) - 1) ) return false;
            }
        }
        return set.size() == n;
    }
};
// @lc code=end

// int main(){
//     Solution s;
//     std::cout << s.queryString("1111000101",5);
// }