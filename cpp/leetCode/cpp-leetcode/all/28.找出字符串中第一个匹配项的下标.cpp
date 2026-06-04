/*
 * @lc app=leetcode.cn id=28 lang=cpp
 *
 * [28] 找出字符串中第一个匹配项的下标
 */

#include <string>
#include <iostream>

using namespace std;

// @lc code=start
class Solution {
public:
    int strStr(string haystack, string needle) {
        int hSize = haystack.size();
        int nSize = needle.size();
        std::cout << "Haystack size: " << hSize << ", Needle size: " << nSize << std::endl; // Debug statement
        for(int i = 0; i <= hSize - nSize; ++i) {
            std::cout << "Checking at index: " << i << std::endl; // Debug statement
            int j = 0;
            for(; j < nSize; ++j) {
                if (haystack[i + j] != needle[j]) {
                    break;
                }
            }
            if (j == nSize) {
                return i;
            }
        }
        return -1;
    }
};
// @lc code=end

int main() {
    Solution solution;
    string haystack = "aaa";
    string needle = "aaaa";
    int result = solution.strStr(haystack, needle);
    printf("Result: %d\n", result); // Output: -1
    return 0;
}