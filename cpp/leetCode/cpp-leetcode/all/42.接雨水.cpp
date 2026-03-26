/*
 * @lc app=leetcode.cn id=42 lang=cpp
 *
 * [42] 接雨水
 */

#include<iostream>
#include<vector>

using namespace std;

// @lc code=start
class Solution {
public:
    int trap(vector<int>& height) {
        int ans = 0;
        int left = 0;
        int right = left + 1;
        int curAddValue = 0;
        while(right < height.size()){
            std::cout << curAddValue << " , ";
            if(height[right] < height[left]){
                curAddValue += height[left] - height[right];
                ++right;
            }else{
                ans += std::max(curAddValue,0);
                curAddValue = 0;
                left = right;
                ++right;
            }
        }
        return ans;
    }
};
// @lc code=end

int main(){
    std::vector<int> height {0,1,0,2,1,0,1,3,2,1,2,1};
    Solution s;
    s.trap(height);
}