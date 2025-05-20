/*
 * @lc app=leetcode.cn id=147 lang=cpp
 *
 * [147] 对链表进行插入排序
 */

// @lc code=start
/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode() : val(0), next(nullptr) {}
 *     ListNode(int x) : val(x), next(nullptr) {}
 *     ListNode(int x, ListNode *next) : val(x), next(next) {}
 * };
 */


struct ListNode {
    int val;
    ListNode *next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode *next) : val(x), next(next) {}
}; 

#include <iostream>

class Solution {
public:
    ListNode* insertionSortList(ListNode* head) {
        if(head == nullptr || head->next == nullptr) {
            return head;
        }

        ListNode* result = head;
        ListNode* q = head->next;

        // 断开链表
        head->next = nullptr;

        while(q != nullptr) {
            ListNode* p = result;
            ListNode* pre = nullptr;
            while(p != nullptr && p->val < q->val) {
                pre = p;
                p = p->next;
            }
            if(pre == nullptr) {
                // 插入到头部
                ListNode* temp = q->next;
                q->next = result;
                result = q;
                q = temp;
            } else {
                // 插入到中间
                ListNode* temp = q->next;
                pre->next = q;
                q->next = p;
                q = temp;
            }

            // test
            // ListNode* temp = result;
            // while (temp != nullptr) {
            //     std::cout << temp->val << " ";
            //     temp = temp->next;
            // }
            // std::cout << std::endl;
        }
        return result;
    }
};
// @lc code=end

// int main() {
//     ListNode* head = new ListNode(4);
//     head->next = new ListNode(2);
//     head->next->next = new ListNode(1);
//     head->next->next->next = new ListNode(3);

//     Solution solution;
//     ListNode* sortedList = solution.insertionSortList(head);

//     while (sortedList != nullptr) {
//         std::cout << sortedList->val << " ";
//         sortedList = sortedList->next;
//     }

//     return 0;
// }