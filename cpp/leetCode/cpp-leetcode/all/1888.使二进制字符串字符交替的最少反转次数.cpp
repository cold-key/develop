/*
 * @lc app=leetcode.cn id=1888 lang=cpp
 *
 * [1888] 使二进制字符串字符交替的最少反转次数
 */

// #include "lib/tool.h"

#include<iostream>
#include<algorithm>
#include<string>

using namespace std;

// @lc code=start
class Solution {
public:
    int minFlips(string s) {
        int reverseCnt = 0;
        int ans = s.size();
        int n = s.size();
        for(int i = 0; i < 2 * n - 1; i++){
            if(s[i % n] % 2 == i % 2){
                ++reverseCnt; 
            }
            int left = i - n + 1;
            if(left < 0){
                continue;
            }
            ans = min({ans,reverseCnt, n-reverseCnt});
            if(s[left] % 2 == left % 2){
                --reverseCnt; 
            }
        }
        return ans;
    }
};
// @lc code=end

// std::min <algorithm> 头文件提供的模板函数

class Point{
public:
    int x;
    int y;
    Point(int x, int y): x {x},y {y}{};
    bool operator<(const Point& p) const{
        return x < p.x;
    }
};

int main(){
    std::cout << std::min(1,2) << '\n';

    Point p1{1,2};
    Point p2{3,4};
    Point minXP = std::min(p1,p2);

    Point minYP = std::min(p1,p2,[](Point p1,Point p2){
        return p1.y < p2.y;
    });
    std::stoi("12",nullptr);
    return 0;
}