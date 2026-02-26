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

#include<vector>
#include<iostream>
#include<utility>
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
        int len = 0;
        ListNode* p = head;
        while(p != nullptr){
            ++len;
            p = p->next;
        }
        if(len <= 1){
            return head;
        }

        ListNode* preHeadList = new ListNode();
        preHeadList->next = head;
        
        for(int size = 1;; size <<=1){
            if(size >= len){
                // std::cout << "enter \n";
                ListNode* left = preHeadList->next;
                ListNode* right = nullptr;
                ListNode* preHead = preHeadList;
                ListNode* p = left;
                int i = 1;
                while(i != size >> 1){
                    p = p->next;
                    ++i;
                }
                right = p->next;
                p->next = nullptr;
                // printLinkList(left);
                // printLinkList(right);
                std::pair<ListNode*,ListNode*> mergePair = merge(left,right);
                ListNode* mergeHead = mergePair.first;
                // printLinkList(mergeHead);
                preHeadList->next = mergeHead;

                break;
            }
            ListNode* left = preHeadList->next;
            ListNode* right = nullptr;
            ListNode* preHead = preHeadList;
            p = left;
            int i = 1;
            while(p != nullptr){
                if(i == size){
                    if(right == nullptr){
                        right = p->next;
                        p->next = nullptr;
                        p = right;
                        i = 1;
                    }else{
                        ListNode* temp = p->next;
                        p->next = nullptr;
                        std::pair<ListNode*,ListNode*> mergePair = merge(left,right);
                        ListNode* mergeHead = mergePair.first;
                        ListNode* tail = mergePair.second;
                        if(preHead != nullptr){
                            preHead->next = mergeHead;
                        }
                        preHead = tail;

                        p = temp;
                        left = temp;
                        right = nullptr;
                        i = 1;
                    }
                }else{
                    ++i;
                    p = p->next;
                }
            }
            if(left != nullptr || right != nullptr){
                std::pair<ListNode*,ListNode*> mergePair = merge(left,right);
                ListNode* mergeHead = mergePair.first;
                if(preHead != nullptr){
                    preHead->next = mergeHead;
                }
            }

            // std:: cout << "size = " << size << "\n";
            // printLinkList(preHeadList->next);
        }
        return preHeadList->next;
    }

    std::pair<ListNode*, ListNode*> merge(ListNode* left, ListNode* right){
        ListNode* p = new ListNode();
        ListNode* head = p;
        // printLinkList(left);
        // printLinkList(right);
        while(left != nullptr && right != nullptr){
            if(left->val < right->val){
                p->next = left;
                p = p->next;
                left = left->next;
            }
            else{
                p->next = right;
                p = p->next;
                right = right->next;
            }
        }
        if(left == nullptr){
            p->next = right;
        }
        else{
            p->next = left;
        }
        ListNode* result = head->next;
        head->next = nullptr;
        // delete head;
        ListNode* tail = nullptr;
        while(p->next != nullptr){
            p = p->next;
        }
        tail = p;
        return std::make_pair(result,tail);
    }

    void printLinkList(ListNode* head){
        ListNode* p = head;
        while(p != nullptr){
            std::cout << p->val << " , ";
            p = p->next;
        }
        std::cout << "\n";
    }
};
// @lc code=end

int main(){
    std::vector<int> arr {-1,5,3,4,0};
    ListNode* preHead = new ListNode();
    ListNode* p = preHead;
    for(int v : arr){
        ListNode* q = new ListNode(v);
        p->next = q;
        p = p->next;
    }
    preHead = preHead->next;
    Solution s;
    s.printLinkList(preHead);
    ListNode* sortHead =  s.sortList(preHead);
    s.printLinkList(sortHead);


    // test merge
    // Solution s;
    // std::vector<int> arr1 {1,4,34,102,188,304,400,642};
    // ListNode* preHead1 = new ListNode();
    // ListNode* p1 = preHead1;
    // for(int v : arr1){
    //     ListNode* q = new ListNode(v);
    //     p1->next = q;
    //     p1 = p1->next;
    // }
    // preHead1 = preHead1->next;
    // std::vector<int> arr2 {101,230,400,441,461,534,664,834};
    // ListNode* preHead2 = new ListNode();
    // ListNode* p2 = preHead2;
    // for(int v : arr2){
    //     ListNode* q = new ListNode(v);
    //     p2->next = q;
    //     p2 = p2->next;
    // }
    // preHead2 = preHead2->next;
    // s.printLinkList(preHead1);
    // s.printLinkList(preHead2);
    // ListNode* result = s.merge(preHead1,preHead2);
    // s.printLinkList(result);
}