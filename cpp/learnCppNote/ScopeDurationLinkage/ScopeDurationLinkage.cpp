#include <iostream>
#include "Constant.h"
#include "./build/ScopeDurationLinkageConfig.h"

extern constexpr int x = 1;

void cout(){
    std::cout<< "cout\n";
}

namespace mySpace{
    int x = 5;

    int add(int a, int b){
        return a+b;
    }

    void print(){
        std::cout<< x <<'\n';
    }

    namespace innerSpace{
        int x = 6;

        void print(){
            std::cout<< x <<'\n';
        }
    }

    void cout(){
        std::cout<< "cout\n";
    }
}

namespace myOtherSpace::innerSpace{
    int y = 10;
    void print(){
        std::cout<< y <<'\n';
    }
}

int main(){
    // Project Config
    std::cout<< "Project Config ------------------ " <<'\n';
    std::cout<< "ScopeDurationLinkage_VERSION_MAJOR:" << ScopeDurationLinkage_VERSION_MAJOR << '\n';
    std::cout<< "ScopeDurationLinkage_VERSION_MINOR:" << ScopeDurationLinkage_VERSION_MINOR << '\n';
    std::cout<< "ScopeDurationLinkage_VERSION_PATCH:" << ScopeDurationLinkage_VERSION_PATCH << '\n';
    // std::cout<< "Compile Time Config x:" << TIMESTAMP << '\n';

    // nameSpace Test
    std::cout<< "nameSpace Test ------------------ " <<'\n';
    mySpace::print();
    mySpace::innerSpace::print();
    mySpace::cout();
    ::cout();
    myOtherSpace::innerSpace::print();
    std::cout<< mySpace::x <<'\n';

    // Scope Test
    std::cout<< "Scope Test ------------------ " <<'\n';
    int x = 10;
    std::cout<< x <<'\n';
    {
        int x = 20;
        std::cout<< x <<'\n';
    }
    std::cout<< x <<'\n';

    // Duration Test
    std::cout<< "Duration Test ------------------ " <<'\n';
    for(int i=0; i<5; i++){
        static int x = 0;
        x++;
        std::cout<< x <<'\n';
    }
    std::cout<< x <<'\n';
    

    // Constant Test
    std::cout<< "Constant Test ------------------ " <<'\n';
    std::cout<< Constants::x <<'\n';
    std::cout<< Constants::y <<'\n';
    std::cout<< Constants::z <<'\n';
    std::cout<< Constants::value <<'\n';

    //extern Test
    std::cout<< "extern Test ------------------ " <<'\n';
    extern int g_x;
    extern int g_y;
    std::cout<< g_x <<'\n';
    std::cout<< g_y <<'\n';

    //static Test
    std::cout<< "static Test ------------------ " <<'\n';
    for(int i = 0; i<5; i++){
        static int x = 0;//只初始化一次
        x++;
        std::cout<< x <<'\n';
    }

    return 0;
}