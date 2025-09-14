import random
import math
from animals import Rabbit, Fox, Wolf, Food, Pack

class World:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.rabbits = []
        self.foxes = []
        self.wolves = []
        self.packs = []
        self.food = []
        self.tick = 0
        self.generation_timer = 0
        self.generation_count = 1
        self.next_pack_id = 1

        # Initialize populations
        self.spawn_initial_population()
        self.spawn_food(30)
        self.create_initial_packs()

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

        # Spawn initial wolves (equal male/female)
        for i in range(8):
            x = random.uniform(50, self.width - 50)
            y = random.uniform(50, self.height - 50)
            gender = 'male' if i % 2 == 0 else 'female'
            wolf = Wolf(x, y, self.width, self.height, gender)
            self.wolves.append(wolf)

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

        # Update all wolves
        new_births = []
        for wolf in self.wolves[:]:
            birth = wolf.update(self)
            if birth:
                new_births.append(birth)
            if not wolf.is_alive():
                # Remove from pack if dead
                if wolf.pack:
                    wolf.pack.remove_member(wolf)
                self.wolves.remove(wolf)
        self.wolves.extend(new_births)

        # Update packs
        self.update_packs()

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

        # Handle wolf mating
        self.handle_species_mating(self.wolves)

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
        wolf_males = sum(1 for w in self.wolves if w.gender == 'male')
        wolf_females = sum(1 for w in self.wolves if w.gender == 'female')

        pregnant_rabbits = sum(1 for r in self.rabbits if r.is_pregnant)
        pregnant_foxes = sum(1 for f in self.foxes if f.is_pregnant)
        pregnant_wolves = sum(1 for w in self.wolves if w.is_pregnant)

        return {
            'tick': self.tick,
            'generation': self.generation_count,
            'rabbits': len(self.rabbits),
            'foxes': len(self.foxes),
            'wolves': len(self.wolves),
            'packs': len(self.packs),
            'food': len(self.food),
            'rabbit_males': rabbit_males,
            'rabbit_females': rabbit_females,
            'fox_males': fox_males,
            'fox_females': fox_females,
            'wolf_males': wolf_males,
            'wolf_females': wolf_females,
            'pregnant_rabbits': pregnant_rabbits,
            'pregnant_foxes': pregnant_foxes,
            'pregnant_wolves': pregnant_wolves,
            'rabbit_avg_energy': sum(r.energy for r in self.rabbits) / len(self.rabbits) if self.rabbits else 0,
            'fox_avg_energy': sum(f.energy for f in self.foxes) / len(self.foxes) if self.foxes else 0,
            'wolf_avg_energy': sum(w.energy for w in self.wolves) / len(self.wolves) if self.wolves else 0,
            'rabbit_avg_age': sum(r.age for r in self.rabbits) / len(self.rabbits) if self.rabbits else 0,
            'fox_avg_age': sum(f.age for f in self.foxes) / len(self.foxes) if self.foxes else 0,
            'wolf_avg_age': sum(w.age for w in self.wolves) / len(self.wolves) if self.wolves else 0,
        }

    def create_initial_packs(self):
        # Create 2-3 initial packs
        if not self.wolves:
            return

        wolves_per_pack = len(self.wolves) // 3 if len(self.wolves) >= 6 else len(self.wolves)
        pack_count = min(3, len(self.wolves) // 2) if len(self.wolves) >= 4 else 1

        for pack_num in range(pack_count):
            pack = Pack(self.next_pack_id)
            self.packs.append(pack)
            self.next_pack_id += 1

            # Assign wolves to pack
            start_idx = pack_num * wolves_per_pack
            end_idx = min(start_idx + wolves_per_pack + 1, len(self.wolves))

            for i in range(start_idx, end_idx):
                if i < len(self.wolves):
                    pack.add_member(self.wolves[i])

    def update_packs(self):
        # Remove empty packs
        self.packs = [pack for pack in self.packs if pack.get_pack_size() > 0]

        # Update existing packs
        for pack in self.packs:
            pack.update_pack_center()
            pack.update_hierarchy()

            # Pack may split if too large
            if pack.get_pack_size() > 8:
                self.split_pack(pack)

        # Lone wolves may try to join or form new packs
        self.manage_lone_wolves()

    def split_pack(self, pack):
        if pack.get_pack_size() <= 4:
            return

        # Split the pack in half
        members = [w for w in pack.members if w.is_alive()]
        half = len(members) // 2

        # Create new pack
        new_pack = Pack(self.next_pack_id)
        self.packs.append(new_pack)
        self.next_pack_id += 1

        # Move some wolves to new pack
        for i in range(half):
            wolf = members[i]
            pack.remove_member(wolf)
            new_pack.add_member(wolf)

    def manage_lone_wolves(self):
        lone_wolves = [w for w in self.wolves if w.pack is None and w.is_alive()]

        for wolf in lone_wolves:
            # Try to join nearby pack
            nearby_packs = []
            for pack in self.packs:
                if pack.get_pack_size() < 6:  # Not too large
                    pack_dist = math.sqrt((wolf.x - pack.pack_center_x)**2 +
                                        (wolf.y - pack.pack_center_y)**2)
                    if pack_dist < 100:  # Close enough
                        nearby_packs.append((pack, pack_dist))

            if nearby_packs and wolf.pack_loyalty > 0.6:
                # Join the closest suitable pack
                nearest_pack = min(nearby_packs, key=lambda x: x[1])[0]
                nearest_pack.add_member(wolf)
            elif len(lone_wolves) >= 2 and random.random() < 0.1:  # 10% chance to form new pack
                # Form new pack with other lone wolves
                new_pack = Pack(self.next_pack_id)
                self.packs.append(new_pack)
                self.next_pack_id += 1

                # Add up to 3 lone wolves to new pack
                for i, lone_wolf in enumerate(lone_wolves[:3]):
                    if lone_wolf.pack is None:
                        new_pack.add_member(lone_wolf)