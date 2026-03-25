/*
 * @lc app=leetcode.cn id=2105 lang=cpp
 *
 * [2105] 给植物浇水 II
 */

#include<vector>
#include<iostream>

using namespace std;

// @lc code=start
class Solution {
public:
    int minimumRefill(vector<int>& plants, int capacityA, int capacityB) {
        int ans = 0;
        int left = 0;
        int right = plants.size() - 1;
        int leftCapacity = capacityA;
        int rightCapacity = capacityB;
        while(left <= right){
            if(left == right){
                int maxCapacity = std::max(leftCapacity,rightCapacity);
                if(maxCapacity < plants[left]){
                    ++ans;
                }
                break;
            }
            if(leftCapacity < plants[left]){
                ++ans;
                leftCapacity = capacityA - plants[left];
            }else{
                leftCapacity -= plants[left];
            }

            if(rightCapacity < plants[right]){
                ++ans;
                rightCapacity = capacityB - plants[right];
            }else{
                rightCapacity -= plants[right];
            }

            ++left;
            --right;
        }
        return ans;
    }
};
// @lc code=end

