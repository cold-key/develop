#include<iostream>
#include<vector>
#include<random>
#include<algorithm>

int main(){
    std::vector testShuffle {1,2,3,4,5,6,7,8,9,10};
    std::random_device rd;
    std::mt19937 g(rd());
    std::shuffle(testShuffle.begin(), testShuffle.end(),g);
    for(int value : testShuffle){
        std::cout<<value<<",";
    }
    return 0;
}