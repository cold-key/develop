/*
 * @lc app=leetcode.cn id=1848 lang=cpp
 *
 * [1848] 到目标元素的最小距离
 */

#include<vector>
#include<cmath>
#include<iostream>

using namespace std;

// @lc code=start
class Solution {
public:
    int getMinDistance(vector<int>& nums, int target, int start) {
        if(nums[start] == target){
            return 0;
        }
        int ans = 0;
        for(int i = 1;;++i){
            int right = start + i;
            int left = start - i;
            if(left >= 0 && nums[left] == target){
                ans = abs(start - left);
                break;
            }
            if(right < nums.size() && nums[right] == target){
                ans = abs(start - right);
                break;
            }
        }
        return ans;
    }
};
// @lc code=end

int main(){
    Solution s;
    vector<int> nums = {1,2,3,4,5};
    int target = 5;
    int start = 3;
    cout << s.getMinDistance(nums, target, start) << endl;
    return 0;
}