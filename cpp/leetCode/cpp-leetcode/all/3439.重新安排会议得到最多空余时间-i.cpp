/*
 * @lc app=leetcode.cn id=3439 lang=cpp
 *
 * [3439] 重新安排会议得到最多空余时间 I
 */

#include<iostream>
#include<vector>

using namespace std;

// @lc code=start
class Solution {
public:
    int maxFreeTime(int eventTime, int k, vector<int>& startTime, vector<int>& endTime) {
        int left = 0;
        vector<int> free;
        for(int i = 0; i < startTime.size(); i++){
            free.push_back(startTime[i] - left);
            left = endTime[i];
        }
        free.push_back(eventTime - left);
        // test
        // for(auto v : free){
        //     std::cout << v << ",";
        // }
        //
        k = k + 1;
        int leftIndex = 0;
        int maxFree = 0;
        int tempFree = 0;
        for(int i = 0; i < free.size(); i++){
            if(i - leftIndex <= k - 1){
                maxFree += free[i];
                tempFree = maxFree;
            }else{
                tempFree = tempFree + free[i] - free[leftIndex];
                maxFree = maxFree > tempFree ? maxFree : tempFree;
                leftIndex++;
            }
        }
        return maxFree;
    }
};
// @lc code=end

// int main(){
//     int eventTime = 99;
//     int k = 1;
//     std::vector<int> startTime {7,21,25};
//     std::vector<int> endTime {13,25,78};
//     Solution s;
//     std::cout << s.maxFreeTime(eventTime, k, startTime, endTime);
// }