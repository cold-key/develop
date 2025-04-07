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
        for(int i = 1; i <= 3; i++){
            string firstStr = s.substr(0,i);
            int firstStrNum = stoi(firstStr);
            if(firstStrNum < f[i-1][0] || firstStrNum > f[i-1][1]){
                continue;
            }
            for(int j = 1; j <= 3; j++){
                string secondStr = s.substr(i,j);
                int secondNum = stoi(secondStr);
                if(secondNum < f[j-1][0] || secondNum > f[j-1][1]){
                    continue;
                }
                for(int k = 1; k <= 3; k++){
                    string sanStr = s.substr(i+j,k);
                    int sanStrNum = stoi(sanStr);
                    if(sanStrNum < f[k-1][0] || sanStrNum > f[k-1][1]){
                        continue;
                    }
                    string siStr = s.substr(i+j+k);
                    if(siStr.length()>3){
                        continue;
                    }
                    int siStrNum = stoi(siStr);
                    if(siStrNum < f[2][0] || siStrNum > f[2][1]){
                        continue;
                    }
                    result.push_back(firstStr+"."+secondStr+"."+sanStr+"."+siStr);
                }
            }
        }
        return result;
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

