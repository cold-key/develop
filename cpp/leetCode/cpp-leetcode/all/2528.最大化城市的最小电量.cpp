/*
 * @lc app=leetcode.cn id=2528 lang=cpp
 *
 * [2528] 最大化城市的最小电量
 */

#include<iostream>
#include<vector>

using namespace std;

// @lc code=start
class Solution {
public:
    long long maxPower(vector<int>& stations, int r, int k) {
        int sum = 0;
        int front = -1;
        int minIndex = 0;
        vector<int> e (stations.size(),0);
        for(int i = 0; i <= r && i < stations.size(); i++){
            e[0] += stations[i];
        }
        for(int i = 1; i < stations.size(); i++){
            int left = i - r;
            int right = i + r;
            int leftValue = left >= 0 ? stations[left] : 0;
            int rightValue = right < stations.size() ? stations[right] : 0;
            e[i] = e[i - 1] -leftValue + rightValue;

            if(e[minIndex] > e[i]){
                minIndex = i;
            }
        }
        for(int i = 0 ; i < k; i++){
            for(int j = minIndex; j <= minIndex + 2 * r && j < e.size(); j++){
                e[j]++;
            }
            minIndex = 0;
            for(int j = 0; j < e.size(); j++){
                if(e[minIndex] > e[j]){
                    minIndex = j;
                }
            }
        }
        return e[minIndex];
    }
};
// @lc code=end


// 解题思路，根据滑动窗口很好求给定数组的最低电量，但在数组上直接贪心却不好求，因为此时局部最优不一定全局最优
// 换个思路，对于给定的r，k，我们要求解的最小电量Xmin <= Xk <= XMax，
// 所以此时可以将问题转化为，对于给定的r，k，station，是否存在一个解使得Xmin >= Xi
// 求解的方法也比较简单，即遍历初始电量，当电量小于Xi时，在i+r处加一个充电桩即可，
// 我们不需要从Xmin遍历到Xmax，记bool check(x)为对于给定r，k，是否存在解 > x ,
// 当check(Xi) == true，时 check(Xmin ... Xi) == true，具有单调性，所以可以用二分
// 考虑使用前缀和，当r >= station.size()，滑动窗口退化
