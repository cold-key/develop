/*
 * @lc app=leetcode.cn id=799 lang=cpp
 *
 * [799] 香槟塔
 */

 #include<iostream>

// @lc code=start
class Solution {
public:
    double champagneTower(int poured, int query_row, int query_glass) {
        double remainingPoured = poured;
        double ans = 0;
        int i = 0;
        for(; remainingPoured > 0 ; i++){
            std::cout << i << " , " << remainingPoured << std::endl;
            if(query_row == i){
                if(remainingPoured >= query_row + 1){
                    ans = 1;
                    break;
                }else{
                    int tmp_i = i;
                    // while()
                    break;
                }
            }else{
                remainingPoured -= (i+1);
            }
        }
        if(i < query_row){
            ans = 0;
        }
        return ans;
    }
};
// @lc code=end

int main(){
    Solution s;
    std::cout << s.champagneTower(25,6,1);
    return 0;
}