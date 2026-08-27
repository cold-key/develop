/*
 * @lc app=leetcode.cn id=169 lang=cpp
 *
 * [169] 多数元素
 */
// 时间复杂度O(n)，空间O(1)的算法：Boyer-Moore 投票算法
// 拓展问题
// (1)如果题目不保证 majority 一定存在，就需要“两遍扫描”：第一遍用 Boyer–Moore 找到候选人 candidate；第二遍重新统计它的实际出现次数

// (2)如何推广到 > n/k
// 推广到 > n/k 时，可以使用 Boyer–Moore 的推广算法 Misra–Gries：
// 维护最多 k-1 个候选者及其计数。
// 遍历元素 x 时：
// 如果 x 已是候选者，对应计数 +1。
// 如果还有空候选槽，把 x 加入，计数设为 1。
// 否则所有 k-1 个候选者计数同时 -1，计数归零的候选者删除。
// 原因是：出现次数 > n/k 的元素最多只能有 k-1 个。
// 第一遍只能得到候选集合，第二遍还要重新统计，确认哪些元素确实满足：
// $$ count(x) > \frac{n}{k} $$
// 例如 > n/3 时，只需要维护 2 个候选者。

#include<vector>

using namespace std;

// @lc code=start
class Solution {
public:
    int majorityElement(vector<int>& nums) {
        int slotNum = nums[0];
        int cnt = 1;
        for(int i = 1; i < nums.size(); ++i){
            if(cnt == 0){
                cnt = 1;
                slotNum = nums[i];
                continue;
            }
            if(slotNum == nums[i]) ++cnt;
            else --cnt;
        }
        return slotNum;
    }
};
// @lc code=end