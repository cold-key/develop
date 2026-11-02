/*
 * @lc app=leetcode.cn id=134 lang=cpp
 *
 * [134] 加油站
 */

#include <vector>
#include <iostream>

using namespace std;

// @lc code=start
class Solution {
public:
    // int canCompleteCircuit(vector<int>& gas, vector<int>& cost) {
    //     int ans = 0;
    //     while(ans < gas.size()){
    //         int cacheAns = ans;
    //         int i = ans;
    //         int cnt = 0;
    //         int sum = 0;
    //         while(cnt < gas.size()){
    //             sum += gas[i] - cost[i];
    //             if(sum < 0){
    //                 break;
    //             }
    //             ++i;
    //             i %= gas.size();
    //             ++cnt;
    //         }
    //         if(cnt == gas.size()){
    //             return ans;
    //         }else{
    //             ans = i + 1;
    //         }
    //         if(ans <= cacheAns) return -1;
    //     }
    //     return -1;
    // }

    int canCompleteCircuit(vector<int>& gas, vector<int>& cost){
      int total = 0;
      int current = 0;
      int start = 0;

      for (int i = 0; i < gas.size(); ++i) {
          int diff = gas[i] - cost[i];

          total += diff;
          current += diff;

          if (current < 0) {
              start = i + 1;
              current = 0;
          }
      }

      return total >= 0 ? start : -1;
    }
};
// @lc code=end

int main(){
    Solution s;
    vector<int> gas = {1,2,3,4,5};
    vector<int> cost = {3,4,5,1,2};
    cout << s.canCompleteCircuit(gas,cost) << endl;
}
