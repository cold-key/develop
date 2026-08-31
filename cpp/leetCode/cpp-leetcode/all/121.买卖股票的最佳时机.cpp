/*
 * @lc app=leetcode.cn id=121 lang=cpp
 *
 * [121] 买卖股票的最佳时机
 */

#include<vector>
#include<iostream>
// #include "lib/tool.h"

using namespace std;

// @lc code=start
class Solution {
public:
    int maxProfit(vector<int>& prices) {
        int minPrice = prices[0];
        int profit = 0;
        for(int i = 1; i < prices.size(); ++i){
            profit = std::max(profit,prices[i] - minPrice);
            minPrice = std::min(minPrice,prices[i]);
        }
        return profit;
    }
};
// @lc code=end

