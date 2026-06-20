#include <iostream>
#include <string>

// Line comment
void hello(const std::string& name) {
    std::cout << "Hello, " << name << std::endl; // inline
}

/* block comment */
const int X = 1;

class Person {
public:
    std::string name;
};
