/*
 * @lc app=leetcode.cn id=923 lang=cpp
 *
 * [923] 多重三数之和
 */

#include<vector>
#include<algorithm>
#include<unordered_map>
#include"lib/tool.h"

using namespace std;

// @lc code=start
class Solution {
public:
    int threeSumMulti(vector<int>& arr, int target) {
        std::ranges::sort(arr);
        int left = 0;
        int right = arr.size() - 1;
        std::unordered_map<int,int> numMap;
        for(int i = 0; i < arr.size(); i++){
            ++numMap[arr[i]];
        }
        printUnorderedMap(numMap);
        return 1;
    }
};
// @lc code=end

int main(){
    std::vector<int> arr {1,1,2,2,3,3,4,4,5,5};
    Solution s;
    s.threeSumMulti(arr,1);
    int test;
    ++test;
    std::cout << test << std::endl;
}