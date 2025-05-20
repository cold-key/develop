/*
 * @lc app=leetcode.cn id=148 lang=cpp
 *
 * [148] 排序链表
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

#include <iostream>
#include <vector>

struct ListNode {
    int val;
    ListNode *next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode *next) : val(x), next(next) {}
}; 

class Solution {
public:
    ListNode* sortList(ListNode* head) {
        if(head == nullptr || head->next == nullptr) {
            return head;
        }
        int pivot = head->val;
        ListNode* p = head->next;
        ListNode* pre = head;

        ListNode* bigP = nullptr;
        ListNode* bigHead = nullptr;
        while(p != nullptr) {
            if(p->val >= pivot) {

                pre->next = p->next;
                p->next = nullptr;

                if(bigP == nullptr) {
                    bigP = p;
                    bigHead = p;
                } else {
                    bigP->next = p;
                    bigP = bigP->next;
                }
            }else{
                pre = p;
            }
            p = pre->next;
        }

        pre->next = head;
        ListNode* temp = head;
        head = head->next;
        temp->next = nullptr;

        // test code
        // ListNode* test1 = head;
        // while(test1 != nullptr) {
        //     std::cout << test1->val << " ";
        //     test1 = test1->next;
        // }
        // std::cout << std::endl;
        // ListNode* test2 = bigHead;
        // while(test2 != nullptr) {
        //     std::cout << test2->val << " ";
        //     test2 = test2->next;
        // }
        // std::cout << std::endl;

        ListNode* left = sortList(head);
        ListNode* right = sortList(bigHead);

        ListNode* i = left;
        while(i != nullptr && i->next != nullptr) {
            i = i->next;
        }
        if(i != nullptr) {
            i->next = right;
        } else {
            left = right;
        }

        return left;
    }
};
// @lc code=end

int main() {
    std::vector<int> nums = {4,19,14,5,-3,1,8,5,11,15};

    ListNode* head = new ListNode(nums[0]);
    ListNode* tail = head;
    for(int i = 1; i < nums.size(); ++i) {
        tail->next = new ListNode(nums[i]);
        tail = tail->next;
    }

    Solution solution;
    ListNode* sortedList = solution.sortList(head);

    while(sortedList != nullptr) {
        std::cout << sortedList->val << " ";
        sortedList = sortedList->next;
    }
    std::cout << std::endl;

    return 0;
}