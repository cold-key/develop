/*
 * @lc app=leetcode.cn id=1493 lang=cpp
 *
 * [1493] 删掉一个元素以后全为 1 的最长子数组
 */

#include<iostream>
#include<vector>
#include<queue>

using namespace std;

// @lc code=start
class Solution {
public:
    int longestSubarray(vector<int>& nums) {
        int max = 0;
        queue<int> zeroIndexQueue;
        zeroIndexQueue.push(-1);
        for(int i = 0 ; i < nums.size(); i++){
            if(nums[i] == 0){
                if(zeroIndexQueue.size() < 2){
                    zeroIndexQueue.push(i);
                }
                else if(zeroIndexQueue.size() == 2){
                    zeroIndexQueue.push(i);
                    max = zeroIndexQueue.back() - zeroIndexQueue.front() - 2;
                }
                else{
                    zeroIndexQueue.pop();
                    zeroIndexQueue.push(i);
                    max  = max > zeroIndexQueue.back() - zeroIndexQueue.front() - 2 ? max : zeroIndexQueue.back() - zeroIndexQueue.front() - 2;
                }
                // std::cout << "i:" << i << " max:" << max << " leftIndex:" << zeroIndexQueue.front() << " rightIndex:" << zeroIndexQueue.back() << endl;
            }
        }
        zeroIndexQueue.pop();
        zeroIndexQueue.push(nums.size());
        max  = max > zeroIndexQueue.back() - zeroIndexQueue.front() - 2 ? max : zeroIndexQueue.back() - zeroIndexQueue.front() - 2;
        if(zeroIndexQueue.size() == 1){
            return nums.size() - 1;
        }
        if(zeroIndexQueue.size() != 3){
            return nums.size() - zeroIndexQueue.size() + 1;
        }
        return max;
    }
};
// @lc code=end

int main(){
    vector<int> test {0,1,1,1,0,1,1,0,1};
    Solution s;
    s.longestSubarray(test);
}