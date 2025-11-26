/*
 * @lc app=leetcode.cn id=417 lang=cpp
 *
 * [417] 太平洋大西洋水流问题
 */

#include<iostream>
#include<vector>
#include<queue>

using namespace std;

// @lc code=start
class Solution {
public:
    vector<vector<int>> direction = {{0,-1},{1,0},{0,1},{-1,0}};

    vector<vector<int>> pacificAtlantic(vector<vector<int>>& heights) {
        vector<vector<int>> result;
        vector<vector<int>> flag (heights.size(),vector<int>(heights[0].size(),0));
        // std::
        for(int i = 0; i < heights.size(); i++){
            for(int j = 0; j < heights[i].size(); j++){
                auto p = std::make_pair(i,j);
                for(int x = 0; x < flag.size();x++){
                    for(int y = 0; y < flag[x].size(); y++){
                        flag[x][y] = 0;
                    }
                }
                if(isCanReach(heights,p,flag,result)){
                    result.push_back({i,j});
                }
            }
        }
        return result;
    }

    bool isCanReach(vector<vector<int>>& heights, std::pair<int,int> point, vector<vector<int>>& flag, vector<vector<int>>& result){
        bool isReachLeft = false;
        bool isReachRight  = false;
        std::queue<std::pair<int,int>> q;
        q.push(point);
        flag[point.first][point.second] = 1;
        while(q.size() > 0){
            std::pair<int,int> p = q.front();

            for(int i = 0; i < direction.size(); i++){
                int newFirst = p.first + direction[i][0];
                int newSecond = p.second + direction[i][1];
                if(newFirst >=0 && newFirst < heights.size() && newSecond >= 0 && newSecond < heights[0].size()){
                    if(heights[newFirst][newSecond] <= heights[p.first][p.second]){
                        // 临时写法
                        for(int j = 0; j < result.size(); j++){
                            if(newFirst == result[j][0] && newSecond == result[j][1]){
                                return true;
                            }
                        }
                        if(!flag[newFirst][newSecond]){
                            q.push(std::make_pair(newFirst,newSecond));
                            flag[newFirst][newSecond] = 1;
                        }
                    }
                }
                else if(newFirst < 0 || newSecond < 0){
                    isReachLeft = true;
                }
                else if(newFirst >= heights.size() || newSecond >= heights[0].size()){
                    isReachRight = true;
                }

                if(isReachLeft && isReachRight){
                    return true;
                }
            }

            q.pop();
        }

        return false;
    }
};
// @lc code=end

int main(){
    vector<vector<int>> test {
        {1,2,2,3,5},
        {3,2,3,4,4},
        {2,4,5,3,1},
        {6,7,1,4,5},
        {5,1,1,2,4}
    };
    Solution s;
    vector<vector<int>> r = s.pacificAtlantic(test);
    for(int i = 0; i < r.size(); i++){
        std::cout << "[";
        for(int j = 0; j < r[i].size(); j++){
            std::cout<< r[i][j] << "," ;
        }
        std::cout << "]";
    }
    return 0;
}

/*
    几乎等于暴力搜索，但能过.....
    正解，反向bfs，找出两边全部可达点的集合，然后求交集即可
*/