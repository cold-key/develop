/*
 * @lc app=leetcode.cn id=679 lang=cpp
 *
 * [679] 24 点游戏
 */
#include<stdio.h>
#include<iostream>
#include<vector>
#include <unordered_set>

using namespace std;

// @lc code=start
class Solution {
public:

    std::vector<float(*)(float,float)> funcs = {add, subOne, subTwo, mul, divOne, divTwo};

    bool judgePoint24(vector<int>& cards) {
        vector<float> cards_float (cards.begin(),cards.end());
        unordered_set<int> maskIndexMap;
        return judgePointN(cards_float, 24.0, maskIndexMap);
    }

    bool judgePointN(vector<float>& cards, float n, unordered_set<int>& maskIndexMap){
        if(cards.size() == 1 ){
            //
        }
        for(int i = 0; i < funcs.size(); i++){
            for(int j = 0; j < cards.size(); j++){
                if(maskIndexMap.count(j)){
                    continue;
                }
                float nextN = funcs[i](n,cards[j]);
                cout << "n : " << n << "  cards[j] : " << cards[j] << "  nextN : " << nextN << endl;
                maskIndexMap.insert(j);
                if(judgePointN(cards, nextN, maskIndexMap)){
                    return true;
                }else{
                    maskIndexMap.erase(j);
                }
            }
        }
        return false;
    }

    static float add(float x, float y){
        return x + y;
    }

    static float subOne(float x, float y){
        return x - y;
    }

    static float subTwo(float x, float y){
        return y - x;
    }

    static float mul(float x, float y){
        return x * y;
    }

    static float divOne(float x, float y){
        return x / y;
    }

    static float divTwo(float x, float y){
        return y / x;
    }
};
// @lc code=end

int main(){
    vector<int> test {4,1,8,7};
    Solution s;
    cout << s.judgePoint24(test);
}