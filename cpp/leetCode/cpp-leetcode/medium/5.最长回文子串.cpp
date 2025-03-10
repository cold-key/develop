/*
 * @lc app=leetcode.cn id=5 lang=cpp
 *
 * [5] 最长回文子串
 */

// @lc code=start

#include <string>
#include <algorithm>
#include <iostream>
using namespace std;

class Solution {
public:
    string longestPalindrome(string s) {
        for(int i = 0; i < s.size(); i++){
            s.insert(i, "#");
            i++;
        }
        s.append("#");
        // cout<<s<<endl;
        string maxSubStr = s.substr(0, 1);
        for(int i = 0 ; i < s.size(); i++){
            int leftIndex = i - 1;
            int rightIndex = i + 1;
            while(leftIndex >= 0 && rightIndex < s.size() && s[leftIndex] == s[rightIndex]){
                leftIndex--;
                rightIndex++;
            }
            if(rightIndex - leftIndex - 1 > maxSubStr.size()){
                maxSubStr = s.substr(leftIndex + 1, rightIndex - leftIndex - 1);
            }
        }
        char target = '#';
        maxSubStr.erase(remove_if(maxSubStr.begin(), maxSubStr.end(), [target](char c) {
            return c == target;
        }), maxSubStr.end());
        
        return maxSubStr;
        
    }
};
// @lc code=end

// 


// test code
// int main(){
//     Solution s;
//     string str = "abb";
//     string result = s.longestPalindrome(str);
//     return 0;
// }
