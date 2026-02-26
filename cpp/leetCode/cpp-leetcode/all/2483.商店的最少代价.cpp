/*
 * @lc app=leetcode.cn id=2483 lang=cpp
 *
 * [2483] 商店的最少代价
 */

#include<iostream>
#include<string>

using namespace std;

// @lc code=start
class Solution {
public:
    int bestClosingTime(string customers) {
        int minCost = customers.size();
        int curCost = 0;
        int result = 0;
        for(int i = 0; i < customers.size(); i++){
            if(customers[i] == 'N'){
                ++curCost;
            }
        }
        result = customers.size();
        minCost = curCost;
        for(int i = customers.size() - 1; i >= 0; i--){
            if(customers[i] == 'N'){
                --curCost;
            }else{
                ++curCost;
            }
            if(curCost <= minCost){
                minCost = curCost;
                result = i;
            }
        }
        return result;
    }
};
// @lc code=end

