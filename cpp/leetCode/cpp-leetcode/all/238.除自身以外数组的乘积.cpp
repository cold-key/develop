/*
 * @lc app=leetcode.cn id=238 lang=cpp
 *
 * [238] 除自身以外数组的乘积
 */

#include <vector>
#include <algorithm>
#include <iostream>

using namespace std;

// @lc code=start
class Solution {
public:
    vector<int> productExceptSelf(vector<int>& nums) {
        vector<int> ans (nums.size(),0);
        ans[ans.size() - 1] = nums[nums.size() - 1];
        for(int i = nums.size() - 2; i >= 0; --i){
            ans[i] = ans[i+1] * nums[i];
        }
        int left = 1;
        for(int i = 0; i < ans.size(); ++i){
            int right = i == ans.size() - 1 ? 1 : ans[i+1];
            ans[i] = left * right;
            left *= nums[i];
        }
        return ans;
    }
};
// @lc code=end

int main(){
    Solution s;
    vector<int> nums = {-1,1,0,-3,3};
    auto ans = s.productExceptSelf(nums);
    for(auto i : ans){
        cout << i << " ";
    }
    cout << endl;
}

/*
时间复杂度和空间复杂度都为O(n)的写法是构建一个前缀积和后缀积的数组，最后再遍历一次计算结果。
要想空间复杂度为O(1)，则可以利用输出数组来存储后缀积，在计算前缀积的时候直接乘上后缀积的值。
*/