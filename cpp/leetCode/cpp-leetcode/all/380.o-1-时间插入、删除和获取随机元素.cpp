/*
 * @lc app=leetcode.cn id=380 lang=cpp
 *
 * [380] O(1) 时间插入、删除和获取随机元素
 */

#include<vector>
#include<unordered_map>
#include <random>
#include<iostream>

using namespace std;

// @lc code=start
class RandomizedSet {
public:
    RandomizedSet() {
        
    }
    
    bool insert(int val) {
        if(indices.contains(val)){
            return false;
        }
        int len = nums.size();
        indices.insert({val,len});
        nums.push_back(val);
        return true;
    }
    
    bool remove(int val) {
        if(!indices.contains(val)){
            return false;
        }
        int index = indices[val];
        int lastVal = nums.back();
        
        // 先更新末尾元素的索引（如果不同的话）
        if (index != nums.size() - 1) {
            indices[lastVal] = index;
            nums[index] = lastVal;
        }
        
        indices.erase(val);
        nums.pop_back();
        return true;
    }
    
    int getRandom() {
        return nums[int(dis(gen) * nums.size())];
    }
private:
    vector<int> nums;
    unordered_map<int, int> indices;
    std::mt19937 gen {std::random_device{}()};
    std::uniform_real_distribution<> dis {0,1};
};

/**
 * Your RandomizedSet object will be instantiated and called as such:
 * RandomizedSet* obj = new RandomizedSet();
 * bool param_1 = obj->insert(val);
 * bool param_2 = obj->remove(val);
 * int param_3 = obj->getRandom();
 */
// @lc code=end

int main(){
    RandomizedSet* obj = new RandomizedSet();
    bool param_1 = obj->insert(1);
    // bool param_2 = obj->remove(2);
    // int param_3 = obj->getRandom();
    bool param_4 = obj->insert(3);
    // bool param_5 = obj->remove(1);
    bool param_6 = obj->insert(4);
    // bool param_7 = obj->remove(3);
    int param_8 = obj->getRandom();

    std::cout << param_1 << std::endl;
    // std::cout << param_2 << std::endl;
    // std::cout << param_3 << std::endl;
    std::cout << param_4 << std::endl;
    // std::cout << param_5 << std::endl;
    std::cout << param_6 << std::endl;
    // std::cout << param_7 << std::endl;
    std::cout << param_8 << std::endl;


    return 0;
}