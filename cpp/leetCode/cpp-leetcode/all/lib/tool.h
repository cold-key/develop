#include<vector>
#include<iostream>
#include<string>
#include<algorithm>
#include<unordered_set>

// LeetCode刷题本地调试用的tool.h

struct ListNode {
    int val;
    ListNode *next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode *next) : val(x), next(next) {}
};

template <typename T>
void printVector(std::vector<T> vector){
    for(auto it = vector.begin(); it != vector.end(); ++it){
        std::cout << *it << " , ";
    }
    std::cout << "\n" ;
}

void printLinkList(ListNode* head){
    ListNode* p = head;
    while(p != nullptr){
        std::cout << p->val << " , ";
        p = p->next;
    }
    std::cout << "\n";
}

template<typename T>
void printUnorderedSet(std::unordered_set<T>& set){
    for(auto it = set.begin(); it != set.end(); ++it){
        std::cout << *it << " , ";
    }
    std::cout << std::endl;
}

// std::vector<int> getVector1ByLeetCodeStr

//