import numpy as np
import math
import random
from neural_network import NeuralNetwork

class Animal:
    def __init__(self, x, y, world_width, world_height, gender=None):
        self.x = x
        self.y = y
        self.world_width = world_width
        self.world_height = world_height
        self.energy = 100
        self.age = 0
        self.max_age = 2000  # Longer lifespan
        self.speed = 1.0  # Slower base speed
        self.direction = random.uniform(0, 2 * math.pi)
        self.fitness = 0
        self.children = 0
        self.gender = gender if gender else random.choice(['male', 'female'])
        self.mating_cooldown = 0
        self.pregnancy_time = 0
        self.is_pregnant = False
        self.mate_seeking = False
        self.last_mate = None

    def update(self, world):
        self.age += 1
        self.energy -= 0.2  # Slower energy loss

        # Update breeding-related timers
        if self.mating_cooldown > 0:
            self.mating_cooldown -= 1
        if self.pregnancy_time > 0:
            self.pregnancy_time -= 1
            if self.pregnancy_time == 0 and self.is_pregnant:
                return self.give_birth()

        # Determine if seeking mate
        self.mate_seeking = (self.can_reproduce() and
                           self.mating_cooldown == 0 and
                           not self.is_pregnant)

        # Get sensory input
        inputs = self.get_inputs(world)

        # Process through neural network
        outputs = self.brain.forward(inputs)

        # Interpret outputs as actions
        self.process_outputs(outputs)

        # Update position
        self.move()

        # Check boundaries
        self.check_boundaries()

        # Update fitness
        self.fitness += 0.1 if self.energy > 0 else -1

    def get_inputs(self, world):
        # Basic sensory inputs (to be overridden by subclasses)
        return [
            self.x / self.world_width,  # Normalized position
            self.y / self.world_height,
            self.energy / 100,  # Normalized energy
            math.cos(self.direction),  # Direction vector
            math.sin(self.direction)
        ]

    def process_outputs(self, outputs):
        # Interpret neural network outputs as actions
        # outputs[0]: turn left/right (-1 to 1)
        # outputs[1]: speed (0 to 1)

        self.direction += (outputs[0] - 0.5) * 0.2  # Gentler turning
        self.speed = outputs[1] * 2.0  # Slower max speed

    def move(self):
        dx = math.cos(self.direction) * self.speed
        dy = math.sin(self.direction) * self.speed

        self.x += dx
        self.y += dy

    def check_boundaries(self):
        if self.x < 0:
            self.x = 0
            self.direction = math.pi - self.direction
        elif self.x >= self.world_width:
            self.x = self.world_width - 1
            self.direction = math.pi - self.direction

        if self.y < 0:
            self.y = 0
            self.direction = -self.direction
        elif self.y >= self.world_height:
            self.y = self.world_height - 1
            self.direction = -self.direction

    def is_alive(self):
        return self.energy > 0 and self.age < self.max_age

    def can_reproduce(self):
        return (self.energy > 120 and self.age > 200 and
               self.mating_cooldown == 0 and not self.is_pregnant)

    def find_mate(self, potential_mates):
        if not self.mate_seeking:
            return None

        best_mate = None
        best_distance = float('inf')

        for mate in potential_mates:
            if (mate != self and mate.gender != self.gender and
                mate.can_reproduce() and mate != self.last_mate):
                distance = self.distance_to(mate)
                if distance < 30 and distance < best_distance:  # Mating range
                    best_mate = mate
                    best_distance = distance

        return best_mate

    def mate_with(self, partner):
        if self.gender == 'female':
            self.is_pregnant = True
            self.pregnancy_time = 300  # 300 ticks gestation
            self.energy -= 30

        self.mating_cooldown = 500  # Cooldown period
        partner.mating_cooldown = 500
        self.last_mate = partner
        partner.last_mate = self

        return True

    def give_birth(self):
        self.is_pregnant = False
        self.children += 1
        self.energy -= 40
        return None  # To be overridden by subclasses

    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


class Rabbit(Animal):
    def __init__(self, x, y, world_width, world_height, gender=None):
        super().__init__(x, y, world_width, world_height, gender)
        self.brain = NeuralNetwork(input_size=10, hidden_sizes=[12, 10], output_size=2)
        self.vision_range = 60
        self.reproduction_energy = 50

    def get_inputs(self, world):
        inputs = super().get_inputs(world)

        # Find nearest food
        nearest_food_dist = float('inf')
        nearest_food_angle = 0
        for food in world.food:
            dist = self.distance_to(food)
            if dist < nearest_food_dist:
                nearest_food_dist = dist
                angle = math.atan2(food.y - self.y, food.x - self.x)
                nearest_food_angle = angle - self.direction

        # Find nearest predator (fox)
        nearest_predator_dist = float('inf')
        nearest_predator_angle = 0
        for fox in world.foxes:
            dist = self.distance_to(fox)
            if dist < nearest_predator_dist and dist < self.vision_range:
                nearest_predator_dist = dist
                angle = math.atan2(fox.y - self.y, fox.x - self.x)
                nearest_predator_angle = angle - self.direction

        # Find nearest potential mate
        nearest_mate_dist = float('inf')
        nearest_mate_angle = 0
        if self.mate_seeking:
            mate = self.find_mate(world.rabbits)
            if mate:
                nearest_mate_dist = self.distance_to(mate)
                angle = math.atan2(mate.y - self.y, mate.x - self.x)
                nearest_mate_angle = angle - self.direction

        inputs.extend([
            min(nearest_food_dist / self.vision_range, 1.0),
            math.cos(nearest_food_angle),
            min(nearest_predator_dist / self.vision_range, 1.0) if nearest_predator_dist < self.vision_range else 0,
            math.cos(nearest_predator_angle) if nearest_predator_dist < self.vision_range else 0,
            min(nearest_mate_dist / self.vision_range, 1.0) if self.mate_seeking and nearest_mate_dist < self.vision_range else 0,
        ])

        return inputs

    def give_birth(self):
        if not self.is_pregnant:
            return None

        # Create child with genetic combination
        child = Rabbit(self.x + random.uniform(-15, 15),
                      self.y + random.uniform(-15, 15),
                      self.world_width, self.world_height)

        # Child inherits from mother's brain with mutations
        child.brain = self.brain.copy()
        child.brain.mutate(mutation_rate=0.1, mutation_strength=0.15)

        self.is_pregnant = False
        return child


class Fox(Animal):
    def __init__(self, x, y, world_width, world_height, gender=None):
        super().__init__(x, y, world_width, world_height, gender)
        self.brain = NeuralNetwork(input_size=9, hidden_sizes=[12, 10], output_size=2)
        self.vision_range = 80
        self.hunt_range = 18
        self.reproduction_energy = 80
        self.kills = 0

    def get_inputs(self, world):
        inputs = super().get_inputs(world)

        # Find nearest rabbit
        nearest_prey_dist = float('inf')
        nearest_prey_angle = 0
        for rabbit in world.rabbits:
            dist = self.distance_to(rabbit)
            if dist < nearest_prey_dist and dist < self.vision_range:
                nearest_prey_dist = dist
                angle = math.atan2(rabbit.y - self.y, rabbit.x - self.x)
                nearest_prey_angle = angle - self.direction

        # Find nearest potential mate
        nearest_mate_dist = float('inf')
        nearest_mate_angle = 0
        if self.mate_seeking:
            mate = self.find_mate(world.foxes)
            if mate:
                nearest_mate_dist = self.distance_to(mate)
                angle = math.atan2(mate.y - self.y, mate.x - self.x)
                nearest_mate_angle = angle - self.direction

        inputs.extend([
            min(nearest_prey_dist / self.vision_range, 1.0) if nearest_prey_dist < self.vision_range else 0,
            math.cos(nearest_prey_angle) if nearest_prey_dist < self.vision_range else 0,
            min(nearest_mate_dist / self.vision_range, 1.0) if self.mate_seeking and nearest_mate_dist < self.vision_range else 0,
            math.cos(nearest_mate_angle) if self.mate_seeking and nearest_mate_dist < self.vision_range else 0,
        ])

        return inputs

    def hunt(self, world):
        for rabbit in world.rabbits[:]:
            if self.distance_to(rabbit) < self.hunt_range:
                world.rabbits.remove(rabbit)
                self.energy += 50
                self.kills += 1
                self.fitness += 10
                break

    def give_birth(self):
        if not self.is_pregnant:
            return None

        # Create child with genetic combination
        child = Fox(self.x + random.uniform(-20, 20),
                   self.y + random.uniform(-20, 20),
                   self.world_width, self.world_height)

        # Child inherits from mother's brain with mutations
        child.brain = self.brain.copy()
        child.brain.mutate(mutation_rate=0.1, mutation_strength=0.15)

        self.is_pregnant = False
        return child

    def update(self, world):
        super().update(world)
        self.hunt(world)


class Pack:
    def __init__(self, pack_id):
        self.pack_id = pack_id
        self.members = []
        self.alpha_male = None
        self.alpha_female = None
        self.pack_center_x = 0
        self.pack_center_y = 0
        self.hunting_target = None
        self.pack_coordination = 0.5  # How well the pack works together

    def update_pack_center(self):
        if not self.members:
            return
        self.pack_center_x = sum(wolf.x for wolf in self.members) / len(self.members)
        self.pack_center_y = sum(wolf.y for wolf in self.members) / len(self.members)

    def add_member(self, wolf):
        self.members.append(wolf)
        wolf.pack = self
        wolf.pack_id = self.pack_id
        self.update_hierarchy()

    def remove_member(self, wolf):
        if wolf in self.members:
            self.members.remove(wolf)
            wolf.pack = None
            wolf.pack_id = None
            self.update_hierarchy()

    def update_hierarchy(self):
        if not self.members:
            self.alpha_male = None
            self.alpha_female = None
            return

        males = [w for w in self.members if w.gender == 'male' and w.is_alive()]
        females = [w for w in self.members if w.gender == 'female' and w.is_alive()]

        self.alpha_male = max(males, key=lambda w: w.pack_dominance) if males else None
        self.alpha_female = max(females, key=lambda w: w.pack_dominance) if females else None

    def get_pack_size(self):
        return len([w for w in self.members if w.is_alive()])

    def is_hunting(self):
        return self.hunting_target is not None


class Wolf(Animal):
    def __init__(self, x, y, world_width, world_height, gender=None, pack_id=None):
        super().__init__(x, y, world_width, world_height, gender)
        self.brain = NeuralNetwork(input_size=14, hidden_sizes=[16, 14], output_size=3)
        self.vision_range = 100
        self.hunt_range = 20
        self.reproduction_energy = 100
        self.kills = 0
        self.pack = None
        self.pack_id = pack_id
        self.pack_dominance = random.uniform(0.3, 1.0)
        self.howl_cooldown = 0
        self.pack_loyalty = random.uniform(0.5, 1.0)
        self.hunting_coordination = random.uniform(0.3, 0.8)
        self.max_age = 2500
        self.energy = 120

    def get_inputs(self, world):
        inputs = super().get_inputs(world)

        # Find nearest rabbit
        nearest_prey_dist = float('inf')
        nearest_prey_angle = 0
        prey_count_nearby = 0
        for rabbit in world.rabbits:
            dist = self.distance_to(rabbit)
            if dist < self.vision_range:
                prey_count_nearby += 1
                if dist < nearest_prey_dist:
                    nearest_prey_dist = dist
                    angle = math.atan2(rabbit.y - self.y, rabbit.x - self.x)
                    nearest_prey_angle = angle - self.direction

        # Find nearest fox (competition)
        nearest_competitor_dist = float('inf')
        for fox in world.foxes:
            dist = self.distance_to(fox)
            if dist < nearest_competitor_dist and dist < self.vision_range:
                nearest_competitor_dist = dist

        # Pack information
        pack_center_dist = float('inf')
        pack_center_angle = 0
        pack_size = 0
        is_alpha = 0

        if self.pack:
            pack_size = self.pack.get_pack_size()
            is_alpha = 1 if (self == self.pack.alpha_male or self == self.pack.alpha_female) else 0
            self.pack.update_pack_center()
            pack_center_dist = math.sqrt((self.x - self.pack.pack_center_x)**2 +
                                       (self.y - self.pack.pack_center_y)**2)
            if pack_center_dist > 0:
                angle = math.atan2(self.pack.pack_center_y - self.y, self.pack.pack_center_x - self.x)
                pack_center_angle = angle - self.direction

        # Find nearest potential mate
        nearest_mate_dist = float('inf')
        nearest_mate_angle = 0
        if self.mate_seeking:
            mate = self.find_mate(world.wolves)
            if mate:
                nearest_mate_dist = self.distance_to(mate)
                angle = math.atan2(mate.y - self.y, mate.x - self.x)
                nearest_mate_angle = angle - self.direction

        inputs.extend([
            min(nearest_prey_dist / self.vision_range, 1.0) if nearest_prey_dist < self.vision_range else 0,
            math.cos(nearest_prey_angle) if nearest_prey_dist < self.vision_range else 0,
            min(prey_count_nearby / 10.0, 1.0),  # Prey density
            min(nearest_competitor_dist / self.vision_range, 1.0) if nearest_competitor_dist < self.vision_range else 0,
            min(pack_center_dist / 100.0, 1.0),  # Distance to pack center
            math.cos(pack_center_angle),
            min(pack_size / 8.0, 1.0),  # Pack size normalized
            is_alpha,
            min(nearest_mate_dist / self.vision_range, 1.0) if self.mate_seeking and nearest_mate_dist < self.vision_range else 0,
        ])

        return inputs

    def process_outputs(self, outputs):
        # outputs[0]: turn left/right (-1 to 1)
        # outputs[1]: speed (0 to 1)
        # outputs[2]: howl/communicate (0 to 1)

        self.direction += (outputs[0] - 0.5) * 0.25  # Pack coordination affects turning
        self.speed = outputs[1] * 2.5  # Wolves are faster than foxes

        # Howling/communication
        if outputs[2] > 0.7 and self.howl_cooldown == 0:
            self.howl()
            self.howl_cooldown = 100

        if self.howl_cooldown > 0:
            self.howl_cooldown -= 1

    def howl(self):
        # Howling helps coordinate pack and attract distant members
        if self.pack:
            for wolf in self.pack.members:
                if wolf != self and self.distance_to(wolf) < 150:
                    # Boost pack coordination
                    wolf.fitness += 1
                    # Help lost pack members find the group
                    if self.distance_to(wolf) > 80:
                        angle_to_pack = math.atan2(self.y - wolf.y, self.x - wolf.x)
                        wolf.direction = angle_to_pack + random.uniform(-0.3, 0.3)

    def hunt(self, world):
        # Pack hunting is more effective
        hunt_bonus = 1.0
        if self.pack and self.pack.get_pack_size() > 1:
            hunt_bonus = 1.0 + (self.pack.get_pack_size() - 1) * 0.3
            hunt_bonus *= self.pack.pack_coordination

        effective_hunt_range = self.hunt_range * hunt_bonus

        for rabbit in world.rabbits[:]:
            if self.distance_to(rabbit) < effective_hunt_range:
                # Pack hunting success rate
                success_chance = 0.4  # Base chance
                if self.pack:
                    # More wolves nearby = higher success rate
                    nearby_pack_members = sum(1 for w in self.pack.members
                                            if w != self and w.distance_to(rabbit) < 50)
                    success_chance += nearby_pack_members * 0.2
                    success_chance = min(success_chance, 0.9)  # Cap at 90%

                if random.random() < success_chance:
                    world.rabbits.remove(rabbit)
                    # Shared kill - all nearby pack members get energy
                    energy_gain = 60
                    if self.pack:
                        nearby_wolves = [w for w in self.pack.members
                                       if w.distance_to(rabbit) < 60]
                        if len(nearby_wolves) > 1:
                            energy_per_wolf = energy_gain / len(nearby_wolves)
                            for wolf in nearby_wolves:
                                wolf.energy += energy_per_wolf
                                wolf.kills += 1 / len(nearby_wolves)  # Shared kill credit
                                wolf.fitness += 15
                        else:
                            self.energy += energy_gain
                            self.kills += 1
                            self.fitness += 12
                    else:
                        self.energy += energy_gain * 0.7  # Lone wolves less efficient
                        self.kills += 1
                        self.fitness += 8
                    break

    def give_birth(self):
        if not self.is_pregnant:
            return None

        child = Wolf(self.x + random.uniform(-20, 20),
                    self.y + random.uniform(-20, 20),
                    self.world_width, self.world_height,
                    pack_id=self.pack_id if self.pack else None)

        child.brain = self.brain.copy()
        child.brain.mutate(mutation_rate=0.1, mutation_strength=0.15)

        # Inherit some pack traits
        if self.pack:
            child.pack_loyalty = self.pack_loyalty + random.uniform(-0.1, 0.1)
            child.hunting_coordination = self.hunting_coordination + random.uniform(-0.1, 0.1)
            child.pack_dominance = self.pack_dominance + random.uniform(-0.2, 0.2)
            # Clamp values
            child.pack_loyalty = max(0.1, min(1.0, child.pack_loyalty))
            child.hunting_coordination = max(0.1, min(1.0, child.hunting_coordination))
            child.pack_dominance = max(0.1, min(1.0, child.pack_dominance))

        self.is_pregnant = False
        return child

    def update(self, world):
        birth = super().update(world)
        self.hunt(world)

        # Pack behavior updates
        if self.pack:
            # Stay closer to pack if loyalty is high
            pack_distance = math.sqrt((self.x - self.pack.pack_center_x)**2 +
                                    (self.y - self.pack.pack_center_y)**2)
            if pack_distance > 200 and self.pack_loyalty > 0.7:
                # Move towards pack center
                angle_to_pack = math.atan2(self.pack.pack_center_y - self.y,
                                         self.pack.pack_center_x - self.x)
                self.direction = angle_to_pack + random.uniform(-0.5, 0.5)

        return birth


class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 30