/*
 * @lc app=leetcode.cn id=2024 lang=cpp
 *
 * [2024] 考试的最大困扰度
 */

#include<iostream>
#include<string>
#include<unordered_map>

using namespace std;

// @lc code=start
class Solution {
public:
    int maxConsecutiveAnswers(string answerKey, int k) {
        int leftEdge = 0;
        int TTimes = 0;
        int FTimes = 0;
        int maxLen = 0;
        for(int i = 0; i < answerKey.size(); i++){
            if(answerKey[i] == 'T'){
                ++TTimes;
            }
            if(answerKey[i] == 'F'){
                ++FTimes;
            }

            if((TTimes < FTimes ? TTimes : FTimes )> k){
                maxLen = maxLen > (i - leftEdge) ? maxLen : (i - leftEdge);
                while((TTimes < FTimes ? TTimes : FTimes ) > k){
                    if(answerKey[leftEdge] == 'T'){
                        --TTimes;
                    }
                    if(answerKey[leftEdge] == 'F'){
                        --FTimes;
                    }
                    ++leftEdge;
                }
            }
        }
        maxLen = maxLen > (answerKey.size() - 1 - leftEdge + 1) ? maxLen : (answerKey.size() - 1 - leftEdge + 1);
        return maxLen;
    }
};
// @lc code=end

