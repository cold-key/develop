/*
 * @lc app=leetcode.cn id=274 lang=cpp
 *
 * [274] H 指数
 */
#include<vector>
#include<iostream>
#include<ranges>
#include<algorithm>

using namespace std;

// @lc code=start
class Solution {
public:
    int hIndex(vector<int>& citations) {
        // return hIndexSortMethod(citations);
        return hIndexBisectionMethod(citations);
    }

    // 排序之后就可以算答案了
    int hIndexSortMethod(vector<int>& citations) {
        ranges::sort(citations);
        for(int i = 0; i < citations.size(); ++i){
            if(citations[i] >= citations.size() - i){
                return citations.size() - i;
            }
        }
        return 0;
    }

    // 二分法，对于一组citations，答案肯定是 0 ~ citations.size() 这样就可以二分猜答案了
    int hIndexBisectionMethod(vector<int>& citations) {
        int left = 0;
        int right = citations.size();
        while(left < right){
            int mid = (left + right) / 2 + 1;
            int cnt = 0;
            for(int i = 0; i < citations.size(); ++i){
                if(citations[i] >= mid){
                    ++cnt;
                }
            }
            if(cnt >= mid){
                left = mid;
            }else{
                right = mid - 1;
            }
        }
        return left;
    }
};
// @lc code=end

int main(){
    Solution s;
    vector<int> citations = {5,5,6,5,5};
    cout << s.hIndex(citations) << endl;
    return 0;
}