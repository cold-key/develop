/*
 * @lc app=leetcode.cn id=874 lang=cpp
 *
 * [874] 模拟行走机器人
 */
#define _USE_MATH_DEFINES
#include<iostream>
#include <vector>
#include <unordered_map>
#include<set>
#include<algorithm>
#include <cmath>
#include<ranges>

using namespace std;

// @lc code=start
class Solution {
public:
    int robotSim(vector<int>& commands, vector<vector<int>>& obstacles) {
        std::unordered_map<int,std::set<int>> xMap;
        std::unordered_map<int,std::set<int>> yMap;
        for(int i = 0; i < obstacles.size(); ++i){
            int x = obstacles[i][0];
            int y = obstacles[i][1];
            xMap[y].insert(x);
            yMap[x].insert(y);
        }
        int maxDistance = 0;

        std::pair<int,int> curPoint (0,0);
        int curAngle = 90;
        for(auto command : commands){
            std::cout << "------------------" << std::endl;
            std::cout << "command: " << command << std::endl;
            std::cout << "curPoint: " << curPoint.first << " " << curPoint.second << std::endl;
            std::cout << "curAngle: " << curAngle << std::endl;
            if(command == -2){
                curAngle += 90;
            }else if(command == -1){
                curAngle -= 90;
            }else{
                double radians = curAngle * M_PI / 180.0;
                int xOper = (int)std::cos(radians);
                int yOper = (int)std::sin(radians);
                std::cout << "xOper: " << xOper << " yOper: " << yOper << std::endl;

                if(xOper == 0){
                    int targetY = curPoint.second + yOper * command;
                    if(targetY > curPoint.second){
                        auto iter = yMap[curPoint.first].upper_bound(curPoint.second);
                        int farY = iter != yMap[curPoint.first].end() ? *iter - 1 : targetY;
                        curPoint.second = min(farY,targetY);
                    }else{
                        auto iter = yMap[curPoint.first].lower_bound(curPoint.second);
                        int farY = iter != yMap[curPoint.first].begin() ? *--iter + 1 : targetY;
                        curPoint.second = max(farY,targetY);
                    }
                }else{
                    int targetX = curPoint.first + xOper * command;
                    if(targetX > curPoint.first){
                        auto iter = xMap[curPoint.second].upper_bound(curPoint.first);
                        int farX = iter != xMap[curPoint.second].end() ? *iter - 1 : targetX;
                        curPoint.first = min(farX,targetX);
                    }else{
                        auto iter = xMap[curPoint.second].lower_bound(curPoint.first);
                        int farX = iter != xMap[curPoint.second].begin() ? *--iter + 1 : targetX;
                        curPoint.first = max(farX,targetX);
                    }
                }
                std::cout << "newPoint: " << curPoint.first << " " << curPoint.second << std::endl;
                int distance = curPoint.first * curPoint.first + curPoint.second * curPoint.second;
                maxDistance = max(maxDistance,distance);
            }

        }
        return maxDistance;
    }
};
// @lc code=end

int main(){
    Solution solution;
    std::vector<int> commands = {6,-1,-1,6};
    std::vector<std::vector<int>> obstacles =  {{0,0}};
    int res = solution.robotSim(commands,obstacles);
    std::cout << res << std::endl;
    return 0;
}