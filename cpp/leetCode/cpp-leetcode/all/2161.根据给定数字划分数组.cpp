/*
 * @lc app=leetcode.cn id=2161 lang=cpp
 *
 * [2161] 根据给定数字划分数组
 */

#include <vector>
#include <iostream>
#include <algorithm>

using namespace std;

// @lc code=start

// ============================================================
// 自实现 std::stable_partition（分治 + 旋转）
// 标准库的做法：
//   有足够临时 buffer → O(n) 缓冲方案
//   没有              → O(n log n) 分治方案（如下）
// ============================================================

class Solution {
    // rotate: 把 [first, middle) 和 [middle, last) 互换位置
    // 例: [1,2,3 | 4,5,6] rotate 到 middle=4 → [4,5,6 | 1,2,3]
    // 经典实现：三次 reverse
    static void my_rotate(vector<int>::iterator first,
                          vector<int>::iterator middle,
                          vector<int>::iterator last) {
        if (first == middle || middle == last) return;
        // reverse [first, middle)
        std::reverse(first, middle);
        // reverse [middle, last)
        std::reverse(middle, last);
        // reverse [first, last)
        std::reverse(first, last);
    }

    // divide-and-conquer stable_partition
    // 返回第一个不满足 pred 的位置（即满足区域的尾后迭代器）
    template<typename Pred>
    static vector<int>::iterator my_stable_partition(
            vector<int>::iterator first,
            vector<int>::iterator last,
            Pred pred) {

        auto len = last - first;
        if (len == 0) return last;
        if (len == 1) {
            return pred(*first) ? last : first;
        }

        // 1. 分：分成左右两半，各自递归
        auto mid = first + len / 2;
        auto left_end  = my_stable_partition(first, mid, pred);
        auto right_end = my_stable_partition(mid, last, pred);

        // 2. 治：此时布局为
        //    [first ... left_end)  true
        //    [left_end ... mid)    false
        //    [mid ... right_end)   true
        //    [right_end ... last)  false
        //
        //    中间两块 [left_end, mid) 和 [mid, right_end) 互换 → rotate
        //    结果: true | true | false | false
        my_rotate(left_end, mid, right_end);

        // 新的 true/false 分界线
        return left_end + (right_end - mid);
    }

public:
    vector<int> pivotArray(vector<int>& nums, int pivot) {
        // 第一趟：< pivot 的稳定排到前面，>= pivot 的排后面
        auto mid = my_stable_partition(
            nums.begin(), nums.end(),
            [pivot](int x) { return x < pivot; });

        // 第二趟：在 >= pivot 的区域里，== pivot 排到 > pivot 前面
        my_stable_partition(
            mid, nums.end(),
            [pivot](int x) { return x == pivot; });

        return nums;
    }
};
// @lc code=end

int main() {
    Solution s;
    // 测试1: {9,12,5,10,14,3,10}, pivot=10 → 期望 {9,5,3,10,10,12,14}
    vector<int> nums1 = {9, 12, 5, 10, 14, 3, 10};
    s.pivotArray(nums1, 10);
    std::cout << "Test1: ";
    for(int i : nums1) std::cout << i << " ";
    std::cout << std::endl;

    // 测试2: {-3,4,3,2}, pivot=2 → 期望 {-3,2,4,3}
    vector<int> nums2 = {-3, 4, 3, 2};
    s.pivotArray(nums2, 2);
    std::cout << "Test2: ";
    for(int i : nums2) std::cout << i << " ";
    std::cout << std::endl;

    // 测试3: {1,2,3,4,5}, pivot=3 → 期望 {1,2,3,4,5}
    vector<int> nums3 = {1, 2, 3, 4, 5};
    s.pivotArray(nums3, 3);
    std::cout << "Test3: ";
    for(int i : nums3) std::cout << i << " ";
    std::cout << std::endl;

    // 测试4: 全相等 pivot → 期望不变
    vector<int> nums4 = {5, 5, 5, 5};
    s.pivotArray(nums4, 5);
    std::cout << "Test4: ";
    for(int i : nums4) std::cout << i << " ";
    std::cout << std::endl;

    // 测试5: 多个 ==pivot 穿插在 > 和 < 之间
    vector<int> nums5 = {8, 3, 5, 1, 5, 9, 5, 2};
    s.pivotArray(nums5, 5);
    // 期望: <5: {3,1,2} 按原序; ==5: {5,5,5} 按原序; >5: {8,9} 按原序
    // → {3,1,2,5,5,5,8,9}
    std::cout << "Test5: ";
    for(int i : nums5) std::cout << i << " ";
    std::cout << " (expect: 3 1 2 5 5 5 8 9)";
    std::cout << std::endl;

    return 0;
}