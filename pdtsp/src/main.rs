use std::env;
mod parser;
use parser::read_instance;
enum MODE {
    Iterative,
    Gloutonne,
}
fn main() {
    println!("PD TSP");
    let mut instance_name = String::from("n20mosA.tsp");
    let mut mode = MODE::Gloutonne;
    if env::args().len() > 1 {
        if env::args().nth(1).unwrap() == "1" {
            mode = MODE::Iterative;
        }
    }
    let file = read_instance(instance_name);
    match mode {
        MODE::Gloutonne => {}
        MODE::Iterative => {}
    }
}
