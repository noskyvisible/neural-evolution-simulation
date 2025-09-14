import pygame
import math
import sys

class Visualizer:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width + 200, height))  # Extra space for stats
        pygame.display.set_caption("Neural Network Evolution - Foxes and Rabbits")

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GREEN = (34, 139, 34)
        self.LIGHT_GREEN = (144, 238, 144)
        self.BROWN = (139, 69, 19)
        self.LIGHT_BROWN = (160, 82, 45)
        self.RED = (220, 20, 60)
        self.DARK_RED = (139, 0, 0)
        self.BLUE = (30, 144, 255)
        self.PURPLE = (148, 0, 211)
        self.PINK = (255, 182, 193)
        self.ORANGE = (255, 140, 0)
        self.GRAY = (128, 128, 128)
        self.DARK_GRAY = (64, 64, 64)
        self.LIGHT_GRAY = (211, 211, 211)

        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

        return self.running

    def draw_world(self, world):
        # Clear screen
        self.screen.fill(self.WHITE)

        # Draw simulation area border
        pygame.draw.rect(self.screen, self.BLACK, (0, 0, self.width, self.height), 2)

        # Draw food with improved graphics
        for food in world.food:
            x, y = int(food.x), int(food.y)
            # Food as a small grass cluster
            pygame.draw.circle(self.screen, self.GREEN, (x, y), 5)
            pygame.draw.circle(self.screen, self.LIGHT_GREEN, (x, y), 3)
            # Add small stems
            for i in range(3):
                stem_x = x + (i - 1) * 2
                pygame.draw.line(self.screen, self.GREEN, (stem_x, y + 2), (stem_x, y - 2), 1)

        # Draw rabbits with gender and state indicators
        for rabbit in world.rabbits:
            x, y = int(rabbit.x), int(rabbit.y)

            # Choose colors based on gender
            body_color = self.BROWN if rabbit.gender == 'male' else self.LIGHT_BROWN
            accent_color = self.BLUE if rabbit.gender == 'male' else self.PINK

            # Draw rabbit body (oval shape)
            pygame.draw.ellipse(self.screen, body_color, (x-7, y-5, 14, 10))
            pygame.draw.circle(self.screen, body_color, (x, y), 6)

            # Draw ears
            ear1_x = x - 3 + math.cos(rabbit.direction + 0.5) * 4
            ear1_y = y - 3 + math.sin(rabbit.direction + 0.5) * 4
            ear2_x = x + 3 + math.cos(rabbit.direction - 0.5) * 4
            ear2_y = y + 3 + math.sin(rabbit.direction - 0.5) * 4
            pygame.draw.circle(self.screen, body_color, (int(ear1_x), int(ear1_y)), 3)
            pygame.draw.circle(self.screen, body_color, (int(ear2_x), int(ear2_y)), 3)

            # Gender indicator (small dot)
            pygame.draw.circle(self.screen, accent_color, (x-8, y-8), 2)

            # Special states
            if rabbit.is_pregnant:
                pygame.draw.circle(self.screen, self.PINK, (x, y), 9, 2)
            elif rabbit.mate_seeking:
                pygame.draw.circle(self.screen, self.PURPLE, (x, y), 10, 1)

            # Draw direction indicator
            end_x = x + math.cos(rabbit.direction) * 12
            end_y = y + math.sin(rabbit.direction) * 12
            pygame.draw.line(self.screen, self.DARK_GRAY, (x, y), (int(end_x), int(end_y)), 2)

            # Draw energy bar
            energy_ratio = rabbit.energy / 200  # Updated max energy
            bar_width = 14
            bar_height = 3
            bar_x = x - bar_width // 2
            bar_y = y - 15

            pygame.draw.rect(self.screen, self.BLACK, (bar_x-1, bar_y-1, bar_width+2, bar_height+2))
            pygame.draw.rect(self.screen, self.GRAY, (bar_x, bar_y, bar_width, bar_height))
            energy_color = self.GREEN if energy_ratio > 0.5 else (self.ORANGE if energy_ratio > 0.25 else self.RED)
            pygame.draw.rect(self.screen, energy_color, (bar_x, bar_y, int(bar_width * energy_ratio), bar_height))

        # Draw foxes with gender and state indicators
        for fox in world.foxes:
            x, y = int(fox.x), int(fox.y)

            # Choose colors based on gender
            body_color = self.RED if fox.gender == 'male' else self.DARK_RED
            accent_color = self.BLUE if fox.gender == 'male' else self.PINK

            # Draw fox body (more fox-like shape)
            pygame.draw.ellipse(self.screen, body_color, (x-9, y-6, 18, 12))
            pygame.draw.circle(self.screen, body_color, (x, y), 8)

            # Draw pointed ears
            ear_tip_x = x + math.cos(rabbit.direction) * 6
            ear_tip_y = y + math.sin(rabbit.direction) * 6
            pygame.draw.polygon(self.screen, body_color, [
                (x-4, y-8), (x-1, y-12), (x+1, y-8)
            ])
            pygame.draw.polygon(self.screen, body_color, [
                (x+1, y-8), (x+4, y-12), (x+7, y-8)
            ])

            # Draw tail
            tail_x = x - math.cos(fox.direction) * 10
            tail_y = y - math.sin(fox.direction) * 10
            pygame.draw.circle(self.screen, body_color, (int(tail_x), int(tail_y)), 4)

            # Gender indicator
            pygame.draw.circle(self.screen, accent_color, (x-10, y-10), 2)

            # Special states
            if fox.is_pregnant:
                pygame.draw.circle(self.screen, self.PINK, (x, y), 12, 2)
            elif fox.mate_seeking:
                pygame.draw.circle(self.screen, self.PURPLE, (x, y), 13, 1)

            # Draw direction indicator
            end_x = x + math.cos(fox.direction) * 15
            end_y = y + math.sin(fox.direction) * 15
            pygame.draw.line(self.screen, self.BLACK, (x, y), (int(end_x), int(end_y)), 3)

            # Draw energy bar
            energy_ratio = fox.energy / 200  # Updated max energy
            bar_width = 18
            bar_height = 4
            bar_x = x - bar_width // 2
            bar_y = y - 18

            pygame.draw.rect(self.screen, self.BLACK, (bar_x-1, bar_y-1, bar_width+2, bar_height+2))
            pygame.draw.rect(self.screen, self.GRAY, (bar_x, bar_y, bar_width, bar_height))
            energy_color = self.GREEN if energy_ratio > 0.5 else (self.ORANGE if energy_ratio > 0.25 else self.RED)
            pygame.draw.rect(self.screen, energy_color, (bar_x, bar_y, int(bar_width * energy_ratio), bar_height))

    def draw_stats(self, world, evolution_manager):
        # Stats panel background
        stats_x = self.width + 10
        pygame.draw.rect(self.screen, self.LIGHT_GREEN, (self.width, 0, 200, self.height))
        pygame.draw.line(self.screen, self.BLACK, (self.width, 0), (self.width, self.height), 2)

        stats = world.get_stats()
        y_offset = 20

        # Title
        title = self.font.render("SIMULATION STATS", True, self.BLACK)
        self.screen.blit(title, (stats_x, y_offset))
        y_offset += 40

        # Enhanced stats with breeding info
        stat_texts = [
            f"Generation: {stats['generation']}",
            f"Tick: {stats['tick']:,}",
            "",
            f"Rabbits: {stats['rabbits']}",
            f"  Males: {stats['rabbit_males']}",
            f"  Females: {stats['rabbit_females']}",
            f"  Pregnant: {stats['pregnant_rabbits']}",
            "",
            f"Foxes: {stats['foxes']}",
            f"  Males: {stats['fox_males']}",
            f"  Females: {stats['fox_females']}",
            f"  Pregnant: {stats['pregnant_foxes']}",
            "",
            f"Food: {stats['food']}",
            "",
            f"Avg Energy:",
            f"  Rabbits: {stats['rabbit_avg_energy']:.1f}",
            f"  Foxes: {stats['fox_avg_energy']:.1f}",
            "",
            f"Avg Age:",
            f"  Rabbits: {stats['rabbit_avg_age']:.0f}",
            f"  Foxes: {stats['fox_avg_age']:.0f}",
            "",
            "Legend:",
            "Brown/Light = Rabbits M/F",
            "Red/Dark Red = Foxes M/F",
            "Purple ring = Seeking mate",
            "Pink ring = Pregnant",
            "",
            "Controls:",
            "SPACE - Pause/Resume",
            "ESC - Exit",
        ]

        for text in stat_texts:
            if text:
                rendered_text = self.small_font.render(text, True, self.BLACK)
                self.screen.blit(rendered_text, (stats_x, y_offset))
            y_offset += 20

        # Pause indicator
        if self.paused:
            pause_text = self.font.render("PAUSED", True, self.RED)
            self.screen.blit(pause_text, (stats_x, self.height - 40))

        # Generation timer progress
        progress = (world.generation_timer / 5000) * 180  # 180 pixels wide
        pygame.draw.rect(self.screen, self.GRAY, (stats_x, self.height - 80, 180, 10))
        pygame.draw.rect(self.screen, self.BLUE, (stats_x, self.height - 80, int(progress), 10))
        gen_text = self.small_font.render("Next Evolution", True, self.BLACK)
        self.screen.blit(gen_text, (stats_x, self.height - 100))

    def update_display(self, world, evolution_manager, frame_rate=30):
        if not self.paused:
            self.draw_world(world)

        self.draw_stats(world, evolution_manager)
        pygame.display.flip()
        self.clock.tick(frame_rate)

    def cleanup(self):
        pygame.quit()
        sys.exit()