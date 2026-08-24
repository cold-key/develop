/*
 * @lc app=leetcode.cn id=88 lang=cpp
 *
 * [88] 合并两个有序数组
 */

#include<iostream>
#include<vector>

using namespace std;

// @lc code=start
class Solution {
public:
    void merge(vector<int>& nums1, int m, vector<int>& nums2, int n) {
        for(int i = m-1; i >= 0; --i){
            nums1[i+n] = nums1[i];
        }
        int i = n;
        int j = 0;
        int k = 0;
        while(i < nums1.size() && j < nums2.size()){
            if(nums1[i] < nums2[j]){
                nums1[k++] = nums1[i++];
            }else{
                nums1[k++] = nums2[j++];
            }
        }
        while(j < nums2.size()){
            nums1[k++] = nums2[j++];
        }
    }
};
// @lc code=end

int main(){
    std::vector nums1 {1,3,5,7,9,0,0,0,0,0,0,0};
    std::vector nums2 {2,4,6,8,10,10,11};
    Solution s;
    s.merge(nums1,5,nums2,7);

    for(auto v : nums1){
        std::cout << v << " , ";
    }
}