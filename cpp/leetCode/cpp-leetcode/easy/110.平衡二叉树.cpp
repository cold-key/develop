/*
 * @lc app=leetcode.cn id=110 lang=cpp
 *
 * [110] 平衡二叉树
 */

// @lc code=start
/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */

struct TreeNode {
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
};

#include<cmath>
#include <algorithm>
using namespace std;
class Solution {
public:
    bool isBalanced(TreeNode* root) {
        if(root == nullptr){
            return true;
        }
        int leftHigh = getTreeHigh(root->left);
        int rightHigh = getTreeHigh(root->right);
        return isBalanced(root->left) && isBalanced(root->right) && abs(leftHigh - rightHigh) <= 1;
    }

    int getTreeHigh(TreeNode* root){
        if(root == nullptr){
            return 0;
        }else{
            return max(getTreeHigh(root->left) , getTreeHigh(root->right)) + 1;
        }
    }
};
// @lc code=end

