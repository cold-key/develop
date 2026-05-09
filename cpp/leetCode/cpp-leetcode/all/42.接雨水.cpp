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
        return ans;
    }
};
// @lc code=end

int main(){
    std::vector<int> height {0,1,0,2,1,0,1,3,2,1,2,1};
    Solution s;
    std::cout << "\n" << s.trap(height);
}