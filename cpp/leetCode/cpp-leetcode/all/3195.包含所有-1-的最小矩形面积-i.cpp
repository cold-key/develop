/*
 * @lc app=leetcode.cn id=3195 lang=cpp
 *
 * [3195] 包含所有 1 的最小矩形面积 I
 */

#include<stdio.h>
#include<iostream>
#include<vector>

using namespace std;

// @lc code=start
class Solution {
public:
    int minimumArea(vector<vector<int>>& grid) {
        int minX = grid[0].size();
        int maxX = 0;
        int minY = grid.size();
        int maxY = 0;

        for(int i = 0; i < grid.size(); i++){
            for(int j = 0; j < grid[i].size(); j++){
                if(grid[i][j] == 1){
                    minX = minX < j ? minX : j;
                    maxX = maxX > j ? maxX : j;
                    minY = minY < i ? minY : i;
                    maxY = maxY > i ? maxY : i;
                }
            }
        }
        return (maxX - minX + 1) * (maxY - minY + 1);
    }
};
// @lc code=end

