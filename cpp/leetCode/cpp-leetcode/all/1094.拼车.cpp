/*
 * @lc app=leetcode.cn id=1094 lang=cpp
 *
 * [1094] 拼车
 */

#include<vector>
#include<iostream>

using namespace std;

// @lc code=start
class Solution {
public:
    bool carPooling(vector<vector<int>>& trips, int capacity) {
        vector<int> road (1010,0);
        int maxEdge = 0;
        int minEdge = 0;
        for(int i = 0; i < trips.size(); i++){
            road[trips[i][1]] += trips[i][0];
            road[trips[i][2]] -= trips[i][0];
            minEdge = minEdge < trips[i][1] ? minEdge : trips[i][1];
            maxEdge = maxEdge > trips[i][2] ? maxEdge : trips[i][2];
        }
        int curPassengers = 0;
        for(int i = minEdge; i <= maxEdge; i++){
            curPassengers += road[i];
            if(curPassengers > capacity){
                return false;
            }
        }
        return true;
    }
};
// @lc code=end

