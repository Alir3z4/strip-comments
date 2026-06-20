package main

import "fmt"

// Line comment
func Hello(name string) {
	fmt.Printf("Hello, %s\n", name) // inline
}

/* block comment */
const X = 1

type Person struct {
	Name string
}
