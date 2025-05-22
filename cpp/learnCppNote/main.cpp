#include<iostream>

using namespace std;

class A{
public:
    A(int a, int b, int c):a(a),b(b),c(c) {
        cout << "A constructor" << endl;
    };
    void printSelf() {
        cout << "a: " << a << " b: " << b << " c: " << c << endl;
    };
    int a;
    int b;
    const int c;
};

int main()
{
    cout << "test"<<"\n";
    A a(1,2,3);
    a.printSelf();
    return 0;
}