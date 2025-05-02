// 排序算法

#include<iostream>
#include<vector>

using namespace std;

void quickSort(vector<int>& a, int left, int right);
void insertSort(vector<int>& a);

int main(){
    vector<int> arr {5,6,9,1,8,10,65,98,30,100,66,24,35,87,69};
    // quickSort(arr,0,arr.size()-1);
    insertSort(arr);
    for(int i = 0; i < arr.size(); i++){
        cout << arr[i] <<" , ";
    }
    return 0;
}

void quickSort(vector<int>& a, int left, int right) {
    if (left < right) {
        // 三数取中法选择基准元素
        int mid = left + (right - left) / 2;
        if (a[left] > a[mid]) swap(a[left], a[mid]);
        if (a[mid] > a[right]) swap(a[mid], a[right]);
        if (a[left] > a[mid]) swap(a[left], a[mid]);

        int pivot = a[mid];
        swap(a[mid], a[right]); // 将基准元素移到数组末尾

        int i = left;
        int j = right - 1;

        while (true) {
            while (a[i] < pivot && i < right) i++;
            while (a[j] > pivot && j > left) j--;
            if (i >= j) break;
            swap(a[i], a[j]);
        }

        swap(a[i], a[right]); // 将基准元素放到正确的位置

        quickSort(a, left, i - 1);
        quickSort(a, i + 1, right);
    }
}

void insertSort(vector<int>& a) {
    for(int i = 0; i < a.size(); i++){
        int num = a[i];
        for(int j = i - 1; j >= 0; j--){
            if(a[j] > num){
                a[j+1] = a[j];
            }else{
                a[j+1] = num;
                break;
            }
        }
    }
}