/*
 * @lc app=leetcode.cn id=384 lang=cpp
 *
 * [384] 打乱数组
 */

#include<stdio.h>
#include<iostream>
#include<vector>
#include<unordered_set>
#include<cstdlib>
#include<float.h>
#include <random>

using namespace std;

// @lc code=start
class Solution {
public:

    vector<int> nums;

    Solution(vector<int>& nums) {
        this->nums = nums;
    }
    
    vector<int> reset() {
        return nums;
    }
    
    vector<int> shuffle() {
        vector<int> shuffleNums = nums;
        static std::random_device rd;
        static std::mt19937 gen(rd());
        for(int i = shuffleNums.size() - 1; i > 0; i--){
            std::uniform_int_distribution<size_t> dis(0, i);
            std::swap(shuffleNums[i],shuffleNums[dis(gen)]);
        }
        return shuffleNums;
    }
};

/**
 * Your Solution object will be instantiated and called as such:
 * Solution* obj = new Solution(nums);
 * vector<int> param_1 = obj->reset();
 * vector<int> param_2 = obj->shuffle();
 */
// @lc code=end

// void printVector(vector<int> v){
//     if(v.size() == 0){
//         std::cout<<"warning size equal zero"<< endl;
//         return;
//     }
//     for(int i = 0; i < v.size(); i++){
//         std::cout << v[i] << ",";
//     }
//     std::cout << endl;
// }

// int main(){
//     vector<int> test {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};
//     Solution* s = new Solution(test);
//     for(int i = 0; i < 10; i++){
//         printVector(s->reset());
//         printVector(s->shuffle());
//     }

// }
