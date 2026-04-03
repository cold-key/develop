/*
 * @lc app=leetcode.cn id=1878 lang=cpp
 *
 * [1878] 矩阵中最大的三个菱形和
 */

#include<vector>
#include<iostream>
#include<algorithm>

using namespace std;

// @lc code=start
class Solution {
public:
    vector<int> getBiggestThree(vector<vector<int>>& grid) {
        std::vector<int> ans;
        std::vector<std::vector<std::pair<int,int>>> preSum (grid.size(),std::vector<std::pair<int,int>>(grid[0].size(),std::make_pair(0,0)));
        int row = grid.size();
        int col = grid[0].size();
        for(int i = 0; i < grid.size(); ++i){
            for(int j = 0; j < grid[i].size(); ++j){
                int preLeftSum = (i - 1 >= 0 && j - 1 >= 0) ? preSum[i-1][j-1].first : 0;
                preSum[i][j].first = preLeftSum + grid[i][j];
                int preRightSum = (i - 1 >= 0 && j + 1 < col) ? preSum[i-1][j+1].second : 0;
                preSum[i][j].second = preRightSum + grid[i][j];
            }
        }
        // std::cout << "row: " << row << " col: " << col << std::endl;
        int maxHeight = std::min(row,col) % 2 == 0 ? std::min(row,col) - 1: std::min(row,col);
        for(int h = maxHeight; h >= 1 ; h -=2){
            int startI = 0;
            int endI = row - h;
            int startJ = (h - 1) / 2;
            int endJ = col - startJ - 1;
            // std::cout << "h: " << h << " startI: " << startI << " endI: " << endI << " startJ: " << startJ << " endJ: " << endJ << std::endl;
            for(int i = startI; i <= endI;++i){
                for(int j = startJ; j <= endJ;++j){
                    // std::cout << i+(h-1)/2 << " " << j-(h-1)/2 << std::endl;
                    // std::cout << i+(h-1)/2 << " " << j+(h-1)/2 << std::endl;
                    // std::cout << i+(h-1) << " " << j << std::endl;
                    int leftTopSum = preSum[i+(h-1)/2][j-(h-1)/2].second - preSum[i][j].second;
                    // std::cout << "leftTopSum: " << leftTopSum << std::endl;
                    int rightTopSum = preSum[i+(h-1)/2][j+(h-1)/2].first - preSum[i][j].first;
                    // std::cout << "rightTopSum: " << rightTopSum << std::endl;
                    int leftBottomSum = preSum[i+(h-1)][j].first - preSum[i+(h-1)/2][j-(h-1)/2].first;
                    // std::cout << "leftBottomSum: " << leftBottomSum << std::endl;
                    int rightBottomSum = preSum[i+(h-1)][j].second - preSum[i+(h-1)/2][j+(h-1)/2].second;
                    // std::cout << "rightBottomSum: " << rightBottomSum << std::endl;
                    int sum = leftTopSum + rightTopSum + leftBottomSum + rightBottomSum;
                    sum += (- grid[i+(h-1)][j] + grid[i][j]);

                    if(h == 1){
                        sum = grid[i][j];
                    }
                    
                    // std::cout << "sum: " << sum << std::endl;
                    if(ans.size()<3){
                        bool isSame = false;
                        for(int a: ans){
                            if(a == sum){
                                isSame = true;
                                break;
                            }
                        }
                        if(!isSame){
                            ans.push_back(sum);
                        }
                        sort(ans.begin(),ans.end(),[](int x,int y){
                            return x > y;
                        });
                    }else{
                        bool isSame = false;
                        for(int a: ans){
                            if(a == sum){
                                isSame = true;
                                break;
                            }
                        }
                        if(isSame){
                            continue;
                        }
                        if(ans[2] < sum){
                            ans[2] = sum;
                        }
                        ranges::sort(ans,[](int x,int y){
                            return x >y;
                        });
                    }
                }
            }
        }
        return ans;
    }
};
// @lc code=end

int main(){
    Solution s;
    vector<vector<int>> grid = {{1,2,3},{4,5,6},{7,8,9}};
    auto ans = s.getBiggestThree(grid);
    for(auto& a: ans){
        cout << a << endl;
    }
}