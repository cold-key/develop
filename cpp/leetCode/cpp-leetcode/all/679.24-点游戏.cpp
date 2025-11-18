/*
 * @lc app=leetcode.cn id=679 lang=cpp
 *
 * [679] 24 点游戏
 */
#include<stdio.h>
#include<iostream>
#include<vector>
#include<unordered_set>
#include<cstdlib>
#include<float.h>

using namespace std;

// @lc code=start
class Solution {
public:

    std::vector<float(*)(float,float)> funcs = {add, subOne, subTwo, mul, divOne, divTwo};

    bool judgePoint24(vector<int>& cards) {
        vector<float> cards_float (cards.begin(),cards.end());
        unordered_set<int> maskIndexMap;
        bool stackBool = judgePointN(cards_float, 24.0, maskIndexMap);
        if(stackBool){
            return stackBool;
        }
        bool twoResultBool = false;
        for(int i = 0; i < cards.size(); i++){
            for(int j = i + 1; j < cards.size(); j++){
                for(int  k = 0; k < funcs.size(); k++){
                    cards_float.clear();
                    maskIndexMap.clear();

                    float tempNum = funcs[i](cards[i],cards[j]);
                    cards_float.push_back(tempNum);
                    for(int l = 0; l < cards.size(); l++){
                        if(l != i && l != j ){
                            cards_float.push_back(cards[l]);
                        }
                    }

                    bool tempResult = judgePointN(cards_float, 24.0, maskIndexMap);
                    if(tempResult){
                        // for(int x = 0; x < cards_float.size(); x++){
                        //     std::cout << cards_float[x] << ",";
                        // }
                        // std::cout << "\n";
                        return tempResult;
                    }
                }
            }
        }
        return twoResultBool;
    }

    bool judgePointN(vector<float>& cards, float n, unordered_set<int>& maskIndexMap){
        if(maskIndexMap.size() == cards.size() - 1){
            float lastNum = cards[0];
            for(int i = 0; i < cards.size(); i++){
                if(!maskIndexMap.count(i)){
                    lastNum = cards[i];
                }
            }
            return abs(n - lastNum) < 0.00001;
        }
        for(int i = 0; i < funcs.size(); i++){
            for(int j = 0; j < cards.size(); j++){
                if(maskIndexMap.count(j)){
                    continue;
                }
                float nextN = funcs[i](n,cards[j]);
                if(cards[j] == 0 && nextN == 0){
                    nextN = FLT_MAX;
                }
                // cout << "n : " << n << "  cards[j] : " << cards[j] << "  nextN : " << nextN << endl;
                maskIndexMap.insert(j);
                if(judgePointN(cards, nextN, maskIndexMap)){
                    // cout << nextN << endl;
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
        if(abs(y)<0.00001){
            return FLT_MAX;
        }
        return x / y;
    }

    static float divTwo(float x, float y){
        if(abs(x)<0.00001){
            return FLT_MAX;
        }
        return y / x;
    }
};
// @lc code=end

// int main(){
//     vector<int> test {1,7,1,7};
//     Solution s;
//     cout << s.judgePoint24(test);
// }