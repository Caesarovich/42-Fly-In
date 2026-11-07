*This project has been created as part of the 42 curriculum.*

# Fly-in

Drones are interesting.

## Description

The goal of this project is to parse maps as graphs and create a pathfinding algorithm to orchestrate the movement of a swarm of drones.
The application is a visualizer of the pathfinding algorithm.

## Instructions


For a simple way to run the application, follow these steps:
1. Clone the repository
2. Install the dependencies with `make install`
3. Ensure there is a `maps` folder in the root of the project
4. Run the application with `make run`

You can also run the app directly and pass the path to the maps folder as an argument:
```bash
uv run python3 -m src.app.main --maps-folder path/to/maps
```

## Resources

- [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra's_algorithm)
- [pygame.org](https://www.pygame.org/docs/)

AI Usage: AI was used for documentation, research and code completions.

## Algorithm explanations

I have three algorithms that build on top of each other:

- Dijkstra's algorithm: the classic pathfinding algorithm that finds the shortest path between two nodes in a graph. It does not care for the swarm and collisions. So drone move one by one.

- Alpha: a modified version of Dijkstra's algorithm that takes into account the swarm and collisions. Nodes on the graph keep track of the drones that occupy and will occupy them in the future. The cost calculation takes into account the waiting times as well as the distance. This means drone can parallelize their movement and wait for each other if needed.

- Beta: This algorithm builds on top of Alpha. It also account for inactive turn where the drones would be stuck waiting in line, and prioritizes the paths that imply less inactive turns. This means that some drones might be slower to reach the destination but they wont block the others behind them.

## Visualizer usage

The vizualizer will try to load the maps from the `maps` folder in the root of the project.
It will then display a grid of maps with a preview. In the main menu you can select the desired map and algorithm.

Simulation controls:
| Key | Action |
| --- | --- |
| ESC | Return to the main menu |
| Space | Start/pause the simulation |
| R | Reset the simulation |
| C | Center the view on the map |
| +/- | Increase/decrease the simulation speed |
| M | Toggle Map view |
| G | Toggle Graph view |
| Mouse wheel | Zoom in/out |
| Mouse drag | Pan the view |
