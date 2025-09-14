import random
import math
from animals import Rabbit, Fox, Food

class World:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.rabbits = []
        self.foxes = []
        self.food = []
        self.tick = 0
        self.generation_timer = 0
        self.generation_count = 1

        # Initialize populations
        self.spawn_initial_population()
        self.spawn_food(30)

    def spawn_initial_population(self):
        # Spawn initial rabbits (equal male/female)
        for i in range(40):
            x = random.uniform(50, self.width - 50)
            y = random.uniform(50, self.height - 50)
            gender = 'male' if i % 2 == 0 else 'female'
            rabbit = Rabbit(x, y, self.width, self.height, gender)
            self.rabbits.append(rabbit)

        # Spawn initial foxes (equal male/female)
        for i in range(12):
            x = random.uniform(50, self.width - 50)
            y = random.uniform(50, self.height - 50)
            gender = 'male' if i % 2 == 0 else 'female'
            fox = Fox(x, y, self.width, self.height, gender)
            self.foxes.append(fox)

    def spawn_food(self, count):
        for _ in range(count):
            x = random.uniform(20, self.width - 20)
            y = random.uniform(20, self.height - 20)
            self.food.append(Food(x, y))

    def update(self):
        self.tick += 1
        self.generation_timer += 1

        # Update all rabbits
        new_births = []
        for rabbit in self.rabbits[:]:
            birth = rabbit.update(self)
            if birth:
                new_births.append(birth)
            if not rabbit.is_alive():
                self.rabbits.remove(rabbit)
        self.rabbits.extend(new_births)

        # Update all foxes
        new_births = []
        for fox in self.foxes[:]:
            birth = fox.update(self)
            if birth:
                new_births.append(birth)
            if not fox.is_alive():
                self.foxes.remove(fox)
        self.foxes.extend(new_births)

        # Handle rabbit feeding
        self.handle_feeding()

        # Handle mating
        self.handle_mating()

        # Spawn new food occasionally
        if self.tick % 100 == 0 and len(self.food) < 40:
            self.spawn_food(5)

        # Random food spawning (slower)
        if random.random() < 0.03:
            self.spawn_food(1)

    def handle_feeding(self):
        for rabbit in self.rabbits:
            for food in self.food[:]:
                if rabbit.distance_to(food) < 15:  # Feeding range
                    self.food.remove(food)
                    rabbit.energy += food.energy
                    rabbit.energy = min(rabbit.energy, 200)  # Cap energy
                    rabbit.fitness += 5
                    break

    def handle_mating(self):
        # Handle rabbit mating
        self.handle_species_mating(self.rabbits)

        # Handle fox mating
        self.handle_species_mating(self.foxes)

    def handle_species_mating(self, animals):
        # Find mating pairs
        mated_animals = set()

        for animal in animals:
            if (animal in mated_animals or not animal.mate_seeking):
                continue

            mate = animal.find_mate(animals)
            if mate and mate not in mated_animals:
                # Successful mating
                if animal.mate_with(mate):
                    mated_animals.add(animal)
                    mated_animals.add(mate)
                    animal.fitness += 20  # Reward successful mating
                    mate.fitness += 20

    def get_stats(self):
        rabbit_males = sum(1 for r in self.rabbits if r.gender == 'male')
        rabbit_females = sum(1 for r in self.rabbits if r.gender == 'female')
        fox_males = sum(1 for f in self.foxes if f.gender == 'male')
        fox_females = sum(1 for f in self.foxes if f.gender == 'female')

        pregnant_rabbits = sum(1 for r in self.rabbits if r.is_pregnant)
        pregnant_foxes = sum(1 for f in self.foxes if f.is_pregnant)

        return {
            'tick': self.tick,
            'generation': self.generation_count,
            'rabbits': len(self.rabbits),
            'foxes': len(self.foxes),
            'food': len(self.food),
            'rabbit_males': rabbit_males,
            'rabbit_females': rabbit_females,
            'fox_males': fox_males,
            'fox_females': fox_females,
            'pregnant_rabbits': pregnant_rabbits,
            'pregnant_foxes': pregnant_foxes,
            'rabbit_avg_energy': sum(r.energy for r in self.rabbits) / len(self.rabbits) if self.rabbits else 0,
            'fox_avg_energy': sum(f.energy for f in self.foxes) / len(self.foxes) if self.foxes else 0,
            'rabbit_avg_age': sum(r.age for r in self.rabbits) / len(self.rabbits) if self.rabbits else 0,
            'fox_avg_age': sum(f.age for f in self.foxes) / len(self.foxes) if self.foxes else 0,
        }