/*
 * @lc app=leetcode.cn id=1582 lang=cpp
 *
 * [1582] 二进制矩阵中的特殊位置
 */
#include"lib/tool.h"
using namespace std;

// @lc code=start
class Solution {
public:
    int numSpecial(vector<vector<int>>& mat) {
        vector<int> rowValue (mat.size(),0);
        vector<int> colValue (mat[0].size(),0);
        for(int i = 0; i < mat.size(); i++){
            for(int j = 0; j < mat[i].size(); j++){
                rowValue[i] += mat[i][j];
                colValue[j] += mat[i][j];
            }
        }

        int cnt = 0;
        for(int i = 0; i < mat.size(); i++){
            for(int j = 0; j < mat[i].size(); j++){
                if(mat[i][j] == 1 && rowValue[i] == 1 && colValue[j] == 1){
                    ++cnt;
                }
            }
        }

        return cnt;
    }
};
// @lc code=end

