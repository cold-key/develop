#include<iostream>

using namespace std;

class Widget {
    int* data;
public:
    Widget() : data(new int[1000]) { std::cout << "Default\n"; }
    Widget(const Widget& w) : data(new int[1000]) {
        std::copy(w.data, w.data+1000, data);
        std::cout << "Copy\n";
    }
    Widget(Widget&& w) noexcept : data(w.data) {
        w.data = nullptr;
        std::cout << "Move\n";
    }
    ~Widget() { delete[] data; std::cout << "Destroy\n"; }
};

Widget createWidget() {
    Widget w;
    return w;
}

int main() {
    Widget w1;
    Widget w2 = w1;
    Widget w3 = createWidget();
    Widget w4 = std::move(w1);
    return 0;
}