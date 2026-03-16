/*
 * @lc app=leetcode.cn id=799 lang=cpp
 *
 * [799] 香槟塔
 */

 #include<iostream>
 #include<queue>

// @lc code=start
class Solution {
public:
    double champagneTower(int poured, int query_row, int query_glass) {
        double remainingPoured = poured;
        double ans = 0;
        int i = 0;
        for(; remainingPoured > 0 ; i++){
            // std::cout << i << " , " << remainingPoured << std::endl;
            if(query_row == i){
                if(remainingPoured >= query_row + 1){
                    ans = 1;
                    break;
                }else{
                    int tmp_i = i;
                    int tmp_j = query_glass;
                    std::queue<std::pair<int, int>> q;
                    q.push({tmp_i, tmp_j});
                    while(!q.empty()){
                        auto [cur_i, cur_j] = q.front();
                        q.pop();
                        if(cur_i == 0 || cur_j == 0 || cur_j == cur_i){
                            std::cout << cur_i << " , " << cur_j << " : " << remainingPoured/(1<<cur_i)/(1<<(tmp_i - cur_i + 1)) << std::endl;
                            ans += remainingPoured/(1<<cur_i)/(1<<(tmp_i - cur_i));
                            continue;
                        }
                        if(cur_j > 0){
                            q.push({cur_i - 1, cur_j - 1});
                        }
                        if(cur_j < cur_i){
                            q.push({cur_i - 1, cur_j});
                        }
                    }
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