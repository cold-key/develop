/*
 * @lc app=leetcode.cn id=495 lang=cpp
 *
 * [495] 提莫攻击
 */

// @lc code=start
#include<vector>
using namespace std;
class Solution {
public:
    int findPoisonedDuration(vector<int>& timeSeries, int duration) {
        int allTime = 0;
        for(int i = 0; i < timeSeries.size()-1; i++){
            int j = i + 1;
            if(timeSeries[j] - timeSeries[i] > duration){
                allTime += duration;
            }else{
                allTime += timeSeries[j] - timeSeries[i];
            }
        }
        return allTime + duration;
    }
};
// @lc code=end

