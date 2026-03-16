/*
 * @lc app=leetcode.cn id=799 lang=cpp
 *
 * [799] 香槟塔
 */

// @lc code=start
class Solution {
public:
    double champagneTower(int poured, int query_row, int query_glass) {
        int remainingPoured = poured;
        double ans = 0;
        int i = 1;
        for(; remainingPoured > 0 ; i++){
            if(query_row == i){
                if(remainingPoured >= query_row){
                    ans = 1;
                    break;
                }else{
                    ans = (remainingPoured / (i - 1))/(query_glass == 1 || query_glass == i ? 2 : 1);
                    break;
                }
            }else{
                remainingPoured -= i;
            }
        }
        if(i < query_row){
            ans = 0;
        }
        return ans;
    }
};
// @lc code=end

