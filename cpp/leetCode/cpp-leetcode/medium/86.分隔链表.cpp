/*
 * @lc app=leetcode.cn id=86 lang=cpp
 *
 * [86] 分隔链表
 */

// @lc code=start
/* *
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
struct ListNode {
    int val;
    ListNode *next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode *next) : val(x), next(next) {}
};
class Solution {
public:
    ListNode* partition(ListNode* head, int x) {
        ListNode* p = head;
        ListNode* q = new ListNode();
        q->next = head;
        ListNode* newhead = q;
        ListNode* maxPtr = nullptr;
        while(p != nullptr){
            // std::cout << p->val << std::endl;
            // std::cout << "-----" << std::endl;

            if(p->val >= x && maxPtr == nullptr){
                maxPtr = q;
            }
            if(maxPtr != nullptr && p->val < x){
                q->next = p ->next;
                ListNode* r = maxPtr->next;
                maxPtr->next = p;
                maxPtr = p;
                p->next = r;
                p = q->next;
            }else{
                q = p;
                p = p->next;
            }

        }
        // std::cout << "exit continue" << std::endl;
        return newhead->next;;
    }
};
// @lc code=end

// test
int main(){
    ListNode* head = new ListNode(1);
    head->next = new ListNode(4);
    head->next->next = new ListNode(3);
    head->next->next->next = new ListNode(2);
    head->next->next->next->next = new ListNode(5);
    head->next->next->next->next->next = new ListNode(2);
    Solution s;
    ListNode* newhead = s.partition(head, 3);
    while(newhead != nullptr){
        std::cout << newhead->val << std::endl;
        newhead = newhead->next;
    }
    return 0;
}