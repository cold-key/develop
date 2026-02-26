/*
 * @lc app=leetcode.cn id=3074 lang=cpp
 *
 * [3074] 重新分装苹果
 */

#include<vector>
#include<algorithm>

using namespace std;

// @lc code=start
class Solution {
public:
    int minimumBoxes(vector<int>& apple, vector<int>& capacity) {
        int sum = 0;
        for(auto v : apple){
            sum += v;
        }
        sort(capacity.begin(),capacity.end(),[](int a, int b) -> bool {
            return a > b;
        });
        int result = 0;
        for(int i = 0; i < capacity.size(); i++){
            if(sum - capacity[i] > 0){
                ++result;
                sum -= capacity[i];
            }else{
                ++result;
                break;
            }
        }
        return result;
    }
};
// @lc code=end

