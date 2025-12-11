/*
 * @lc app=leetcode.cn id=1658 lang=cpp
 *
 * [1658] 将 x 减到 0 的最小操作数
 */

#include<iostream>
#include<vector>

using namespace std;

// @lc code=start
class Solution {
public:
    int minOperations(vector<int>& nums, int x) {
        if(nums[0] == x || nums[nums.size() - 1] == x){
            return 1;
        }
        int minOperateNum = nums.size() + 1;
        int leftEdge = 0;
        int rigthEdge = 0;
        int sum = 0;
        for(; rigthEdge < nums.size(); ++rigthEdge){
            if(sum + nums[rigthEdge] < x){
                sum += nums[rigthEdge];
            }
            else if(sum + nums[rigthEdge] == x){
                minOperateNum = minOperateNum < (rigthEdge - leftEdge + 1) ? minOperateNum : (rigthEdge - leftEdge + 1);
                break;
            }else{
                sum += nums[rigthEdge];
                break;
            }
        }
        if(rigthEdge == nums.size() && minOperateNum == nums.size() + 1){
            return -1;
        }
        std::cout << "init sum" << sum << endl;
        while(rigthEdge >= 0){
            if(sum > x){
                if(leftEdge < rigthEdge){
                    sum -= nums[rigthEdge];
                    --rigthEdge;
                }else if(leftEdge > rigthEdge){
                    if(sum - nums[leftEdge] >= x){
                        sum -= nums[leftEdge];
                        ++leftEdge;
                        leftEdge = leftEdge == nums.size() ? 0 : leftEdge;
                    }else{
                        sum -= nums[rigthEdge];
                        --rigthEdge;
                    }
                }else{
                    leftEdge = nums.size() - 1;
                    rigthEdge = nums.size() - 1;
                    sum = nums[nums.size() - 1];
                    break;
                }
            }else if (sum == x){
                if(leftEdge < rigthEdge){
                    minOperateNum = minOperateNum < (rigthEdge - leftEdge + 1) ? minOperateNum : (rigthEdge - leftEdge + 1);
                }else if(leftEdge > rigthEdge){
                    int len = rigthEdge + 1 + nums.size() - leftEdge;
                    minOperateNum = minOperateNum < len ? minOperateNum : len;
                }else{
                    std::cout << leftEdge << endl;
                    return 1;
                }
                sum -= nums[rigthEdge];
                --rigthEdge;
            }else if(sum < x){
                --leftEdge;
                if(leftEdge < 0){
                    leftEdge = nums.size() - 1;
                }

                sum += nums[leftEdge];
                if(sum > x){
                    sum -= nums[rigthEdge];
                    --rigthEdge;
                }

            }
        }
        rigthEdge = rigthEdge < 0 ? nums.size() - 1 : rigthEdge;
        while(leftEdge <= rigthEdge){
            if(sum > x){
                if(sum - nums[leftEdge] >= x){
                    sum -= nums[leftEdge];
                    leftEdge++;
                }else{
                    break;
                }
            }else if(sum == x){
                minOperateNum = minOperateNum < (rigthEdge - leftEdge + 1) ? minOperateNum : (rigthEdge - leftEdge + 1);
                break;
            }else{
                --leftEdge;
                if(sum + nums[leftEdge] <= x){
                    sum += nums[leftEdge];
                }else{
                    break;
                }
            }
        }
        return minOperateNum == nums.size() + 1 ? -1 : minOperateNum;
    }
};
// @lc code=end

int main(){
    vector<int> test {8828,9581,49,9818,9974,9869,9991,10000,10000,10000,9999,9993,9904,8819,1231,6309};
    int x = 134365;
    Solution s;
    std::cout << s.minOperations(test,x);
}

// 直接滑动太多边界情况了，需要逆向思维（求 reduce(nums) - x），上述题解90/97，无心考虑各种边界情况