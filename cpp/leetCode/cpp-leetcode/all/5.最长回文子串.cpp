/*
 * @lc app=leetcode.cn id=5 lang=cpp
 *
 * [5] 最长回文子串
 */

#include <string>
#include <algorithm>
#include <iostream>
#include <vector>

using namespace std;

// @lc code=start
class Solution {
public:
    string longestPalindrome(string s) {
        for(int i = 0; i < s.size(); i++){
            s.insert(i, "#");
            i++;
        }
        s.append("#");
        // cout<<s<<endl;
        
        std::vector<int> radius(s.size(), 0);
        int maxRightEdge = -1;
        int maxRightEdgeIndex = -1;
        int maxLeftIndex = 0;
        int maxRightIndex = 0;
        for(int i = 0 ; i < s.size(); i++){
            if(i < maxRightEdge){
                radius[i] = min(radius[2 * maxRightEdgeIndex - i], maxRightEdge - i);
            }
            int leftIndex = i - 1 - radius[i];
            int rightIndex = i + 1 + radius[i];
            while(leftIndex >= 0 && rightIndex < s.size() && s[leftIndex] == s[rightIndex]){
                leftIndex--;
                rightIndex++;
            }
            if(rightIndex - leftIndex - 1 > maxRightIndex - maxLeftIndex - 1){
                maxLeftIndex = leftIndex;
                maxRightIndex = rightIndex;
            }
            radius[i] = (rightIndex - leftIndex - 1) / 2;
            if(radius[i] > maxRightEdge){
                maxRightEdge = radius[i];
                maxRightEdgeIndex = i;
            }
        }
        char target = '#';
        string maxSubStr = s.substr(maxLeftIndex + 1, maxRightIndex - maxLeftIndex - 1);
        maxSubStr.erase(remove_if(maxSubStr.begin(), maxSubStr.end(), [target](char c) {
            return c == target;
        }), maxSubStr.end());
        
        return maxSubStr;
        
    }
};
// @lc code=end

int main(){
    Solution s;
    string str = "ccc";
    string result = s.longestPalindrome(str);
    std::cout << result << std::endl;
    return 0;
}






















// --------------------
// 个人错误解法：动态规划思路，维护一个最小最大index，当有新的字符从末尾加入时，分情况讨论。
// 貌似勤快简单。可对于回文串长度的奇数偶数情况没有很好的处理，导致了很多边界情况的错误。
// class Solution {
// public:
//     string longestPalindrome(string s) {
//         int maxLeftIndex = 0;
//         int maxRightIndex = 0;
//         for (int i = 1; i < s.size(); i++) {
//             std::cout << "i: " << i << " maxLeftIndex: " << maxLeftIndex << " maxRightIndex: " << maxRightIndex << std::endl;
//             if(maxRightIndex == i - 1){
//                 if(maxLeftIndex == maxRightIndex && s[i] == s[maxLeftIndex]) {
//                     maxRightIndex = i;
//                     continue;
//                 }
//                 if(maxLeftIndex - 1 > 0 && s[i] == s[maxLeftIndex - 1]) {
//                     maxLeftIndex = maxLeftIndex - 1;
//                     maxRightIndex = i;
//                     continue;
//                 }else{
//                     int leftCheck = maxLeftIndex + 1;
//                     int rightCheck = i;
//                     while(leftCheck < rightCheck) {
//                         if(s[leftCheck] == s[rightCheck]) {
//                             leftCheck++;
//                             rightCheck--;
//                         }else{
//                             break;
//                         }
//                     }
//                     if(leftCheck >= rightCheck) {
//                         maxLeftIndex = maxLeftIndex + 1;
//                         maxRightIndex = i;
//                     }
//                 }
//             }else{
//                 for(int j = 0; j <= i - (maxRightIndex - maxLeftIndex); j++) {
//                     int leftCheck = j;
//                     int rightCheck = i;
//                     while(leftCheck < rightCheck) {
//                         if(s[leftCheck] == s[rightCheck]) {
//                             leftCheck++;
//                             rightCheck--;
//                         }else{
//                             break;
//                         }
//                     }
//                     if(leftCheck >= rightCheck && i - j >= maxRightIndex - maxLeftIndex) {
//                         maxLeftIndex = j;
//                         maxRightIndex = i;
//                         break;
//                     }
//                 }
//             }
//         }
//         return s.substr(maxLeftIndex, maxRightIndex - maxLeftIndex + 1);
//     }
// };