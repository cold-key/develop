/*
 * @lc app=leetcode.cn id=1423 lang=cpp
 *
 * [1423] 可获得的最大点数
 */

#include<iostream>
#include<vector>

using namespace std;

// @lc code=start
class Solution {
public:
    int maxScore(vector<int>& cardPoints, int k) {
        int leftIndex = 0;
        int rightIndex = 0;
        int sum = 0;
        int temp = 0;
        for(int i = 0; i < cardPoints.size() && i < k; i++){
            sum += cardPoints[i];
        }
        rightIndex = k - 1;
        temp = sum;

        while(rightIndex >= 0){
            leftIndex--;
            if(leftIndex < 0){
                leftIndex = cardPoints.size()-1;
            }
            temp = (temp - cardPoints[rightIndex] + cardPoints[leftIndex]);
            sum = sum > temp ? sum : temp;
            std::cout << sum << endl;
            rightIndex--;
        }
        return sum;
    }
};
// @lc code=end

// int main(){
//     vector<int> test {1,2,3,4,5,6,1};
//     Solution s;
//     s.maxScore(test,3);
// }