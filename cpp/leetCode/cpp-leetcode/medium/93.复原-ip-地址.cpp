/*
 * @lc app=leetcode.cn id=93 lang=cpp
 *
 * [93] 复原 IP 地址
 */

// @lc code=start
#include<iostream>
#include<vector>
#include<string>
using namespace std;
class Solution {
public:
    vector<vector<int>> f {{0,9},{10,99},{100,255}};

    vector<string> restoreIpAddresses(string s) {
        vector<string> result;
    }

    // vector<string> subToNumPieces(string s , int num){
    //     if(num > 1){
    //         for(int i = 0; i < 3; i++){
    //             int n = stoi(s.substr(0,i));
    //             if( n >= f[i][0] && n <= f[i][1]){
    //                 vector<string> sv = subToNumPieces()
    //             }else{
    //                 break;
    //             }
    //         }
            
    //     }else{
    //         //
    //     }
    // }
};
// @lc code=end

