/*
 * @lc app=leetcode.cn id=1277 lang=cpp
 *
 * [1277] 统计全为 1 的正方形子矩阵
 */

#include<stdio.h>
#include<iostream>
#include<vector>

using namespace std;

// @lc code=start
class Solution {
public:
    int countSquares(vector<vector<int>>& matrix) {
        vector<vector<int>> result(matrix.size(),vector<int>(matrix[0].size(), 0));
        result[0][0] = matrix[0][0];
        for(int j = 1; j < matrix[0].size();j++){
            result[0][j] = result[0][j - 1] + matrix[0][j];
        }
        for(int i = 1; i < matrix.size(); i++){
            vector<int> posMaxRect (matrix[i].size(),0);
            for(int j = 0; j < matrix[i].size(); j++){
                // cout << "j : " << j << endl;
                if(j == 0){
                    result[i][j] = matrix[i][j] + result[i - 1][matrix[i].size() - 1];
                    posMaxRect[j] = matrix[i][j];
                }else{
                    if(posMaxRect[j - 1] == 0){
                        posMaxRect[j] = matrix[i][j];
                        result[i][j] = result[i][j-1] + matrix[i][j];
                    }else{
                        int k = 0;
                        for(; k < posMaxRect[j - 1]; k++){
                            // cout << "Test 001" << endl;
                            if(matrix[i - k][j] != 1){
                                result[i][j] = result[i][j-1] + k;
                                posMaxRect[j] = k;
                                break;
                            }
                        }
                        if (k == posMaxRect[j - 1]){
                            // cout << "Test 002" << endl;
                            if ((i - posMaxRect[j - 1]) < 0){
                                result[i][j] = result[i][j-1] + posMaxRect[j - 1];
                                posMaxRect[j] = posMaxRect[j - 1];
                            }else{
                                int l = j;
                                for(; l >= j - posMaxRect[j - 1]; l--){
                                    // cout << "Test 003" << endl;
                                    // cout << i << "," << posMaxRect[j - 1] << endl;
                                    // cout << i - posMaxRect[j - 1] << "," << l << endl;
                                    // cout << matrix[i - posMaxRect[j - 1]][l] << endl;
                                    // cout << i << "," << j << endl;
                                    if(matrix[i - posMaxRect[j - 1]][l] != 1){
                                        result[i][j] = result[i][j-1] + k;
                                        posMaxRect[j] = k;
                                        break;
                                    }
                                    // cout << "Test 004" << endl;
                                }
                                if(l == j - posMaxRect[j - 1] - 1){
                                    result[i][j] = result[i][j-1] + posMaxRect[j - 1] + 1;
                                    posMaxRect[j] = posMaxRect[j - 1] + 1;
                                }
                            }
                        }
                    }
                }
            }
            // for(int x = 0; x < posMaxRect.size(); x++){
            //     cout << posMaxRect[x] << ",";
            // }
            // cout << endl;
        }

        // cout << "----------------" << endl;
        // for(int i = 0; i < result.size();i++){
        //     for(int j = 0; j < result[i].size();j++){
        //         cout << result[i][j] << " ,";
        //     }
        //     cout << endl;
        // }
        return result[matrix.size() - 1][matrix[0].size() - 1];
    }
};
// @lc code=end

// test code
// int main(){
//     std::vector<std::vector<int>> vec = {
//         {0,1,1,1},
//         {1,1,1,1},
//         {0,1,1,1}
//     };
//     Solution s;
//     int r = s.countSquares(vec);
//     cout << r << endl;
// }