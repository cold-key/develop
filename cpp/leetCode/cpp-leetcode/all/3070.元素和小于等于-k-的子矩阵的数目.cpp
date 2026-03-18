/*
 * @lc app=leetcode.cn id=3070 lang=cpp
 *
 * [3070] 元素和小于等于 k 的子矩阵的数目
 */

#include<vector>
#include<iostream>

using namespace std;

// @lc code=start
class Solution {
public:
    int countSubmatrices(vector<vector<int>>& grid, int k) {
        int ans = 0;
        int max_i = grid.size() - 1;
        int max_j = grid[0].size() - 1;
        int sum = 0;
        for(int i = 0; i <= max_i; i++){
            sum+=grid[i][0];
            if(sum <= k){
                ++ans;
            }else{
                max_i = std::max(i - 1,0);
                break;
            }
        }
        std::cout << "first ans:" << ans << std::endl;
        sum = 0;
        for(int j = 0; j <= max_j; j++){
            sum+=grid[0][j];
            if(sum <= k){
                ++ans;
            }else{
                sum-=grid[0][j];
                max_j = std::max(j - 1,0);
                break;
            }
        }
        std::cout << "first ans:" << ans << std::endl;
        --ans;
        std::cout << "first ans:" << ans << std::endl;

        std::cout << max_i << " , " << max_j << std::endl;
        std::cout << sum << std::endl;
        for(int i = 1; i <= max_i; i++){
            if(max_j <= 0){
                break;
            }
            int cur_i_sum = 0;
            for(int j = 0; j <= max_j;j++){
                cur_i_sum += grid[i][j];
            }
            while(sum + cur_i_sum > k){
                // sum -= grid[i-1][max_j];
                for(int k = 0; k <= i-1;k++){
                    sum -= grid[k][max_j];
                }
                cur_i_sum -= grid[i][max_j];
                --max_j;
            }
            if(max_j <= 0){
                break;
            }
            sum = sum + cur_i_sum;
            ans += max_j;
        }
        return std::max(ans,0);
    }
};
// @lc code=end

// int main(){
//     vector<vector<int>> grid {{5,2,9,5},{1,10,2,9},{3,5,9,7},{5,2,6,3},{3,10,2,5}};
//     Solution s;
//     std::cout << s.countSubmatrices(grid,8);
// }

// 暴力法，O(1)空间，后续优化可考虑空间换时间