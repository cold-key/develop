/*
 * @lc app=leetcode.cn id=2039 lang=cpp
 *
 * [2039] 网络空闲的时刻
 */

#include<stdio.h>
#include<iostream>
#include<vector>
#include<unordered_set>
#include<cstdlib>
#include<float.h>

using namespace std;

// @lc code=start
class Solution {
public:
    int networkBecomesIdle(vector<vector<int>>& edges, vector<int>& patience) {
        // 暂时不做排序
        vector<int> toServerDis (patience.size(),patience.size()+1);
        int curPoint = edges[0][0];
        unordered_set<int> hasInvitedSet;
        hasInvitedSet.insert(curPoint);
        toServerDis[0] = 0;
        for(int i = 0; i < edges.size(); i++){

        }

    }
};
// @lc code=end

