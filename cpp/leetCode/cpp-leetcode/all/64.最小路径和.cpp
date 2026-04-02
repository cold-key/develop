/*
 * @lc app=leetcode.cn id=64 lang=cpp
 *
 * [64] 最小路径和
 */

#include<vector>
#include<iostream>
#include<limits>

using namespace std;

// @lc code=start
class Solution {
public:
    int minPathSum(vector<vector<int>>& grid) {
        constexpr int MAX_VAL = std::numeric_limits<int>::max();
        std::vector<std::vector<int>> minVec (grid.size(), std::vector<int>(grid[0].size(), 0));
        minVec[0][0] = grid[0][0];
        for(int i = 0; i < grid.size(); ++i){
            for(int j = 0; j < grid[i].size(); ++j){
                if(i == 0 && j == 0) continue;
                int topMinVal = i - 1 >= 0 ? minVec[i-1][j] : MAX_VAL;
                int leftMinVal = j - 1 >= 0 ? minVec[i][j-1] : MAX_VAL;
                minVec[i][j] =  grid[i][j] + std::min(topMinVal,leftMinVal);
            }
        }
        std::cout << "minVec : " << std::endl;
        for (const auto& row : minVec) {
            for (const auto& val : row) {
                std::cout << val << " ";
            }
            std::cout << std::endl;
        }
        return minVec[minVec.size() - 1][minVec[0].size() - 1];
    }
};
// @lc code=end

// int main(){
//     Solution sol;
//     vector<vector<int>> grid = {{100,100,100,100}};
//     int result = sol.minPathSum(grid);
//     std::cout << "result : " << result << std::endl;
//     return 0;
// }