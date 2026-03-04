/*
 * @lc app=leetcode.cn id=1536 lang=cpp
 *
 * [1536] 排布二进制网格的最少交换次数
 */

#include<iostream>
#include<vector>
#include<algorithm>

// #include"lib/tool.h"

using namespace std;

// @lc code=start
class Solution {
public:
    int minSwaps(vector<vector<int>>& grid) {
        vector<int> tailZeroVector (grid.size(),0);
        for(int i = 0; i < grid.size(); i++){
            int zeroCnt = 0;
            for(int j = 0; j < grid[i].size(); j++){
                if(grid[i][j] == 0){
                    ++zeroCnt;
                }else{
                    zeroCnt = 0;
                }
            }
            tailZeroVector[i] = zeroCnt;
        }
        int colNum = tailZeroVector.size();
        int swapCnt = 0;
        // printVector(tailZeroVector);
        for(int i = 0; i < tailZeroVector.size(); i++){
            int cache = tailZeroVector[i];
            bool isSwap = false;
            for(int j = i; j < tailZeroVector.size(); j++){
                if(tailZeroVector[j] >= colNum - i - 1){
                    isSwap = true;
                    swapCnt += j - i;
                    tailZeroVector[i] = tailZeroVector[j];
                    tailZeroVector[j] = cache;
                    break;
                }else{
                    int temp = tailZeroVector[j];
                    if(j - 1 >= i){
                        tailZeroVector[j] = cache;
                    }
                    cache = temp;
                }
            }
            if(!isSwap){
                return -1;
            }
            // std::cout << swapCnt << std::endl;
            // printVector(tailZeroVector);
        }
        return swapCnt;
    }
};
// @lc code=end

// int main(){
//     vector<vector<int>> gird {{1,0,0},{1,1,0},{1,1,1}};
//     Solution s;
//     std::cout << s.minSwaps(gird);
// }