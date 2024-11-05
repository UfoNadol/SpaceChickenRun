import pygame
import sys
import os
import random

# Inicjalizacja Pygame
pygame.init()

# Ustawienia okna gry
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Gra Rzutu Bocznego")

# Inicjalizacja postaci
player_image_paths = [f"ruch{i}.png" for i in range(1, 9)]
player_images = [pygame.transform.scale(pygame.image.load(os.path.join("images", img)), (200, 200)) for img in player_image_paths]
player_rect = player_images[0].get_rect()
player_rect.topleft = (100, height // 2)
player_health = 100

# Inicjalizacja przeciwników
enemy_images = [pygame.transform.scale(pygame.image.load(os.path.join("images", "enemy1.png")), (100, 100)),
                pygame.transform.scale(pygame.image.load(os.path.join("images", "enemy2.png")), (100, 100))]
enemies = []

# Inicjalizacja tła
background = pygame.image.load("background.png")
background_rect = background.get_rect()
bg_x = 0

# Inicjalizacja potionu
potion_image = pygame.transform.scale(pygame.image.load(os.path.join("images", "potion.png")), (50, 50))
potion_rect = potion_image.get_rect()
potion_rect.topleft = (width + random.randint(200, 500), random.randint(50, height - 50))

# Inicjalizacja strzału
shoot_image = pygame.transform.scale(pygame.image.load(os.path.join("images", "shoot.png")), (15, 15))
shoot_speed = 200
shoots = []

# Inicjalizacja punktów i życia
points = 0
font = pygame.font.Font(None, 36)

# Ustawienia ruchu postaci
player_speed = 5
animation_speed = 30  # Zmniejszenie prędkości animacji postaci o 40%
animation_count = 1
clock = pygame.time.Clock()

# Flaga sterowania postacią
is_moving = False

# Inicjalizacja dźwięku
pygame.mixer.music.load(os.path.join("sounds", "soundtrack.wav"))
pygame.mixer.music.play(-1)

# Funkcja resetująca stan gry
def reset_game():
    global player_health, points, enemies, shoots, bg_x, player_speed, max_shoots
    player_health = 100
    points = 0
    enemies = []
    shoots = []
    bg_x = 0
    player_speed = 5
    max_shoots = 0
    player_rect.topleft = (100, height // 2)

# Funkcja spawnująca przeciwników
def spawn_enemy():
    enemy_type = random.choice(enemy_images)
    enemy_rect = enemy_type.get_rect()
    enemy_rect.topleft = (width + random.randint(200, 500), random.randint(50, height - 50))
    return [enemy_type, enemy_rect]

max_shoots: float = 0
frames = 30
running = True
game_over = False

# Główna pętla gry
while running:
    if game_over:
        # Wyświetlenie ekranu końcowego
        screen.fill((0, 0, 0))
        end_text = font.render("THE END - Retry?", True, (255, 0, 0))
        screen.blit(end_text, (width // 2 - end_text.get_width() // 2, height // 2))

        # Oczekiwanie na klawisz Enter
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    reset_game()
                    game_over = False

        pygame.display.flip()
        clock.tick(frames)
        continue

    # Obsługa zdarzeń w grze
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                is_moving = True
            elif event.key == pygame.K_SPACE:
                if len(shoots) <= max_shoots:
                    shoots.append((player_rect.midright[0], player_rect.midright[1] - shoot_image.get_height() // 2))
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                is_moving = False
                animation_count = 0

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_rect.left > 0:
        if player_rect.left > 100:
            player_rect.x -= player_speed
        else:
            bg_x += player_speed
    if keys[pygame.K_RIGHT] and player_rect.right < width:
        if player_rect.right < width/2:
            player_rect.right += player_speed
        else:
            bg_x -= player_speed
    if keys[pygame.K_UP] and player_rect.top > 0:
        player_rect.y -= player_speed
    if keys[pygame.K_DOWN] and player_rect.bottom < height:
        player_rect.y += player_speed

    # Spawnowanie przeciwników
    if random.randint(1, 100) < 5:
        enemies.append(spawn_enemy())

    # Poruszanie przeciwników wraz z tłem
    for enemy in enemies:
        enemy[1].x -= player_speed

    # Animacja ruchu postaci
    if is_moving:
        player_image_index = (animation_count // (animation_speed // len(player_images))) % len(player_images)
        player_image = player_images[player_image_index]
        if animation_count >= animation_speed * len(player_images):
            animation_count = 0
        animation_count += 1
    else:
        player_image_index = len(player_images) - 1 - (animation_count // (animation_speed // len(player_images))) % len(player_images)
        player_image = player_images[player_image_index]

    # Rysowanie na ekranie
    screen.blit(background, (bg_x, 0))
    screen.blit(background, (bg_x + background_rect.width, 0))
    screen.blit(player_image, player_rect.topleft)

    # Rysowanie przeciwników
    for enemy in enemies:
        screen.blit(enemy[0], enemy[1].topleft)

    # Rysowanie potionu
    screen.blit(potion_image, potion_rect.topleft)

    # Rysowanie strzałów
    for shoot_pos in shoots:
        screen.blit(shoot_image, shoot_pos)

    # Kollision z przeciwnikami
    for enemy in enemies:
        if not player_rect.colliderect(enemy[1]):
            continue
        x, y, _, _ = enemy[1]
        a = x-player_rect.x-50
        b = y-player_rect.y-50
        c = (a**2 + b**2)**(1/2)
        if c>100:
            continue
        player_speed *= .75 if player_speed > 5 else 1
        player_health -= 10
        enemies.remove(enemy)
        points += 2

    # Kollision z potionem
    if player_rect.colliderect(potion_rect):
        player_health = min(100, player_health + 20)
        potion_rect.topleft = (width + random.randint(200, 500), random.randint(50, height - 50))

    # Kollision ze strzałami
    for shoot_pos in shoots:
        for enemy in enemies:
            if enemy[1].colliderect(shoot_pos[0], shoot_pos[1], shoot_image.get_width(), shoot_image.get_height()):
                enemies.remove(enemy)
                max_shoots += .2
                points += 2
                player_speed += 1
                shoots.remove(shoot_pos)

    # Usuwanie strzałów, które przekroczyły ekran
    shoots = [(x+10, y) for x, y in shoots]
    shoots = [shoot for shoot in shoots if shoot[0] < width]

    # Rysowanie punktów i życia
    points_text = font.render(f'Points: {points}', True, (255, 255, 255))
    screen.blit(points_text, (350, 350))

    health_text = font.render(f'Health: {player_health}', True, (255, 255, 255))
    screen.blit(health_text, (300, 300))

    # Sprawdzenie końca gry
    if player_health <= 0:
        game_over = True

    # Aktualizacja ekranu
    pygame.display.flip()

    # Ustawienie liczby klatek na sekundę
    clock.tick(frames)

# Zamknięcie gry
pygame.quit()
sys.exit()
