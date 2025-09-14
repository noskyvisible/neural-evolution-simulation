#!/usr/bin/env python3

import sys
import time
from world import World
from evolution import EvolutionManager
from visualization import Visualizer

def main():
    print("Starting Neural Network Evolution Simulation...")
    print("Foxes (red circles) hunt Rabbits (brown circles)")
    print("Both species evolve their neural networks over time")
    print("Controls: SPACE to pause/resume, ESC to exit")
    print()

    # Create world and components
    world = World(width=800, height=600)
    evolution_manager = EvolutionManager(world)
    visualizer = Visualizer(width=800, height=600)

    print(f"Initial population: {len(world.rabbits)} rabbits, {len(world.foxes)} foxes")
    print("Starting simulation...")

    # Main simulation loop
    simulation_speed = 1  # Ticks per frame (slower updates)
    frame_rate = 30  # Lower frame rate for more detailed observation

    try:
        while visualizer.running:
            # Handle input events
            if not visualizer.handle_events():
                break

            # Update simulation if not paused
            if not visualizer.paused:
                for _ in range(simulation_speed):
                    world.update()

                    # Check for evolution
                    if evolution_manager.should_evolve():
                        print(f"\nTriggering evolution at tick {world.tick}")
                        evolution_manager.evolve()

                    # Prevent empty populations
                    if len(world.rabbits) == 0:
                        print("Rabbits extinct! Respawning...")
                        from animals import Rabbit
                        world.rabbits = evolution_manager.create_random_population(20, Rabbit)

                    if len(world.foxes) == 0:
                        print("Foxes extinct! Respawning...")
                        from animals import Fox
                        world.foxes = evolution_manager.create_random_population(8, Fox)

                    if len(world.wolves) == 0:
                        print("Wolves extinct! Respawning...")
                        from animals import Wolf
                        world.wolves = evolution_manager.create_random_population(6, Wolf)
                        world.create_initial_packs()

            # Update display
            visualizer.update_display(world, evolution_manager, frame_rate)

            # Print periodic stats
            if world.tick % 1000 == 0 and world.tick > 0:
                stats = world.get_stats()
                print(f"Tick {stats['tick']:,} - Gen {stats['generation']} - "
                      f"Rabbits: {stats['rabbits']}, Foxes: {stats['foxes']}, Food: {stats['food']}")

    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")

    finally:
        # Final statistics
        print(f"\n=== SIMULATION COMPLETE ===")
        stats = world.get_stats()
        print(f"Final Statistics:")
        print(f"  Total Ticks: {stats['tick']:,}")
        print(f"  Generations: {stats['generation']}")
        print(f"  Final Populations - Rabbits: {stats['rabbits']}, Foxes: {stats['foxes']}")
        print(f"  Average Ages - Rabbits: {stats['rabbit_avg_age']:.1f}, Foxes: {stats['fox_avg_age']:.1f}")

        if world.rabbits:
            best_rabbit = max(world.rabbits, key=lambda r: r.fitness)
            print(f"  Best Rabbit - Fitness: {best_rabbit.fitness:.2f}, Children: {best_rabbit.children}")

        if world.foxes:
            best_fox = max(world.foxes, key=lambda f: f.fitness)
            print(f"  Best Fox - Fitness: {best_fox.fitness:.2f}, Kills: {best_fox.kills}, Children: {best_fox.children}")

        visualizer.cleanup()

if __name__ == "__main__":
    main()