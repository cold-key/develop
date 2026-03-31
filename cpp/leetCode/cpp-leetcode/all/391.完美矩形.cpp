/*
 * @lc app=leetcode.cn id=391 lang=cpp
 *
 * [391] 完美矩形
 */

#include<vector>
#include<cmath>
#include<iostream>
#include<unordered_map>

using namespace std;

// @lc code=start
class Solution {
public:
    bool isRectangleCover(vector<vector<int>>& rectangles) {
        std::unordered_map<std::string, int> points;
        long long minLeft = rectangles[0][0];
        long long minBottom = rectangles[0][1];
        long long maxRight = rectangles[0][2];
        long long maxTop = rectangles[0][3];
        long long area = (maxRight - minLeft) * (maxTop - minBottom);
        points[std::to_string(rectangles[0][0]) + "," + std::to_string(rectangles[0][1])] += 1;
        points[std::to_string(rectangles[0][0]) + "," + std::to_string(rectangles[0][3])] += 1;
        points[std::to_string(rectangles[0][2]) + "," + std::to_string(rectangles[0][1])] += 1;
        points[std::to_string(rectangles[0][2]) + "," + std::to_string(rectangles[0][3])] += 1;
        for(int i = 1; i < rectangles.size(); ++i){
            minLeft = minLeft > rectangles[i][0] ? rectangles[i][0] : minLeft;
            minBottom = minBottom > rectangles[i][1] ? rectangles[i][1] : minBottom;
            maxRight = maxRight < rectangles[i][2] ? rectangles[i][2] : maxRight;
            maxTop = maxTop < rectangles[i][3] ? rectangles[i][3] : maxTop;

            points[std::to_string(rectangles[i][0]) + "," + std::to_string(rectangles[i][1])] += 1;
            points[std::to_string(rectangles[i][0]) + "," + std::to_string(rectangles[i][3])] += 1;
            points[std::to_string(rectangles[i][2]) + "," + std::to_string(rectangles[i][1])] += 1;
            points[std::to_string(rectangles[i][2]) + "," + std::to_string(rectangles[i][3])] += 1;

            area += (rectangles[i][2] - rectangles[i][0]) * (rectangles[i][3] - rectangles[i][1]);
        }
        // std::cout << "minLeft : " << minLeft << " minBottom : " << minBottom << " maxRight : " << maxRight << " maxTop : " << maxTop << std::endl;
        for(auto& point : points){
            // std::cout << "point : " << point.first << " count : " << point.second << std::endl;
            if(point.second % 2 != 0 
                && point.first != std::to_string(minLeft) + "," + std::to_string(minBottom) 
                && point.first != std::to_string(minLeft) + "," + std::to_string(maxTop)
                && point.first != std::to_string(maxRight) + "," + std::to_string(minBottom)
                && point.first != std::to_string(maxRight) + "," + std::to_string(maxTop)){
                // std::cout << "first : false" << std::endl;
                return false;
            }
        }
        if(points[std::to_string(minLeft) + "," + std::to_string(minBottom)] != 1 
            || points[std::to_string(maxRight) + "," + std::to_string(maxTop)] != 1
            || points[std::to_string(minLeft) + "," + std::to_string(maxTop)] != 1
            || points[std::to_string(maxRight) + "," + std::to_string(minBottom)] != 1){
            // std::cout << "second : false" << std::endl;
            return false;
        }
        long long expectedArea = (maxRight - minLeft) * (maxTop - minBottom);
        return area == expectedArea;
    }
};
// @lc code=end

// 尝试一：面积法，不行
// 尝试二：面积法，好像可以

// int main(){
//     std::vector<std::vector<int>> rectangles = {{1,1,3,3},{3,1,4,2},{3,2,4,4},{1,3,2,4},{2,3,3,4}};
//     Solution sol;
//     bool result = sol.isRectangleCover(rectangles);
//     std::cout << (result ? "True" : "False") << std::endl;
//     return 0;
// }