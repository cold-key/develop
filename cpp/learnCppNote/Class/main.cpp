#include <iostream>


struct PublicStruct{
    int x {};
    int y {};

    void printThis(){
        std::cout << "x: " << x << " y: " << y << std::endl;
    }
};

class PrivateClass{
    int x {};
    int y {};

    public:
        PrivateClass() = default;
        PrivateClass(int x, int y) : x{x},y{y}{
                
            }
        int getX() const { return x; }
        int getY() const { return y; }

        void printThis(){
            std::cout << "x: " << x << " y: " << y << std::endl;
        }

};

class Point{
    private:
        int x {};
        int y {};
        int& refX;
    public:
        Point(int x, int y) : x{x},y{y},refX{x}{
        }
        int getX() const { return x; }
        void setX(int x) { this->x = x; }
        int getY() const { return y; }
        void test(){
            std::cout << refX << std::endl;
        }
};

class ClassOne{
    private:
        int x;
        int y;
    public:
        ClassOne() = default;
        ClassOne(const ClassOne& other) : x{other.x},y{other.y}{
            std::cout << "Copy constructor" << std::endl;
        }
        ClassOne(int x) : ClassOne(x,1){}
        ClassOne(int x, int y) : x{x},y{y}{}

        int getX() const { return x; }
        int getY() const { return y; }

        void printThis(){
            std::cout << "x: " << x << " y: " << y << std::endl;
        }
};

int main(){

    PublicStruct ps;
    ps.printThis();

    // PublicStruct* ps = new PublicStruct();
    // PrivateClass* pc = new PrivateClass();

    // ps->x = 1;
    // // pc->x = 1; // error

    // Point p {1,2};
    // p.test();
    // p.setX(3);
    // p.test();

    // PrivateClass p2 {1,2};
    // p2.printThis();
    // PrivateClass p3;
    // p3.printThis();

    // ClassOne c1 {1};
    // c1.printThis();

    // ClassOne c2  = c1;
    return 0;
}