/*
 * @lc app=leetcode.cn id=1689 lang=cpp
 *
 * [1689] 十-二进制数的最少数目
 */

// @lc code=start
class Solution {
public:
    int minPartitions(string n) {
        char maxChar = '0';
        for(int i = 0; i < n.size();i++){
            if(n[i] > maxChar){
                maxChar = n[i];
            }
        }
        return maxChar - '0';
    }
};
// @lc code=end

