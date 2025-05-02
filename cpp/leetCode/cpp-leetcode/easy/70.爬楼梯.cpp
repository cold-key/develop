/*
 * @lc app=leetcode.cn id=70 lang=cpp
 *
 * [70] 爬楼梯
 */
#include<vector>
using namespace std;
// @lc code=start
class Solution {
public:
    int climbStairs(int n) {
        int vectorSize = (n+1)>=4?(n+1):4;
        vector<int> step (vectorSize,0);
        step[0] = 0;
        step[1] = 1;
        step[2] = 2;
        step[3] = 3;
        for(int i = 4; i <= n; i++){
            step[i] = step[i-1] +step[i-2];
        }
        return step[n];
    }
};
// @lc code=end

