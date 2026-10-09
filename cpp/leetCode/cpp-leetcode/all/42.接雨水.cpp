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
    // 笨方法，会超时
    int trap(vector<int>& height) {
        int ans = 0;
        int left, right = 0;
        int curDealHight = 0;
        while(true){
            left = right = 0;
            for(int i = 0; i < height.size(); ++i){
                if(height[i] > curDealHight){
                    left = i;
                    break;
                }
            }
            for(int i = height.size() - 1; i >= 0; --i){
                if(height[i] > curDealHight){
                    right = i;
                    break;
                }
            }
            if(left >= right){
                break;
            }
            for(int i = 0; i < height.size(); ++i){
                if(height[i] <= curDealHight && i > left && i < right){
                    ++ans;
                }
            }
            // std::cout << ans << "," << curDealHight << "," << left << "," << right << std::endl;
            ++curDealHight;
        }
        return ans;
    }
    
    //
    // int trap2(vector<int>& height){
    //     int ans = 0;
    //     int left = -1;
    //     for(int i = 0; i < height.size() - 2; ++i){
    //         if(height)
    //     }
    // }
};
// @lc code=end

int main(){
    std::vector<int> height {0,1,0,2,1,0,1,3,2,1,2,1};
    std::vector<int> height2 {4,2,0,3,2,5};
    Solution s;
    std::cout << "\n" << s.trap(height2);
}