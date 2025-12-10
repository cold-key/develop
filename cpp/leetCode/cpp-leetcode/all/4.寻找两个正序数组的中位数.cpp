/*
 * @lc app=leetcode.cn id=4 lang=cpp
 *
 * [4] 寻找两个正序数组的中位数
 */
#include<iostream>
#include<vector>

using namespace std;

// @lc code=start
class Solution {
public:
    double findMedianSortedArrays(vector<int>& nums1, vector<int>& nums2) {
        int mergeSize = nums1.size() + nums2.size();
        int midIndex = mergeSize / 2 - 1;
        int frontIndex = -1;
        int midNum1 = 0;
        int midNum2 = 0;
        int i = 0, j = 0;
        while(i < nums1.size() && j < nums2.size()){
            if(frontIndex == midIndex){
                midNum2 = nums1[i] < nums2[j] ? nums1[i] : nums2[j];
                break;
            }
            if(nums1[i] < nums2[j]){
                midNum1 = nums1[i];
                i++;
            }else{
                midNum1 = nums2[j];
                j++;
            }
            frontIndex++;
        }
        if(frontIndex <= midIndex){
            if(i == nums1.size()){
                for(;j < nums2.size();j++){
                    if(frontIndex == midIndex){
                        midNum2 = nums2[j];
                        break;
                    }
                    midNum1 = nums2[j];
                    frontIndex++;
                }
            }else if(j == nums2.size()){
                for(;i < nums1.size();i++){
                    if(frontIndex == midIndex){
                        midNum2 = nums1[i];
                        break;
                    }
                    midNum1 = nums1[i];
                    frontIndex++;
                }
            }
        }
        if(mergeSize % 2 == 0){
            return (midNum1+midNum2) / 2.0;
        }else{
            return midNum2 * 1.0;
        }
    }
};
// @lc code=end

// int main(){
//     vector<int> nums1 {0,0,0,0,0};
//     vector<int> nums2 {-1,0,0,0,0,0,1};
//     Solution s;

//     std::cout << s.findMedianSortedArrays(nums1,nums2);
// }