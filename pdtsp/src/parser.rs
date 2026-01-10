use std::collections::HashMap;

#[derive(Debug)]
pub struct TspInstance {
    pub name: String,
    pub comment: Option<String>,
    pub dimension: usize,
    pub capacity: Option<i32>,
    pub edge_weight_type: Option<String>,
    pub node_coords: HashMap<usize, (f64, f64)>,
    pub display_coords: HashMap<usize, (i32, i32)>,
    pub demands: HashMap<usize, i32>,
}

pub fn parse_tsp(input: &str) -> Result<TspInstance, String> {
    let mut name = None;
    let mut comment = None;
    let mut dimension = None;
    let mut capacity = None;
    let mut edge_weight_type = None;

    let mut node_coords = HashMap::new();
    let mut display_coords = HashMap::new();
    let mut demands = HashMap::new();

    enum Section {
        None,
        NodeCoord,
        Display,
        Demand,
    }

    let mut section = Section::None;

    for line in input.lines() {
        let line = line.trim();
        if line.is_empty() {
            continue;
        }

        match line {
            "NODE_COORD_SECTION" => {
                section = Section::NodeCoord;
                continue;
            }
            "DEMAND_SECTION" => {
                section = Section::Demand;
                continue;
            }
            "EOF" => break,
            _ if line.starts_with("DISPLAY_DATA_SECTION") => {
                section = Section::Display;
                continue;
            }
            _ => {}
        }

        match section {
            Section::None => {
                if let Some((key, value)) = line.split_once(':') {
                    let key = key.trim();
                    let value = value.trim();

                    match key {
                        "NAME" => name = Some(value.to_string()),
                        "COMMENT" => comment = Some(value.to_string()),
                        "DIMENSION" => {
                            dimension =
                                Some(value.parse::<usize>().map_err(|_| "Invalid DIMENSION")?)
                        }
                        "CAPACITY" => {
                            capacity = Some(value.parse::<i32>().map_err(|_| "Invalid CAPACITY")?)
                        }
                        "EDGE_WEIGHT_TYPE" => edge_weight_type = Some(value.to_string()),
                        _ => {}
                    }
                }
            }

            Section::NodeCoord => {
                let parts: Vec<_> = line.split_whitespace().collect();
                if parts.len() != 3 {
                    return Err(format!("Invalid NODE_COORD line: {}", line));
                }
                let id = parts[0].parse::<usize>().unwrap();
                let x = parts[1].parse::<f64>().unwrap();
                let y = parts[2].parse::<f64>().unwrap();
                node_coords.insert(id, (x, y));
            }

            Section::Display => {
                let parts: Vec<_> = line.split_whitespace().collect();
                if parts.len() != 3 {
                    return Err(format!("Invalid DISPLAY_DATA line: {}", line));
                }
                let id = parts[0].parse::<usize>().unwrap();
                let x = parts[1].parse::<i32>().unwrap();
                let y = parts[2].parse::<i32>().unwrap();
                display_coords.insert(id, (x, y));
            }

            Section::Demand => {
                let parts: Vec<_> = line.split_whitespace().collect();
                if parts.len() != 2 {
                    return Err(format!("Invalid DEMAND line: {}", line));
                }
                let id = parts[0].parse::<usize>().unwrap();
                let demand = parts[1].parse::<i32>().unwrap();
                demands.insert(id, demand);
            }
        }
    }

    Ok(TspInstance {
        name: name.ok_or("Missing NAME")?,
        comment,
        dimension: dimension.ok_or("Missing DIMENSION")?,
        capacity,
        edge_weight_type,
        node_coords,
        display_coords,
        demands,
    })
}
