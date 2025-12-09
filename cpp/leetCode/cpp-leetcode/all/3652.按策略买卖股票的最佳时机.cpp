/*
 * @lc app=leetcode.cn id=3652 lang=cpp
 *
 * [3652] 按策略买卖股票的最佳时机
 */

#include<iostream>
#include<vector>

using namespace std;

// @lc code=start
class Solution {
public:
    long long maxProfit(vector<int>& prices, vector<int>& strategy, int k) {
        int leftIndex = 0;
        long maxAddProfit = 0;
        long tempAddProfit = 0;
        long originProfit = 0;
        for(int i = 0; i < k && i < prices.size(); i++){
            if(i < k /2){
                maxAddProfit += (0 - strategy[i]) * prices[i];
            }else{
                maxAddProfit += (1 - strategy[i]) * prices[i];
            }

            originProfit += prices[i] * strategy[i];
        }
        tempAddProfit = maxAddProfit;
        // std::cout << tempAddProfit << ",";

        for(int i = k; i < prices.size(); i++){
            tempAddProfit += (1 - strategy[i]) * prices[i]
             - (1 - strategy[leftIndex + k/2]) * prices[leftIndex + k/2]
             + (0 - strategy[leftIndex + k/2]) * prices[leftIndex + k/2]
             - (0 - strategy[leftIndex]) * prices[leftIndex];
            // std::cout << tempAddProfit << ",";
            maxAddProfit = maxAddProfit > tempAddProfit ? maxAddProfit : tempAddProfit;
            leftIndex++;

            originProfit += prices[i] * strategy[i];
        }

        maxAddProfit = maxAddProfit > 0 ? maxAddProfit : 0;

        return originProfit + maxAddProfit;
    }
};
// @lc code=end

// int main(){
//     std::vector<int> prices {5,14,16,9};
//     std::vector<int> strategy {-1,0,0,-1};
//     int k = 2;
//     Solution s;
//     int result = s.maxProfit(prices, strategy, k);
//     std::cout << "\nresult:" <<  result;
// }