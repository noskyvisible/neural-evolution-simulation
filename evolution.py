import random
from animals import Rabbit, Fox
from neural_network import crossover

class EvolutionManager:
    def __init__(self, world):
        self.world = world
        self.generation = 1
        self.rabbit_population_target = 40
        self.fox_population_target = 12

    def evolve_population(self, animals, target_population, animal_class):
        if len(animals) == 0:
            return self.create_random_population(target_population, animal_class)

        # Sort by fitness
        animals.sort(key=lambda x: x.fitness, reverse=True)

        # Statistics
        avg_fitness = sum(a.fitness for a in animals) / len(animals)
        max_fitness = animals[0].fitness if animals else 0
        males = sum(1 for a in animals if a.gender == 'male')
        females = sum(1 for a in animals if a.gender == 'female')
        total_children = sum(a.children for a in animals)

        print(f"Generation {self.generation} - {animal_class.__name__}s:")
        print(f"  Population: {len(animals)} (M:{males}, F:{females})")
        print(f"  Total Children Born: {total_children}")
        print(f"  Avg Fitness: {avg_fitness:.2f}")
        print(f"  Max Fitness: {max_fitness:.2f}")
        if animal_class.__name__ == 'Fox' and animals:
            total_kills = sum(getattr(a, 'kills', 0) for a in animals)
            print(f"  Total Kills: {total_kills}")

        # Select the best individuals for reproduction
        elite_size = max(2, len(animals) // 4)  # Top 25%
        elite = animals[:elite_size]

        # Create new generation
        new_animals = []

        # Keep some elite (15% of target population) with gender balance
        elite_survivors = min(len(elite), target_population // 7)
        male_survivors = 0
        female_survivors = 0

        for survivor in elite:
            if len(new_animals) >= elite_survivors:
                break
            # Try to maintain gender balance
            if ((survivor.gender == 'male' and male_survivors < elite_survivors // 2) or
                (survivor.gender == 'female' and female_survivors < elite_survivors // 2) or
                len(new_animals) == elite_survivors - 1):

                new_animal = animal_class(
                    random.uniform(50, self.world.width - 50),
                    random.uniform(50, self.world.height - 50),
                    self.world.width,
                    self.world.height,
                    survivor.gender
                )
                new_animal.brain = survivor.brain.copy()
                new_animals.append(new_animal)

                if survivor.gender == 'male':
                    male_survivors += 1
                else:
                    female_survivors += 1

        # Fill the rest through breeding pairs with gender balance
        males_created = sum(1 for a in new_animals if a.gender == 'male')
        females_created = sum(1 for a in new_animals if a.gender == 'female')

        while len(new_animals) < target_population:
            # Determine child gender to maintain balance
            if males_created < target_population // 2:
                child_gender = 'male'
                males_created += 1
            elif females_created < target_population // 2:
                child_gender = 'female'
                females_created += 1
            else:
                child_gender = random.choice(['male', 'female'])

            if len(elite) >= 2 and random.random() < 0.8:  # 80% crossover (breeding)
                # Select breeding pair (preferably different genders)
                male_parents = [a for a in elite if a.gender == 'male']
                female_parents = [a for a in elite if a.gender == 'female']

                if male_parents and female_parents:
                    parent1 = random.choices(male_parents, weights=[a.fitness + 1 for a in male_parents])[0]
                    parent2 = random.choices(female_parents, weights=[a.fitness + 1 for a in female_parents])[0]
                else:
                    parent1, parent2 = random.choices(elite, k=2, weights=[a.fitness + 1 for a in elite])

                child_brain = crossover(parent1.brain, parent2.brain)
            else:  # 20% mutation of single parent
                parent = random.choices(elite, k=1, weights=[a.fitness + 1 for a in elite])[0]
                child_brain = parent.brain.copy()

            # Create new animal
            child = animal_class(
                random.uniform(50, self.world.width - 50),
                random.uniform(50, self.world.height - 50),
                self.world.width,
                self.world.height,
                child_gender
            )
            child.brain = child_brain
            child.brain.mutate(mutation_rate=0.12, mutation_strength=0.18)

            new_animals.append(child)

        return new_animals

    def create_random_population(self, size, animal_class):
        animals = []
        for i in range(size):
            gender = 'male' if i % 2 == 0 else 'female'  # Even gender distribution
            animal = animal_class(
                random.uniform(50, self.world.width - 50),
                random.uniform(50, self.world.height - 50),
                self.world.width,
                self.world.height,
                gender
            )
            animals.append(animal)
        return animals

    def should_evolve(self):
        # Evolve when population gets too low or after certain time
        rabbit_count = len(self.world.rabbits)
        fox_count = len(self.world.foxes)

        return (rabbit_count < self.rabbit_population_target * 0.2 or
                fox_count < self.fox_population_target * 0.2 or
                self.world.generation_timer > 8000)  # Every 8000 ticks (longer generations)

    def evolve(self):
        print(f"\n=== EVOLUTION - Generation {self.generation} ===")

        # Evolve rabbits
        self.world.rabbits = self.evolve_population(
            self.world.rabbits, self.rabbit_population_target, Rabbit
        )

        # Evolve foxes
        self.world.foxes = self.evolve_population(
            self.world.foxes, self.fox_population_target, Fox
        )

        self.generation += 1
        self.world.generation_timer = 0
        self.world.generation_count = self.generation

        # Add some fresh food after evolution
        self.world.spawn_food(20)