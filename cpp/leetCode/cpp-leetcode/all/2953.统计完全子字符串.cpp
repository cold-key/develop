/*
 * @lc app=leetcode.cn id=2953 lang=cpp
 *
 * [2953] 统计完全子字符串
 */

#include<string>
#include<iostream>
#include<unordered_map>
#include<cmath>

using namespace std;

// @lc code=start
class Solution {
public:
    int countCompleteSubstrings(string word, int k) {
        int ans = 0;
        int widthIndex = 1;
        for(int w = k ; w <= word.size(); w = k * widthIndex){
            if(widthIndex > 26){
                break;
            }
            // std::cout << "width: "<< w<<std::endl;
            int leftIndex = 0;
            int rightIndex = 0;
            std::unordered_map<char,int> cntMap;
            while(rightIndex < word.size()){
                // std::cout << leftIndex << " , " << rightIndex << std::endl;
                if(rightIndex - 1 >=0 && abs((word[rightIndex] - word[rightIndex - 1]))>2 && w > 1){
                    leftIndex = rightIndex;
                    cntMap.clear();
                    cntMap.insert({char(word[rightIndex]),1});
                    ++rightIndex;
                    continue;
                }
                if(rightIndex - leftIndex + 1 < w){
                    if(cntMap.contains(word[rightIndex])){
                        ++cntMap[word[rightIndex]];
                    }else{
                        cntMap.insert({char(word[rightIndex]),1});
                    }
                    ++rightIndex;
                }else if(rightIndex - leftIndex + 1 == w){
                    if(cntMap.contains(word[rightIndex])){
                        ++cntMap[word[rightIndex]];
                    }else{
                        cntMap.insert({char(word[rightIndex]),1});
                    }
                    bool isAns = true;
                    for(auto it = cntMap.begin(); it != cntMap.end(); ++it){
                        if(it->second != k  && it->second > 0){
                            isAns = false;
                            break;
                        }
                    }
                    ans = isAns ? ans + 1: ans;
                    ++rightIndex;
                    // if(isAns){
                    //     std::cout << "ans str: " << word.substr(leftIndex,rightIndex - leftIndex) << std::endl;
                    // }
                }else{
                    if(cntMap.contains(word[rightIndex])){
                        ++cntMap[word[rightIndex]];
                    }else{
                        cntMap.insert({char(word[rightIndex]),1});
                    }
                    --cntMap[word[leftIndex]];
                    ++rightIndex;
                    ++leftIndex;
                    bool isAns = true;
                    for(auto it = cntMap.begin(); it != cntMap.end(); ++it){
                        // std::cout<< it->first << " , " << it->second << std::endl;
                        if(it->second != k && it->second > 0){
                            isAns = false;
                            break;
                        }
                    }
                    // if(isAns){
                    //     std::cout << "ans str: " << word.substr(leftIndex,rightIndex - leftIndex) << std::endl;
                    // }
                    ans = isAns ? ans + 1: ans;
                }
            }
            ++widthIndex;
            // std::cout << "ans : " << ans << std::endl;
            // std::cout << leftIndex << " , " << rightIndex << std::endl;
        }
        return ans;
    }
};
// @lc code=end

// int main(){
//     Solution s;
//     std::cout <<s.countCompleteSubstrings("hmfttfmhpttmpphmhthfpffphftfhthtmhthhfphfmmm",1);
// }


// 暴力法
// 759/759 cases passed (1664 ms)
// Your runtime beats 9.56 % of cpp submissions
// Your memory usage beats 12.17 % of cpp submissions (246.3 MB)

// TODO 后续复习优化方向
// 1. 参考题解进行修改
// 2. unordered_map改vector
// 3. 跳跃index