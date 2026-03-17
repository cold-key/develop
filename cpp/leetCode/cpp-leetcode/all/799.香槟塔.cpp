/*
 * @lc app=leetcode.cn id=799 lang=cpp
 *
 * [799] 香槟塔
 */

 #include<iostream>
 #include<vector>
 #include<algorithm>

 #include"lib/tool.h"

 using namespace std;

// @lc code=start
class Solution {
public:
    double champagneTower(int poured, int query_row, int query_glass) {
        double ans =0;
        std::vector<double> last_row(1,0);
        last_row[0] = poured - 1;
        for(int i = 1; i <  query_row; i++){
            // std::cout << "last_row: " << i - 1 << "   ";
            // printVector(last_row);
            std::vector<double> cur_row(i+1,0);
            for(int j = 0; j <= i; j++){
                double left_output = (j-1>=0?last_row[j-1]:0) / 2;
                double right_output = ((j < i)?last_row[j]:0) / 2;
                // std::cout << left_output << " , " << right_output << std::endl;
                cur_row[j] = std::max(double((left_output + right_output) - 1),0.0);
            }
            last_row = cur_row;
        }
        // printVector(last_row);
        ans =  ((query_glass-1>=0?last_row[query_glass-1]:0) + last_row[query_glass]) /2.0;
        return ans;
    }
};

// AI修正版
// class Solution {
// public:
//     double champagneTower(int poured, int query_row, int query_glass) {
//         // 第0行特殊处理
//         if (query_row == 0) {
//             return min(poured, 1);
//         }
        
//         // last_row[i] = 上一行第i个杯子的溢出量
//         vector<double> last_row(1, max(poured - 1.0, 0.0));
        
//         // 计算到第 query_row - 1 行的溢出
//         for (int i = 1; i < query_row; i++) {
//             vector<double> cur_row(i + 1, 0);
//             for (int j = 0; j <= i; j++) {
//                 double left_overflow = (j - 1 >= 0) ? last_row[j - 1] / 2 : 0;
//                 double right_overflow = (j < i) ? last_row[j] / 2 : 0;
//                 double inflow = left_overflow + right_overflow;
//                 cur_row[j] = max(inflow - 1.0, 0.0);  // 当前杯子的溢出量
//             }
//             last_row = cur_row;
//         }
        
//         // 计算第 query_row 行第 query_glass 个杯子的流入量
//         double left_inflow = (query_glass - 1 >= 0) ? last_row[query_glass - 1] / 2 : 0;
//         double right_inflow = (query_glass < last_row.size()) ? last_row[query_glass] / 2 : 0;
//         double total_inflow = left_inflow + right_inflow;
        
//         return min(total_inflow, 1.0);
//     }
// };

// 官方题解
// class Solution {
// public:
//     double champagneTower(int poured, int query_row, int query_glass) {
//         vector<double> row = {(double)poured};
//         for (int i = 1; i <= query_row; i++) {
//             vector<double> nextRow(i + 1, 0.0);
//             for (int j = 0; j < row.size(); j++) {
//                 double volume = row[j];
//                 if (volume > 1) {
//                     nextRow[j] += (volume - 1) / 2;
//                     nextRow[j + 1] += (volume - 1) / 2;
//                 }
//             }
//             row = nextRow;
//         }            
//         return min(1.0, row[query_glass]);
//     }
// };

// @lc code=end

int main(){
    Solution s;
    std::cout << s.champagneTower(25,6,1);
    return 0;
}

// 错误1：初始状态错误
// last_row[0] = poured - 1;  // ❌ 问题：如果 poured <= 1，溢出量是负数
// last_row[0] = max(poured - 1.0, 0.0);  // ✅ 溢出量不能为负

// 错误3：答案计算错误（最严重）, 运算符优先级 bug！ ?: 优先级低于 +

// ans = (query_glass-1>=0 ? last_row[query_glass-1] : 0 + last_row[query_glass]) / 2.0;
// 实际解析为
// ans = (query_glass-1>=0 ? last_row[query_glass-1] : (0 + last_row[query_glass])) / 2.0;
// 当 query_glass-1 >= 0 时，返回 last_row[query_glass-1]，完全没加 last_row[query_glass]！