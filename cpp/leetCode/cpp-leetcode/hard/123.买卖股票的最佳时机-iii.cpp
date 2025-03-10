/*
 * @lc app=leetcode.cn id=123 lang=cpp
 *
 * [123] 买卖股票的最佳时机 III
 */

// @lc code=start

#include <iostream>
#include <vector>
using namespace std;

class Solution {
public:
    // O(n2)
    int badMaxProfit(vector<int>& prices) {
        int maxProfit = 0;
        for(int i = 0; i < prices.size(); i++){
            vector<int> leftVector = vector<int>(prices.begin(),prices.begin()+i);
            vector<int> rightVector = vector<int>(prices.begin()+i,prices.end());

            int leftProfit = findMaxProfitInOneInterval(leftVector);
            int rightProfit = findMaxProfitInOneInterval(rightVector);
            if(leftProfit + rightProfit > maxProfit){
                maxProfit = leftProfit + rightProfit;
            }
            // cout << i << " " << leftProfit << " " << rightProfit << '\n';
        }
        return maxProfit;
        
    }

    int findMaxProfitInOneInterval(vector<int>& prices){
        int maxProfit = 0;
        int minPrice = 99999999;
        for(int i = 0; i < prices.size(); i++){
            int todayProfit = prices[i] - minPrice;
            if(todayProfit > maxProfit){
                maxProfit = todayProfit;
            }
            if(prices[i] < minPrice){
                minPrice = prices[i];
            }
        }

        return maxProfit;
    }

    // 对前一个算法的优化，典型的空间换时间，将所有中间结果进行存储
    int maxProfit(vector<int>& prices) {
        int maxProfit = 0;

        int rightMaxPrice = 0;
        int rightMaxLoss = -99999999;
        vector<int> toLeft(prices.size());
        for(int i = prices.size() - 1; i >= 0; i--){
            int tempMinLoss = prices[i] - rightMaxPrice;
            if(tempMinLoss < rightMaxLoss){
                tempMinLoss = rightMaxLoss;
            }
            toLeft[i] = tempMinLoss;
            if(prices[i] > rightMaxPrice){
                rightMaxPrice = prices[i];
            }
        }

        vector<int> toRight(prices.size());
        int leftMaxProfit = 0;
        int leftMinPrice = prices[0];
        for(int i = 0; i < prices.size(); i++){
            int tempMaxProfit = prices[i] - leftMinPrice;
            if(tempMaxProfit > leftMaxProfit){
                leftMaxProfit = tempMaxProfit;
            }
            toRight[i] = leftMaxProfit;
            if(prices[i] < leftMinPrice){
                leftMinPrice = prices[i];
            }
        }

        for(int i = 0; i < prices.size(); i++){
            // cout << toRight[i] ;
            // cout << toLeft[i] << '\n';
            if(toRight[i] - toLeft[i] > maxProfit){
                maxProfit = toRight[i] - toLeft[i];
            }
        }
        return maxProfit;
        
    }
};
// @lc code=end

// test code
int main(){
    vector<int> test {3,3,5,0,0,3,1,4};
    Solution s;
    int maxProfit = s.maxProfit(test);
    cout << maxProfit;
}