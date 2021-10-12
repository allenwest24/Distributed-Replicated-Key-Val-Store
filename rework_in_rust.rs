// This file is the Rust re-work (obviously a lot left to do) of the Python Distributed KVS algorithm I designed loosely based
// on Raft.

// Imports.
use std::collections::HashMap;

// Global Variables.

// Storage methods being used must be Key-Value oriented.
let mut log = HashMap::new();
let mut kvs = HashMap::new();
// A node enters as a follower by default.
let mut state = "follower";
// A randomly chosen integer in a given range to differentiate tolerance times.
let elect_to : i32 = 0; //TODO: Make this a random value in a range.
