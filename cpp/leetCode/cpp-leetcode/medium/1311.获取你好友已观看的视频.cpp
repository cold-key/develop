/*
 * @lc app=leetcode.cn id=1311 lang=cpp
 *
 * [1311] 获取你好友已观看的视频
 */

 #include <iostream>
 #include<string>
 #include<vector>
 #include<unordered_map>
 #include<map>
 using namespace std;

// @lc code=start
class Solution {
public:
    vector<string> watchedVideosByFriends(vector<vector<string>>& watchedVideos, vector<vector<int>>& friends, int id, int level) {
        vector<unordered_map<int,int>> levelTree(level+1);
        unordered_map<int,int> m ;
        for(int i = 0; i < friends[id].size();i++){
            m[friends[id][i]] = 1;
        }
        levelTree[0] = m;
        for(int i = 1; i <= level; i++){
            unordered_map<int,int> m2 ;
            for(auto &iter : levelTree[i-1]){
                // cout << iter.first << endl;
                for(int j = 0; j < friends[iter.first].size();j++){
                    m2[friends[iter.first][j]] = 1;
                }
            }
            levelTree[i] = m2;
        }

        // 输出levelTree
        // for(int i = 0; i <= level; i++){
        //     cout << "level " << i << ": ";
        //     for(auto &p : levelTree[i]){
        //         cout << p.first << " ";
        //     }
        //     cout << endl;
        // }

        map<string,int> resultMap ;
        vector<string> result;
        for(auto &p : levelTree[level - 1]){
            if(p.first == id) continue;
            for(int i = 0 ; i < watchedVideos[p.first].size(); i++){
                resultMap[watchedVideos[p.first][i]] += 1;
            }
        }
        for(auto &r : resultMap){
            // cout << r.first << endl;
            if(r.second > 0){
                result.push_back(r.first);
            }
        }
        return result;
    }
};
// @lc code=end

// test
// int main(){
//     Solution s;
//     vector<vector<string>> watchedVideos = {{"A","B"},{"C"},{"B","C"},{"D"}};
//     vector<vector<int>> friends = {{1,2},{0,3},{0,3},{1,2}};
//     vector<string> result = s.watchedVideosByFriends(watchedVideos, friends, 0, 1);
//     for(int i = 0; i < result.size(); i++){
//         cout << result[i] << " ";
//     }
//     cout << endl;
//     return 0;
// }
