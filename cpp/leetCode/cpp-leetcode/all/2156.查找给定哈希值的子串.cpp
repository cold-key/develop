/*
 * @lc app=leetcode.cn id=2156 lang=cpp
 *
 * [2156] 查找给定哈希值的子串
 */

#include<iostream>
#include<string>
#include<cmath>

using namespace std;

// @lc code=start
class Solution {
public:
    long long qpow(int power,int n,int m){
        long long result = 1;
        long long llpower = power;
        while(n > 0){
            int lastNum = n & 1;
            if(lastNum == 1){
                result = result * llpower % m;
            }
            // std::cout << "n:" << n << "\tlastNum:" << lastNum << "\ttempNum:" << tempNum << endl;
            llpower = llpower * llpower % m;
            n = n >> 1;
        }
        return result;
    }

    string subStrHash(string s, int power, int modulo, int k, int hashValue) {
        auto val = [](char c) -> int {
            return c - 'a' + 1;
        };
        long long tempHashValue = 0;
        string minStr;
        int minStrStartIndex = 0;
        for(int i = k; i > 0; i--){
            tempHashValue += val(s[s.size() - 1 - (k - i)]) * (long long)qpow(power, i - 1, modulo);
            tempHashValue %= modulo;
        }
        if(tempHashValue == hashValue){
            // minStr = s.substr(s.size() - k);
            minStrStartIndex = s.size() - k;
        }
        // std::cout << "firsr tempHashValue:" << tempHashValue << endl;
        for(int i = s.size() - k - 1; i >= 0; i--){
            long long subTempHashValue = (tempHashValue - ((val(s[i + k]) * (long long)qpow(power, k - 1, modulo)) % modulo) + modulo) % modulo;
            subTempHashValue = (subTempHashValue * (power % modulo)) % modulo;
            tempHashValue = (subTempHashValue + (val(s[i]) % modulo)) % modulo;
            if(tempHashValue == hashValue){
                // minStr = s.substr(i, k);
                minStrStartIndex = i;
            }
            // std::cout << "str:" << s.substr(i, k) <<"\thashValue:"<<tempHashValue<<endl;
        }
        minStr = s.substr(minStrStartIndex, k);
        return minStr;
    }
};
// @lc code=end

// int main(){
//     // string str = "leetcode";
//     // int power = 7;
//     // int modulo = 20;
//     // int k = 2;
//     // int hashValue = 0;
//     // Solution s;
//     // std::cout << s.subStrHash(str,power,modulo,k,hashValue);

//     // test qpow
//     Solution s;
//     int power = 2;
//     cout << s.qpow(power,19,1024);
//     for(int i = 1; i < 63; i++){
//         int rightValue = (long long)pow(power,i) % 1024;
//         int qpowValue = s.qpow(power,i,1024);
//         std::cout<<rightValue << "---"<<qpowValue<<endl;
//     }
// }