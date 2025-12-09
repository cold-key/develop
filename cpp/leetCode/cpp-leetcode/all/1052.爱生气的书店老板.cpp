/*
 * @lc app=leetcode.cn id=1052 lang=cpp
 *
 * [1052] 爱生气的书店老板
 */

#include<iostream>
#include<vector>

using namespace std;

// @lc code=start
class Solution {
public:
    int maxSatisfied(vector<int>& customers, vector<int>& grumpy, int minutes) {
        int minC = 0;
        int tempC = 0;
        int minLeftIndex = 0;
        int minRightIndex = 0;
        int leftIndex = 0;
        for(int i = 0; i < customers.size(); i++){
            if(i - leftIndex <= minutes - 1){
                minC += customers[i] * grumpy[i] * -1;
                tempC = minC;
                minRightIndex = i;
            }else{
                tempC = tempC + (customers[i] * grumpy[i] * -1) - (customers[leftIndex] * grumpy[leftIndex] * -1);
                if(tempC < minC){
                    minC = tempC;
                    minLeftIndex = leftIndex + 1;
                    minRightIndex = i;
                }
                leftIndex++;
            }
        }

        int result = 0;
        for(int i = 0; i < customers.size(); i++){
            if(i >= minLeftIndex && i <= minRightIndex){
                result += customers[i];
            }else{
                result += customers[i] * ((grumpy[i] + 1) % 2);
            }
        }

        return result;

    }
};
// @lc code=end

