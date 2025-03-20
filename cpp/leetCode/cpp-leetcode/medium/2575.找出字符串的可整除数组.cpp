/*
 * @lc app=leetcode.cn id=2575 lang=cpp
 *
 * [2575] 找出字符串的可整除数组
 */

 #include<iostream>
 #include<string>
 #include<vector>
 using namespace std;

// @lc code=start
class Solution {
public:
    vector<int> divisibilityArray(string word, int m) {
        string numString = to_string(m);
        int startIndex = 0;

        vector<int> result (word.length(),0);
        long ys = stoll(word.substr(0,startIndex+1)) % m;
        result[startIndex] = ys == 0;

        for(int i = startIndex + 1; i < word.size(); i++){
            ys = (ys * 10 + (word[i] -'0')) % m;
            result[i] =  ys == 0;
        }
        
        return result;
    }
};
// @lc code=end

// //test
// int main(){
//     Solution s;
//     vector<int> result = s.divisibilityArray("1010", 10);
//     for(int i = 0; i < result.size(); i++){
//         cout << result[i] << " ";
//     }
//     cout << endl;
//     return 0;
// }
