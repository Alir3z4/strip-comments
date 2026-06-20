// Module comment
const std = @import("std");

// Function comment
fn greet(name: []const u8) []const u8 {
    // Inline comment
    return "Hello";
}

// Struct comment
const Greeter = struct {
    fn greet() []const u8 {
        return "hi";
    }
};
