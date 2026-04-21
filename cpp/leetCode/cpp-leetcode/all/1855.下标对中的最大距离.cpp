/*
 * @lc app=leetcode.cn id=1855 lang=cpp
 *
 * [1855] 下标对中的最大距离
 */

#include <vector>
#include <iostream>

using namespace std;

// @lc code=start
class Solution {
public:
    int maxDistance(vector<int>& nums1, vector<int>& nums2) {
        int ans = 0;
        int i = 0;
        for(int j = 0; j < nums2.size(); ++j){
            while(i < nums1.size() && nums1[i] > nums2[j]){
                ++i;
            }
            if(i >= nums1.size()){
                break;
            }
            ans = std::max(ans,j-i);
        }
        return ans;
    }
};
// @lc code=end

