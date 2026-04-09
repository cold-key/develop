/*
 * @lc app=leetcode.cn id=122 lang=cpp
 *
 * [122] 买卖股票的最佳时机 II
 */

#include<vector>
#include<iostream>

using namespace std;

// @lc code=start
class Solution {
public:
    int maxProfit(vector<int>& prices) {
        // return greedyMaxProfit(prices);
        return dpMaxProfit(prices);
    }

    // 贪心法
    int greedyMaxProfit(vector<int>& prices) {
        int ans = 0;
        for(int i = 1; i < prices.size(); ++i){
            ans += std::max(0,prices[i] - prices[i-1]);
        }
        return ans;
    }

    // 动态规划法
    int dpMaxProfit(vector<int>& prices) {
        int frontHaveProfit = -prices[0];
        int frontNoHaveProfit = 0;
        for(int i = 1; i < prices.size(); ++i){
            int curHaveProfit = std::max(frontHaveProfit,frontNoHaveProfit - prices[i]);
            int curNoHaveProfit = std::max(frontNoHaveProfit,frontHaveProfit + prices[i]);
            frontHaveProfit = curHaveProfit;
            frontNoHaveProfit = curNoHaveProfit;
        }
        return frontNoHaveProfit;
    }

};
// @lc code=end

int main(){
    Solution solution;
    std::vector<int> prices = {7,1,5,3,6,4};
    int result = solution.maxProfit(prices);
    std::cout << "result: " << result << std::endl;
    return 0;
}