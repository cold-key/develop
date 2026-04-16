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
    int canCompleteCircuit(vector<int>& gas, vector<int>& cost) {
        int ans = 0;
        while(ans < gas.size()){
            int cacheAns = ans;
            int i = ans;
            int cnt = 0;
            int sum = 0;
            while(cnt < gas.size()){
                sum += gas[i] - cost[i];
                if(sum < 0){
                    break;
                }
                ++i;
                i %= gas.size();
                ++cnt;
            }
            if(cnt == gas.size()){
                return ans;
            }else{
                ans = i + 1;
            }
            if(ans <= cacheAns) return -1;
        }
        return -1;
    }
};
// @lc code=end

int main(){
    Solution s;
    vector<int> gas = {1,1,1,1,1,1,1,1};
    vector<int> cost = {1,1,1,1,1,1,1,1};
    cout << s.canCompleteCircuit(gas,cost) << endl;
}