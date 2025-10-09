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
    int candy(vector<int>& ratings) {
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
};
// @lc code=end


// TEST CODE
int main(){
    vector<int> test {1,2,3,1,0};
    Solution s;
    s.candy(test);
    return 0;
}