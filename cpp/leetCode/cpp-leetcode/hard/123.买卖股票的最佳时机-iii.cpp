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
    int maxProfit(vector<int>& prices) {
        int maxProfit = 0;
        for(int i = 0; i < prices.size(); i++){
            vector<int> leftVector = vector<int>(prices.begin(),prices.begin()+i);
            vector<int> rightVector = vector<int>(prices.begin()+i,prices.end());

            int leftProfit = findMaxProfitInOneInterval(leftVector);
            int rightProfit = findMaxProfitInOneInterval(rightVector);
            if(leftProfit + rightProfit > maxProfit){
                maxProfit = leftProfit + rightProfit;
            }
            cout << i << " " << leftProfit << " " << rightProfit << '\n';
        }
        return maxProfit;
        
    }

    int findMaxProfitInOneInterval(vector<int>& prices){
        int maxProfit = 0;
        for(int i = 1; i < prices.size(); i++){
            
        }

        return maxProfit;
    }
};
// @lc code=end

// test code
int main(){
    vector<int> test {3,3,5,0,0,3,1,4};
    Solution s;
    s.maxProfit(test);
}