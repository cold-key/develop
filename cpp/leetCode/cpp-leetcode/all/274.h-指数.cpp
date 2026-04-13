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
        ranges::sort(citations);
        for(int i = 0; i < citations.size(); ++i){
            if(citations[i] >= citations.size() - i){
                return citations.size() - i;
            }
        }
        return 0;
    }
};
// @lc code=end

int main(){
    Solution s;
    vector<int> citations = {1,3,1};
    cout << s.hIndex(citations) << endl;
    return 0;
}