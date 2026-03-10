/*
 * @lc app=leetcode.cn id=1980 lang=cpp
 *
 * [1980] 找出不同的二进制字符串
 */

#include<string>
#include<vector>
#include<unordered_set>
#include<bitset>
#include<iostream>

using namespace std;

// @lc code=start
class Solution {
public:
    string findDifferentBinaryString(vector<string>& nums) {
        unordered_set<int> m;
        for(string num : nums){
            m.insert(std::stoi(num,nullptr,2));
        }
        int ans = 0;
        int maxIndex = 1 << nums.size();
        // std::cout << maxIndex;
        for(int i = 0; i < maxIndex ; i++){
            if(!m.count(i)){
                ans = i;
                break;
            }
        }
        return bitset<32>(ans).to_string().substr(32 - nums.size());
    }
};
// @lc code=end

// int main(){
//     vector<string> t {"01","10"};
//     Solution s;
//     s.findDifferentBinaryString(t);
// }