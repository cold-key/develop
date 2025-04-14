/*
 * @lc app=leetcode.cn id=221 lang=cpp
 *
 * [221] 最大正方形
 */
#include<vector>
using namespace std;
// @lc code=start
class Solution {
public:
    int maximalSquare(vector<vector<char>>& matrix) {
        vector<vector<int>> dp;
        int maxL = 0;
        for(int i = 0; i < matrix.size();i++){
            vector<int> r ( matrix[i].size() ,  0);
            dp.push_back(r);
            for(int j = 0; j < matrix[i].size(); j++){
                if(i==0 || j == 0){
                    dp[i][j] = matrix[i][j] - '0';
                }else if(matrix[i][j] == '0'){
                    dp[i][j] = 0;
                }else{
                    dp[i][j] = minInThree(dp[i-1][j-1],dp[i][j-1],dp[i-1][j]) + 1;
                }
                maxL = maxL > dp[i][j] ? maxL :dp[i][j];
            }
        }
        return maxL * maxL;
    }

    int minInThree(int a ,int b, int c){
        int min  = a < b ? a :b;
        return min < c ? min : c;
    }
};
// @lc code=end

