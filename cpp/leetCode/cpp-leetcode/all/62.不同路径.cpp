/*
 * @lc app=leetcode.cn id=62 lang=cpp
 *
 * [62] 不同路径
 */

#include<iostream>
#include<vector>

using namespace std;

// @lc code=start
class Solution {
public:
    int uniquePaths(int m, int n) {
        vector<vector<int>> map (m, vector<int>(n, 0));
        for(int i = 0; i < m; i++) map[i][n-1] = 1;
        for(int i = 0; i < n; i++) map[m-1][i] = 1;

        for(int i = m - 2; i >= 0; i--){
            for(int j = n - 2; j >= 0; j--){
                map[i][j] = map[i+1][j] + map[i][j+1];
            }
        }

        return map[0][0];
    }
};
// @lc code=end

// class Solution {
// public:
//     int multiply(int A, int B) {
//         if(A == 1){
//             return B;
//         }
//         if(B == 1){
//             return A;
//         }
//         if(A > B){
//             return A + multiply(A, B-1);
//         }else{
//             return B + multiply(A-1,B);
//         }
//     }
// };

// int main(){
//     Solution s;
//     std::cout << s.uniquePaths(3,7);
// }