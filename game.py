
import pygame
import random
import math
import time

WIDTH, HEIGHT = 800, 560
FPS = 60
BG = (30, 35, 25)
SPEED = 4


class Zombie:
    TYPES = {
        "normal": {
            "size": 30, "speed": 1.5, "hp": 3,
            "color": (60, 140, 60)
        },
        "fast": {
            "size": 20, "speed": 3.0, "hp": 1,
            "color": (230, 190, 40)
        },
        "tank": {
            "size": 44, "speed": 0.8, "hp": 6,
            "color": (150, 65, 65)
        },
    }

    def __init__(self, x, y, zombie_type="normal"):
        stats = self.TYPES[zombie_type]
        self.zombie_type = zombie_type
        self.size = stats["size"]
        self.speed = stats["speed"]
        self.max_hp = stats["hp"]
        self.hp = self.max_hp
        self.color = stats["color"]
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.frame = 0

    def update(self, player_pos):
        px, py = player_pos
        cx, cy = self.rect.center
        dx, dy = px - cx, py - cy
        dist = math.hypot(dx, dy)

        if dist:
            self.rect.x += round(dx / dist * self.speed)
            self.rect.y += round(dy / dist * self.speed)

        self.frame += 1

    def hit(self):
        self.hp -= 1
        return self.hp <= 0

    def draw(self, screen):
        wobble_y = int(math.sin(self.frame * 0.2) * 3)
        draw_rect = self.rect.move(0, wobble_y)

        pygame.draw.rect(
            screen, self.color, draw_rect, border_radius=5
        )

        eye_y = draw_rect.y + self.size // 3
        eye_radius = max(2, self.size // 9)

        for ex in (
            draw_rect.x + self.size // 3,
            draw_rect.x + 2 * self.size // 3,
        ):
            pygame.draw.circle(
                screen, (200, 40, 40), (ex, eye_y), eye_radius
            )

        if self.zombie_type == "tank":
            bar_width = self.size
            pygame.draw.rect(
                screen, (60, 20, 20),
                (draw_rect.x, draw_rect.y - 8, bar_width, 5)
            )
            pygame.draw.rect(
                screen, (220, 60, 60),
                (
                    draw_rect.x,
                    draw_rect.y - 8,
                    int(bar_width * max(0, self.hp) / self.max_hp),
                    5,
                ),
            )


def spawn_zombie(width, height, player_rect, zombie_type=None, margin=120):
    if zombie_type is None:
        zombie_type = random.choices(
            ["normal", "fast", "tank"],
            weights=[6, 3, 1],
            k=1,
        )[0]

    size = Zombie.TYPES[zombie_type]["size"]

    while True:
        x = random.randint(0, width - size)
        y = random.randint(45, height - size)
        rect = pygame.Rect(x, y, size, size)

        if not rect.colliderect(player_rect.inflate(margin, margin)):
            return Zombie(x, y, zombie_type)


class Barrel:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 28, 34)
        self.explosion_radius = 100

    def draw(self, screen):
        pygame.draw.rect(
            screen, (170, 65, 30), self.rect, border_radius=5
        )
        pygame.draw.rect(
            screen, (240, 180, 55),
            (self.rect.x + 4, self.rect.y + 8, 20, 5)
        )
        pygame.draw.rect(
            screen, (240, 180, 55),
            (self.rect.x + 4, self.rect.y + 23, 20, 5)
        )


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.color = (60, 160, 220)
        self.bullets = []
        self.shoot_cooldown = 0

        # Task 1: Health and temporary invincibility
        self.hp = 3
        self.max_hp = 3
        self.invincible_until = 0
        self.invincibility_duration = 1.0

        # Task 2: Ammo and reloading
        self.ammo = 12
        self.max_ammo = 12
        self.reloading = False
        self.reload_start_time = 0
        self.reload_duration = 2.0

    def take_damage(self):
        now = time.time()

        if now < self.invincible_until:
            return False

        self.hp -= 1
        self.invincible_until = now + self.invincibility_duration
        return True

    def reload(self):
        if self.ammo < self.max_ammo and not self.reloading:
            self.reloading = True
            self.reload_start_time = time.time()

    def update_reload(self):
        if (
            self.reloading
            and time.time() - self.reload_start_time >= self.reload_duration
        ):
            self.ammo = self.max_ammo
            self.reloading = False

    def move(self, keys, width, height):
        dx = dy = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = SPEED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = SPEED

        self.rect.x = max(0, min(width - self.rect.width, self.rect.x + dx))
        self.rect.y = max(40, min(height - self.rect.height, self.rect.y + dy))

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def shoot(self, target_pos):
        if (
            self.shoot_cooldown > 0
            or self.reloading
            or self.ammo <= 0
        ):
            return

        cx, cy = self.rect.center
        tx, ty = target_pos
        dx, dy = tx - cx, ty - cy
        dist = math.hypot(dx, dy)

        if dist == 0:
            return

        vx, vy = dx / dist * 10, dy / dist * 10
        self.bullets.append([cx - 4, cy - 4, vx, vy])
        self.ammo -= 1
        self.shoot_cooldown = 15

    def update_bullets(self, width, height):
        live = []

        for bullet in self.bullets:
            bullet[0] += bullet[2]
            bullet[1] += bullet[3]

            if 0 <= bullet[0] <= width and 0 <= bullet[1] <= height:
                live.append(bullet)

        self.bullets = live

    def draw(self, screen):
        if (
            time.time() >= self.invincible_until
            or int(time.time() * 10) % 2 == 0
        ):
            pygame.draw.rect(
                screen, self.color, self.rect, border_radius=6
            )

        for bullet in self.bullets:
            pygame.draw.circle(
                screen,
                (255, 220, 60),
                (int(bullet[0]), int(bullet[1])),
                5,
            )


class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Zombie Escape")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 16)
        self.big_font = pygame.font.SysFont("monospace", 44, bold=True)
        self.reset()

    def reset(self):
        self.player = Player(WIDTH // 2, HEIGHT // 2)

        # Task 4: Guarantee all zombie types appear at startup.
        self.zombies = [
            spawn_zombie(WIDTH, HEIGHT, self.player.rect, "normal"),
            spawn_zombie(WIDTH, HEIGHT, self.player.rect, "fast"),
            spawn_zombie(WIDTH, HEIGHT, self.player.rect, "tank"),
            spawn_zombie(WIDTH, HEIGHT, self.player.rect, "fast"),
        ]

        # Task 3: Four explosive barrels
        positions = [
            (100, 100),
            (670, 100),
            (100, 430),
            (670, 430),
        ]
        self.barrels = [Barrel(x, y) for x, y in positions]

        self.score = 0
        self.wave = 1
        self.kills = 0
        self.kills_to_next = 8
        self.game_over = False
        self.start_time = time.time()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                if self.game_over:
                    self.reset()
                else:
                    self.player.reload()

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and not self.game_over
            ):
                self.player.shoot(event.pos)

        return True

    def update(self):
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.player.move(keys, WIDTH, HEIGHT)
        self.player.update_reload()
        self.player.update_bullets(WIDTH, HEIGHT)

        self.score = int(time.time() - self.start_time)

        for zombie in self.zombies:
            zombie.update(self.player.rect.center)

            if zombie.rect.colliderect(self.player.rect):
                self.player.take_damage()

                if self.player.hp <= 0:
                    self.game_over = True
                    break

        dead = []

        # Task 3: Shooting a barrel triggers an explosion.
        for bullet in self.player.bullets[:]:
            bx, by = int(bullet[0]), int(bullet[1])
            bullet_rect = pygame.Rect(bx - 4, by - 4, 8, 8)

            hit_barrel = None
            for barrel in self.barrels:
                if barrel.rect.colliderect(bullet_rect):
                    hit_barrel = barrel
                    break

            if hit_barrel is not None:
                center = hit_barrel.rect.center
                radius = hit_barrel.explosion_radius

                self.barrels.remove(hit_barrel)
                self.player.bullets.remove(bullet)

                for zombie in self.zombies[:]:
                    distance = math.hypot(
                        zombie.rect.centerx - center[0],
                        zombie.rect.centery - center[1],
                    )
                    if distance <= radius:
                        dead.append(zombie)

                continue

            for zombie in self.zombies:
                if zombie.rect.collidepoint(bx, by):
                    if zombie.hit():
                        dead.append(zombie)

                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)

                    break

        for zombie in dead:
            if zombie in self.zombies:
                self.zombies.remove(zombie)
                self.kills += 1
                self.score += 10

        # Preserve wave progression.
        if self.kills >= self.kills_to_next:
            self.kills = 0
            self.wave += 1
            self.kills_to_next = 8 + self.wave * 2

            for _ in range(self.wave + 3):
                self.zombies.append(
                    spawn_zombie(WIDTH, HEIGHT, self.player.rect)
                )

    def draw(self):
        self.screen.fill(BG)

        for x in range(0, WIDTH, 60):
            pygame.draw.line(
                self.screen, (40, 45, 35), (x, 0), (x, HEIGHT), 1
            )

        for y in range(0, HEIGHT, 60):
            pygame.draw.line(
                self.screen, (40, 45, 35), (0, y), (WIDTH, y), 1
            )

        for barrel in self.barrels:
            barrel.draw(self.screen)

        for zombie in self.zombies:
            zombie.draw(self.screen)

        self.player.draw(self.screen)

        pygame.draw.rect(
            self.screen, (15, 20, 15), pygame.Rect(0, 0, WIDTH, 40)
        )

        reload_text = " RELOADING..." if self.player.reloading else ""
        hud = self.font.render(
            f"HP: {self.player.hp}/3  Ammo: {self.player.ammo}/12"
            f"{reload_text}  Wave: {self.wave}  Score: {self.score}"
            f"  Kills: {self.kills}/{self.kills_to_next}",
            True,
            (160, 220, 120),
        )
        self.screen.blit(hud, (8, 12))

        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))

            message = self.big_font.render(
                "DEVOURED!", True, (180, 40, 40)
            )
            subtitle = self.font.render(
                f"Wave {self.wave} | Score {self.score} | Press R",
                True,
                (200, 200, 200),
            )

            self.screen.blit(
                message,
                (
                    WIDTH // 2 - message.get_width() // 2,
                    HEIGHT // 2 - 40,
                ),
            )
            self.screen.blit(
                subtitle,
                (
                    WIDTH // 2 - subtitle.get_width() // 2,
                    HEIGHT // 2 + 20,
                ),
            )

        pygame.display.flip()

    def run(self):
        running = True

        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    engine = GameEngine()
    engine.run()
