import random
from animals import Rabbit, Fox, Wolf, Pack
from neural_network import crossover

class EvolutionManager:
    def __init__(self, world):
        self.world = world
        self.generation = 1
        self.rabbit_population_target = 40
        self.fox_population_target = 12
        self.wolf_population_target = 8

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

        wolf_count = len(self.world.wolves)

        return (rabbit_count < self.rabbit_population_target * 0.2 or
                fox_count < self.fox_population_target * 0.2 or
                wolf_count < self.wolf_population_target * 0.2 or
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

        # Evolve wolves with pack considerations
        self.world.wolves = self.evolve_wolf_population(
            self.world.wolves, self.wolf_population_target
        )

        self.generation += 1
        self.world.generation_timer = 0
        self.world.generation_count = self.generation

        # Add some fresh food after evolution
        self.world.spawn_food(20)

    def evolve_wolf_population(self, wolves, target_population):
        if len(wolves) == 0:
            return self.create_random_population(target_population, Wolf)

        # Group wolves by pack for evolution
        pack_groups = {}
        lone_wolves = []

        for wolf in wolves:
            if wolf.pack:
                if wolf.pack.pack_id not in pack_groups:
                    pack_groups[wolf.pack.pack_id] = []
                pack_groups[wolf.pack.pack_id].append(wolf)
            else:
                lone_wolves.append(wolf)

        # Sort all wolves by fitness
        all_wolves = sorted(wolves, key=lambda x: x.fitness, reverse=True)

        # Statistics
        avg_fitness = sum(w.fitness for w in all_wolves) / len(all_wolves)
        max_fitness = all_wolves[0].fitness if all_wolves else 0
        avg_pack_coordination = sum(w.pack.pack_coordination for w in all_wolves if w.pack) / len([w for w in all_wolves if w.pack]) if any(w.pack for w in all_wolves) else 0

        print(f"Generation {self.generation} - Wolves:")
        print(f"  Population: {len(all_wolves)}")
        print(f"  Packs: {len(pack_groups)}")
        print(f"  Lone Wolves: {len(lone_wolves)}")
        print(f"  Avg Fitness: {avg_fitness:.2f}")
        print(f"  Max Fitness: {max_fitness:.2f}")
        print(f"  Avg Pack Coordination: {avg_pack_coordination:.2f}")

        # Select elite wolves for breeding
        elite_size = max(2, len(all_wolves) // 4)
        elite = all_wolves[:elite_size]

        # Create new wolf generation
        new_wolves = []

        # Keep some elite survivors (15% of target)
        elite_survivors = min(len(elite), target_population // 7)
        male_survivors = 0
        female_survivors = 0

        for survivor in elite:
            if len(new_wolves) >= elite_survivors:
                break
            if ((survivor.gender == 'male' and male_survivors < elite_survivors // 2) or
                (survivor.gender == 'female' and female_survivors < elite_survivors // 2) or
                len(new_wolves) == elite_survivors - 1):

                new_wolf = Wolf(
                    random.uniform(50, self.world.width - 50),
                    random.uniform(50, self.world.height - 50),
                    self.world.width,
                    self.world.height,
                    survivor.gender
                )
                new_wolf.brain = survivor.brain.copy()
                # Inherit pack traits
                new_wolf.pack_loyalty = survivor.pack_loyalty
                new_wolf.hunting_coordination = survivor.hunting_coordination
                new_wolf.pack_dominance = survivor.pack_dominance

                new_wolves.append(new_wolf)

                if survivor.gender == 'male':
                    male_survivors += 1
                else:
                    female_survivors += 1

        # Fill the rest through breeding
        males_created = sum(1 for w in new_wolves if w.gender == 'male')
        females_created = sum(1 for w in new_wolves if w.gender == 'female')

        while len(new_wolves) < target_population:
            # Determine child gender to maintain balance
            if males_created < target_population // 2:
                child_gender = 'male'
                males_created += 1
            elif females_created < target_population // 2:
                child_gender = 'female'
                females_created += 1
            else:
                child_gender = random.choice(['male', 'female'])

            if len(elite) >= 2 and random.random() < 0.8:  # 80% crossover
                # Prefer breeding within successful packs
                male_parents = [w for w in elite if w.gender == 'male']
                female_parents = [w for w in elite if w.gender == 'female']

                if male_parents and female_parents:
                    parent1 = random.choices(male_parents, weights=[w.fitness + 1 for w in male_parents])[0]
                    parent2 = random.choices(female_parents, weights=[w.fitness + 1 for w in female_parents])[0]
                else:
                    parent1, parent2 = random.choices(elite, k=2, weights=[w.fitness + 1 for w in elite])

                child_brain = crossover(parent1.brain, parent2.brain)

                # Inherit pack traits from both parents
                child_pack_loyalty = (parent1.pack_loyalty + parent2.pack_loyalty) / 2 + random.uniform(-0.1, 0.1)
                child_hunting_coordination = (parent1.hunting_coordination + parent2.hunting_coordination) / 2 + random.uniform(-0.1, 0.1)
                child_pack_dominance = (parent1.pack_dominance + parent2.pack_dominance) / 2 + random.uniform(-0.2, 0.2)
            else:  # 20% mutation
                parent = random.choices(elite, k=1, weights=[w.fitness + 1 for w in elite])[0]
                child_brain = parent.brain.copy()

                child_pack_loyalty = parent.pack_loyalty + random.uniform(-0.1, 0.1)
                child_hunting_coordination = parent.hunting_coordination + random.uniform(-0.1, 0.1)
                child_pack_dominance = parent.pack_dominance + random.uniform(-0.2, 0.2)

            # Create new wolf
            child = Wolf(
                random.uniform(50, self.world.width - 50),
                random.uniform(50, self.world.height - 50),
                self.world.width,
                self.world.height,
                child_gender
            )
            child.brain = child_brain
            child.brain.mutate(mutation_rate=0.1, mutation_strength=0.15)

            # Clamp inherited traits
            child.pack_loyalty = max(0.1, min(1.0, child_pack_loyalty))
            child.hunting_coordination = max(0.1, min(1.0, child_hunting_coordination))
            child.pack_dominance = max(0.1, min(1.0, child_pack_dominance))

            new_wolves.append(child)

        # Clear old packs and create new ones
        self.world.packs.clear()
        self.world.next_pack_id = 1

        # Recreate packs with new wolves
        if new_wolves:
            self.create_new_packs(new_wolves)

        return new_wolves

    def create_new_packs(self, wolves):
        # Create 2-3 packs based on population
        pack_count = min(3, max(1, len(wolves) // 3))

        for pack_num in range(pack_count):
            pack = Pack(self.world.next_pack_id)
            self.world.packs.append(pack)
            self.world.next_pack_id += 1

        # Assign wolves to packs based on compatibility
        for wolf in wolves:
            # Find the best pack for this wolf
            best_pack = None
            best_compatibility = -1

            for pack in self.world.packs:
                if pack.get_pack_size() >= 4:  # Don't overfill packs
                    continue

                # Calculate compatibility based on pack traits
                if pack.members:
                    avg_loyalty = sum(w.pack_loyalty for w in pack.members) / len(pack.members)
                    avg_coordination = sum(w.hunting_coordination for w in pack.members) / len(pack.members)

                    compatibility = (1 - abs(wolf.pack_loyalty - avg_loyalty)) * (1 - abs(wolf.hunting_coordination - avg_coordination))
                else:
                    compatibility = wolf.pack_loyalty * wolf.hunting_coordination

                if compatibility > best_compatibility:
                    best_compatibility = compatibility
                    best_pack = pack

            if best_pack:
                best_pack.add_member(wolf)