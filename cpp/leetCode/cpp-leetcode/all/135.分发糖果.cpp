/*
 * @lc app=leetcode.cn id=135 lang=cpp
 *
 * [135] 分发糖果
 */

#include<stdio.h>
#include<iostream>
#include<vector>

using namespace std;

// @lc code=start
class Solution {
public:
    // 最坏时间复杂度为n方，空间为n
    int candy(vector<int>& ratings) {
        return candy_n_1(ratings);
        vector<int> candyNum (ratings.size(),0);
        candyNum[0] = 1;
        for(int i = 1; i < ratings.size(); i++){
            if(ratings[i] > ratings[i - 1]){
                candyNum[i] = candyNum[i - 1] + 1;
            }else if(ratings[i] == ratings[i - 1]){
                candyNum[i] = 1;
            }else{
                if(candyNum[i - 1] == 1){
                    candyNum[i] = 1;
                    candyNum[i-1]++;
                    for(int j = i - 2; j >= 0; j--){
                        if(ratings[j] > ratings[j+1] && candyNum[j] <= candyNum[j+1]){
                            candyNum[j]++;
                        }else{
                            break;
                        }
                    }
                }else{
                    candyNum[i] = 1;
                }
            }
        }

        int total = 0;
        for(int i = 0; i < candyNum.size();i++){
            cout << candyNum[i] << ",";
            total += candyNum[i];
        }
        return total;
    }

    // 时间复杂度 n ，空间复杂度 1 的做法
    int candy_n_n(vector<int>& ratings){
        std::vector<int> candyNum(ratings.size(),1);
        for(int i = 1; i < ratings.size(); ++i){
            if(ratings[i] > ratings[i - 1]){
                candyNum[i] = candyNum[i - 1] + 1;
            }
        }
        for(int i = ratings.size() - 2; i >= 0; --i){
            if(ratings[i] > ratings[i + 1]){
                candyNum[i] = std::max(candyNum[i],candyNum[i + 1] + 1);
            }
        }
        int result = 0;
        for(auto v : candyNum){
            result += v;
        }
        return result;
    }

    int candy_n_1(vector<int>& ratings){
        int ans = ratings.size();
        int up = 0;
        int down = 0;
        int peak = 0;
        for(int i = 1; i < ratings.size(); ++i){
            if(ratings[i] > ratings[i-1]){
                ++up;
                ans += up;
                down = 0;
                peak = up;
            }else if(ratings[i] == ratings[i-1]){
                up = down = peak = 0;
            }else{
                up = 0;
                ++down;
                ans += down;
                if(down <= peak){
                    --ans;
                }
            }
        }
        return ans;
    }
};
// @lc code=end


// TEST CODE
int main(){
    vector<int> test {1,2,3,1,0};
    Solution s;
    s.candy(test);
    return 0;
}