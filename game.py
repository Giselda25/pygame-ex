import pygame
pygame.init()

# Окно игры
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Практика Pygame")
WHITE = (255, 255, 255)

# Загрузка 10 кадров анимации хождения(скомпилировано из гиф)
try:
  walk_frames = [
      pygame.transform.scale(
          pygame.image.load(f"walk_{i}.png").convert_alpha(), (80, 80)
      )
      for i in range(1, 11)
  ]
  static_image = walk_frames[0]
except Exception as e:
  print(
      "Ошибка загрузки изображения!"
  )
  # Заглушка на случай ошибки, чтобы программа не вылетела
  surf = pygame.Surface((80, 80))
  surf.fill((255, 0, 0))
  walk_frames = [surf]
  static_image = surf

# Начальные координаты персонажа и скорость
player_x = WIDTH // 2 - 40
player_y = HEIGHT // 2 - 40
player_speed = 4

# Переменные для анимации
anim_index = 0
anim_timer = 0
ANIM_SPEED = 6  # Скорость смены кадров, чем меньше тем быстрее анимация

# Игровой таймер и флаг работы цикла
clock = pygame.time.Clock()
running = True

# Главный игровой цикл
while running:
  # Обработка закрытия окна
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

  # Управление клавишами, стрелки и WASD
  keys = pygame.key.get_pressed()
  is_moving = False

  if keys[pygame.K_LEFT] or keys[pygame.K_a]:
    player_x -= player_speed
    is_moving = True
  if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
    player_x += player_speed
    is_moving = True
  if keys[pygame.K_UP] or keys[pygame.K_w]:
    player_y -= player_speed
    is_moving = True
  if keys[pygame.K_DOWN] or keys[pygame.K_s]:
    player_y += player_speed
    is_moving = True

  # Ограничение, чтобы персонаж не выбегал за границы окна
  if player_x < 0:
    player_x = 0
  elif player_x > WIDTH - 80:
    player_x = WIDTH - 80

  if player_y < 0:
    player_y = 0
  elif player_y > HEIGHT - 80:
    player_y > HEIGHT - 80

  # Логика анимации кадров
  if is_moving:
    anim_timer += 1
    if anim_timer >= ANIM_SPEED:
      anim_timer = 0
      anim_index = (anim_index + 1) % len(walk_frames)
    current_image = walk_frames[anim_index]
  else:
    # Если персонаж стоит на месте, то сбрасывается на первый кадр(стоячее положение)
    current_image = static_image
    anim_index = 0
    anim_timer = 0

  # Отрисовка кадров
  screen.fill(WHITE)  # Белый экран
  screen.blit(current_image, (player_x, player_y))  # Сам персонаж

  # Обновление экрана
  pygame.display.flip()

  # Ограничение до 60 кадров в секунду для плавной работы
  clock.tick(60)

pygame.quit()