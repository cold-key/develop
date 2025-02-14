#include <iostream>

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

    return 0;
}