#include <iostream>


struct PublicStruct{
    int x {};
    int y {};
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

int main(){
    // PublicStruct* ps = new PublicStruct();
    // PrivateClass* pc = new PrivateClass();

    // ps->x = 1;
    // // pc->x = 1; // error

    Point p {1,2};
    p.test();
    p.setX(3);
    p.test();

    PrivateClass p2 {1,2};
    p2.printThis();
    PrivateClass p3;
    p3.printThis();

    return 0;
}