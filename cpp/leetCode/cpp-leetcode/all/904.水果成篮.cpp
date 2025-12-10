/*
 * @lc app=leetcode.cn id=904 lang=cpp
 *
 * [904] 水果成篮
 */

#include<iostream>
#include<vector>
#include<unordered_map>
#include<utility>

using namespace std;

// @lc code=start
class Solution {
public:
    int totalFruit(vector<int>& fruits) {
        std::unordered_map<int,std::pair<int,int>> treeMap;
        int maxLen = 0;
        int minLeftEdge = 0;
        for(int i = 0; i < fruits.size(); i++){
            if(treeMap.size() < 2){
                int leftEdge = treeMap.count(fruits[i]) ? i : treeMap[fruits[i]].first;
                treeMap[fruits[i]] = make_pair(leftEdge,i);
                minLeftEdge = minLeftEdge < leftEdge ? minLeftEdge : leftEdge;
            }else{
                if(treeMap.count(fruits[i])){
                    treeMap[fruits[i]] = make_pair(treeMap[fruits[i]].first,i);;
                }else{
                    int minUpdateEdge = fruits.size();
                    int waitForDeleteKey;
                    for(const auto& n : treeMap){
                        int rightEdge = n.second.second;
                        if(rightEdge < minUpdateEdge){
                            minUpdateEdge = rightEdge;
                            waitForDeleteKey = n.first;
                        }
                    }

                    for(auto& n : treeMap){
                        n.second.first = treeMap[waitForDeleteKey].second + 1;
                    }
                    minLeftEdge = treeMap[waitForDeleteKey].second + 1;
                    treeMap.erase(waitForDeleteKey);

                    treeMap[fruits[i]] = make_pair(i,i);;
                }
            }
            maxLen = maxLen > (i - minLeftEdge + 1) ? maxLen : (i - minLeftEdge + 1);
        }
        return maxLen;
    }
};
// @lc code=end

