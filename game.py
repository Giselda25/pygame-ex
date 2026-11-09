import random
import pygame

pygame.init()

# Окно игры
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Практика Pygame: Появление зомбэ")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
ground_y = HEIGHT - 100

# Загрузка кадров ходьбы игрока (1-10)
walk_frames = []
for i in range(1, 11):
  try:
    img = pygame.image.load(f"walk_{i}.png").convert_alpha()
    walk_frames.append(pygame.transform.scale(img, (80, 80)))
  except:
    pass

if not walk_frames:
  surf = pygame.Surface((80, 80))
  surf.fill((255, 0, 0))
  walk_frames = [surf]

# Загрузка кадров анимации зогмэ (1-11)
zombie_frames = []
for i in range(1, 12):
  try:
    img = pygame.image.load(f"zombie_{i}.png").convert_alpha()
    zombie_frames.append(pygame.transform.scale(img, (80, 80)))
  except:
    pass

# Загрузка спрайта стрельбы
try:
  shoot_img = pygame.image.load("shoot.png").convert_alpha()
  shoot_img = pygame.transform.scale(shoot_img, (80, 80))
except:
  shoot_img = walk_frames[0]

# Игрок
player_x = WIDTH // 2 - 40
player_y = ground_y - 80
player_speed = 4
facing_right = True
is_shooting = False

anim_index = 0
anim_timer = 0

# Списки объектов
bullets = []
zombies = []
spawn_timer = 0

running = True
while running:
  screen.fill(WHITE)

  # Рисуем землю
  pygame.draw.rect(screen, GREEN, (0, ground_y, WIDTH, 100))

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_SPACE:
        is_shooting = True
        bx = player_x + 70 if facing_right else player_x + 10
        bullets.append({
            'x': bx,
            'y': player_y + 26,
            'speed': 10 if facing_right else -10,
        })

    if event.type == pygame.KEYUP:
      if event.key == pygame.K_SPACE:
        is_shooting = False

  # Управление игроком
  keys = pygame.key.get_pressed()
  is_moving = False

  if not is_shooting:
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
      player_x -= player_speed
      facing_right = False
      is_moving = True
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
      player_x += player_speed
      facing_right = True
      is_moving = True

  # Границы экрана для игрока
  player_x = max(0, min(WIDTH - 80, player_x))

  # Спавн зомби слева или справа
  spawn_timer += 1
  if spawn_timer >= 100:
    spawn_timer = 0
    if random.choice([True, False]):
      # Спавн слева
      zombies.append({
          'x': -80,
          'speed': 1.5,
          'facing_right': True,
          'anim_index': 0,
          'anim_timer': 0,
      })
    else:
      # Спавн справа
      zombies.append({
          'x': WIDTH,
          'speed': -1.5,
          'facing_right': False,
          'anim_index': 0,
          'anim_timer': 0,
      })

  # Обновление и отрисовка пуль
  for bullet in bullets[:]:
    bullet['x'] += bullet['speed']
    if bullet['x'] < 0 or bullet['x'] > WIDTH:
      bullets.remove(bullet)
    else:
      pygame.draw.circle(
          screen, (255, 200, 0), (int(bullet['x']), int(bullet['y'])), 4
      )

  # Обновление и отрисовка зомби
  for zombie in zombies[:]:
    zombie['x'] += zombie['speed']
    zombie_rect = pygame.Rect(zombie['x'], ground_y - 80, 80, 80)

    # Анимация зомби
    zombie['anim_timer'] += 1
    if zombie['anim_timer'] >= 6:  # Скорость смены кадров зомбэ
      zombie['anim_timer'] = 0
      zombie['anim_index'] = (zombie['anim_index'] + 1) % len(zombie_frames)

    # Проверка попадания пули в зомби
    hit = False
    for bullet in bullets[:]:
      if zombie_rect.collidepoint(bullet['x'], bullet['y']):
        bullets.remove(bullet)
        hit = True
        break

    if hit:
      zombies.remove(zombie)
      continue

    # Выбираем текущий кадр анимации зомби
    z_image = zombie_frames[zombie['anim_index']]

    # Направления зомби
    if not zombie['facing_right']:
      z_image = pygame.transform.flip(z_image, True, False)

    # Рисуем зомби
    screen.blit(z_image, (zombie['x'], ground_y - 80))

  # Выбор спрайта игрока
  if is_shooting:
    current_image = shoot_img
  elif is_moving:
    anim_timer += 1
    if anim_timer >= 6:
      anim_timer = 0
      anim_index = (anim_index + 1) % len(walk_frames)
    current_image = walk_frames[anim_index]
  else:
    current_image = walk_frames[0]
    anim_index = 0
    anim_timer = 0

  # Поворот спрайта игрока
  if not facing_right:
    current_image = pygame.transform.flip(current_image, True, False)

  # Рисуем игрока
  screen.blit(current_image, (player_x, player_y))

  pygame.display.flip()
  clock.tick(60)

pygame.quit()