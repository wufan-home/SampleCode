#include <iostream>

using namespace std;

class testClass
{
public:
    testClass(int size) { cout << size << endl; }
};

int main()
{
    testClass *ptr = new testClass[10];
    delete[] ptr;
    return 1;
}
