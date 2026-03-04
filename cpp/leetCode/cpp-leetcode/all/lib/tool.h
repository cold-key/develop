#include<vector>
#include<iostream>

template <typename T>
void printVector(std::vector<T> vector){
    for(auto it = vector.begin(); it != vector.end(); ++it){
        std::cout << *it << " , ";
    }
    std::cout << "\n" ;
}