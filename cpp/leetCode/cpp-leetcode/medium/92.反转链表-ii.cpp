/*
 * @lc app=leetcode.cn id=92 lang=cpp
 *
 * [92] 反转链表 II
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
    ListNode* reverseBetween(ListNode* head, int left, int right) {
        ListNode* newHead = new ListNode();
        newHead->next = head;
        ListNode* p = newHead;
        int nowIndex = 0;

        ListNode* f = nullptr;
        ListNode* fn = nullptr;

        while(p != nullptr){
            if(nowIndex == left - 1){
                f = p;
                fn = p->next;
                p=p->next;
            }else if(nowIndex > left && nowIndex <= right && left != right){
                ListNode* needMove = p;
                p = p->next;
                needMove->next = f->next;
                f->next = needMove;
            }else if(nowIndex == right + 1){
                fn->next = p;
                p = p->next;
            }else{
                p = p->next;
            }
            ++nowIndex;
        }
        if(nowIndex == right +1){
            fn->next = nullptr;
        }
        head = newHead->next;
        delete newHead;
        return head;
    }
};
// @lc code=end

