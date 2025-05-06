/*
 * @lc app=leetcode.cn id=61 lang=cpp
 *
 * [61] 旋转链表
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

class Solution {
public:
    ListNode* rotateRight(ListNode* head, int k) {
        if(head == nullptr || k == 0){
            return head;
        }
        int listLength = 0;
        ListNode* p = head;
        while(p->next != nullptr){
            listLength++;
            p = p->next;
        }
        listLength++;
        p->next = head;

        k %= listLength;

        int needMoveTimes = listLength - k;
        while(needMoveTimes > 0){
            p=p->next;
            needMoveTimes--;
        }
        head = p->next;
        p->next = nullptr;
        return head;
    }
};
// @lc code=end

