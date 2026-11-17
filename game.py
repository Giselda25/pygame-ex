import random
import pygame

pygame.init()
pygame.mixer.init()  # Инициализация звукового движка

# Окно игры
WIDTH, HEIGHT = 800, 600
WORLD_WIDTH = 1600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Практика Pygame: Выживание в доме")
clock = pygame.time.Clock()

# Шрифты
font = pygame.font.Font(None, 24)
font_large = pygame.font.Font(None, 32)
font_hud = pygame.font.Font(None, 28)
font_gameover = pygame.font.Font(None, 48)

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 220, 0)
RED = (220, 50, 50)
GREEN = (50, 200, 50)

# --- ЗАГРУЗКА ЗВУКОВЫХ ЭФФЕКТОВ (с защитой от ошибок) ---
try:
  shot_sound = pygame.mixer.Sound("shot.mp3")
except:
  shot_sound = None

try:
  hit_sound = pygame.mixer.Sound("hit.mp3")
except:
  hit_sound = None

try:
  reload_sound = pygame.mixer.Sound("reload.mp3")
except:
  reload_sound = None

# Фоновая музыка для радио
try:
  pygame.mixer.music.load("rickroll.mp3")
except:
  pass

# --- ПИКСЕЛЬНЫЙ ФОН КОМНАТЫ ---
bg_surface = pygame.Surface((WORLD_WIDTH, HEIGHT))
bg_surface.fill((45, 50, 60))

for wx in range(0, WORLD_WIDTH, 50):
  pygame.draw.line(bg_surface, (52, 58, 70), (wx, 0), (wx, HEIGHT - 100), 3)

ground_y = HEIGHT - 100
pygame.draw.rect(bg_surface, (70, 45, 30), (0, ground_y, WORLD_WIDTH, 100))
for fx in range(0, WORLD_WIDTH, 80):
  pygame.draw.line(bg_surface, (50, 30, 20), (fx, ground_y), (fx, HEIGHT), 2)
pygame.draw.rect(bg_surface, (35, 22, 15), (0, ground_y - 12, WORLD_WIDTH, 12))

# Дверь и окно на фоне
pygame.draw.rect(bg_surface, (35, 25, 18), (150, ground_y - 380, 100, 368))
pygame.draw.rect(bg_surface, (25, 18, 12), (158, ground_y - 372, 84, 352))
pygame.draw.circle(bg_surface, (210, 190, 60), (228, ground_y - 190), 5)

pygame.draw.rect(bg_surface, (20, 30, 45), (1250, 120, 150, 240))
pygame.draw.circle(bg_surface, (230, 230, 210), (1350, 160), 16)
pygame.draw.rect(bg_surface, (55, 45, 35), (1240, 110, 170, 260), 8)
pygame.draw.line(bg_surface, (55, 45, 35), (1325, 110), (1325, 370), 6)
pygame.draw.line(bg_surface, (55, 45, 35), (1240, 240), (1410, 240), 6)


# --- ЗАГРУЗКА СПРАЙТОВ ---
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

zombie_frames = []
for i in range(1, 12):
  try:
    img = pygame.image.load(f"zombie_{i}.png").convert_alpha()
    zombie_frames.append(pygame.transform.scale(img, (80, 80)))
  except:
    pass

try:
  shoot_img = pygame.image.load("shoot.png").convert_alpha()
  shoot_img = pygame.transform.scale(shoot_img, (80, 80))
except:
  shoot_img = walk_frames[0]


# --- ИГРОК И ХАРАКТЕРИСТИКИ ---
player_x = 300
player_y = ground_y - 80
player_speed = 4
player_health = 5
max_player_health = 5
ammo = 13
max_ammo = 13
last_damage_time = 0

facing_right = True
is_shooting = False
anim_index = 0
anim_timer = 0
game_over = False


# --- ОБЪЕКТЫ В КОМНАТЕ ---
objects = [
    {
        'name': 'Тумбочка',
        'x': 550,
        'y': ground_y - 75,
        'w': 75,
        'h': 75,
        'state': 'Закрыта',
    },
    {
        'name': 'Радио',
        'x': 1050,
        'y': ground_y - 45,
        'w': 60,
        'h': 45,
        'state': 'Выключено',
    },
]

bullets = []
zombies = []
headshot_texts = []
floating_texts = []
spawn_timer = 0
interaction_message = ''
message_timer = 0

running = True
while running:
  current_time = pygame.time.get_ticks()

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

    if event.type == pygame.KEYDOWN:
      # Рестарт по Enter при смерти
      if game_over:
        if event.key == pygame.K_RETURN:
          player_health = max_player_health
          ammo = max_ammo
          player_x = 300
          zombies.clear()
          bullets.clear()
          game_over = False
        continue

      if event.key == pygame.K_SPACE:
        if ammo > 0:
          ammo -= 1
          is_shooting = True
          # Воспроизведение звука выстрела (накладывается поверх других)
          if shot_sound:
            shot_sound.play()

          bx = player_x + 70 if facing_right else player_x + 10
          bullets.append({
              'x': bx,
              'y': player_y + 26,
              'speed': 10 if facing_right else -10,
          })

      # Перезарядка на R
      if event.key == pygame.K_r:
        ammo = max_ammo
        if reload_sound:
          reload_sound.play()
        interaction_message = 'Перезарядка!'
        message_timer = 60

      # Взаимодействие по E
      if event.key == pygame.K_e:
        player_center = player_x + 40
        for obj in objects:
          obj_center = obj['x'] + obj['w'] // 2
          if abs(player_center - obj_center) < 65:
            if obj['name'] == 'Тумбочка':
              player_health = max_player_health
              obj['state'] = 'Открыта (Бинты взяты)'
              interaction_message = 'Здоровье полностью восстановлено!'
              floating_texts.append({
                  'text': '+ЗДОРОВЬЕ',
                  'x': player_x + 10,
                  'y': player_y - 15,
                  'timer': 50,
              })
            elif obj['name'] == 'Радио':
              if obj['state'] == 'Выключено':
                obj['state'] = 'Играет Rickroll ♫'
                try:
                  pygame.mixer.music.play(-1)
                except:
                  pass
                interaction_message = 'Радио: Играет музыка!'
              else:
                obj['state'] = 'Выключено'
                try:
                  pygame.mixer.music.stop()
                except:
                  pass
                interaction_message = 'Радио: Выключено'
            message_timer = 120

    if event.type == pygame.KEYUP:
      if event.key == pygame.K_SPACE:
        is_shooting = False

  # --- ЭКРАН ИГРА ОКОНЧЕНА ---
  if game_over:
    screen.fill((15, 0, 0))
    over_text = font_gameover.render("ИГРА ОКОНЧЕНА", True, RED)
    sub_text = font.render("НАЖМИТЕ ENTER, ЧТОБЫ НАЧАТЬ СНАЧАЛА", True, WHITE)

    over_rect = over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 25))
    sub_rect = sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 25))

    screen.blit(over_text, over_rect)
    screen.blit(sub_text, sub_rect)

    pygame.display.flip()
    clock.tick(60)
    continue

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

  player_x = max(0, min(WORLD_WIDTH - 80, player_x))

  # Камера
  camera_x = player_x - WIDTH // 2 + 40
  camera_x = max(0, min(WORLD_WIDTH - WIDTH, camera_x))

  # --- СПАВН ЗОМБИ ---
  spawn_timer += 1
  if spawn_timer >= 110:
    spawn_timer = 0
    if random.choice([True, False]):
      zombies.append({
          'x': camera_x - 100,
          'speed': 1.4,
          'hp': 3,
          'max_hp': 3,
          'facing_right': True,
          'anim_index': 0,
          'anim_timer': 0,
      })
    else:
      zombies.append({
          'x': camera_x + WIDTH + 100,
          'speed': -1.4,
          'hp': 3,
          'max_hp': 3,
          'facing_right': False,
          'anim_index': 0,
          'anim_timer': 0,
      })

  # --- ОТРИСОВКА ФОНА ---
  screen.blit(bg_surface, (-camera_x, 0))

  # --- ОБЪЕКТЫ И ПОДСКАЗКИ ---
  player_center = player_x + 40
  near_object = None

  for obj in objects:
    obj_rect_screen = pygame.Rect(
        obj['x'] - camera_x, obj['y'], obj['w'], obj['h']
    )
    if obj['name'] == 'Тумбочка':
      pygame.draw.rect(screen, (90, 60, 40), obj_rect_screen)
      pygame.draw.rect(screen, (50, 30, 15), obj_rect_screen, 3)
      pygame.draw.circle(
          screen,
          (200, 180, 50),
          (obj_rect_screen.centerx, obj_rect_screen.centery),
          4,
      )
    else:
      pygame.draw.rect(screen, (80, 80, 90), obj_rect_screen, border_radius=4)
      pygame.draw.circle(
          screen,
          (30, 30, 30),
          (obj_rect_screen.x + 15, obj_rect_screen.centery),
          6,
      )
      pygame.draw.circle(
          screen,
          (30, 30, 30),
          (obj_rect_screen.x + 35, obj_rect_screen.centery),
          6,
      )

    if abs(player_center - (obj['x'] + obj['w'] // 2)) < 65:
      near_object = obj

  # --- ПУЛИ ---
  for bullet in bullets[:]:
    bullet['x'] += bullet['speed']
    if bullet['x'] < camera_x - 50 or bullet['x'] > camera_x + WIDTH + 50:
      bullets.remove(bullet)
    else:
      pygame.draw.circle(
          screen,
          (255, 200, 0),
          (int(bullet['x'] - camera_x), int(bullet['y'])),
          4,
      )

  # --- ЗОМБИ И КОЛЛИЗИИ ---
  player_rect = pygame.Rect(player_x, player_y, 80, 80)

  for zombie in zombies[:]:
    zombie['x'] += zombie['speed']
    zombie_rect = pygame.Rect(zombie['x'], ground_y - 80, 80, 80)

    # Урон игроку
    if player_rect.colliderect(zombie_rect):
      if current_time - last_damage_time > 1000:
        player_health -= 1
        last_damage_time = current_time
        if player_health <= 0:
          game_over = True
          try:
            pygame.mixer.music.stop()
          except:
            pass

    # Анимация зомби
    zombie['anim_timer'] += 1
    if zombie['anim_timer'] >= 6:
      zombie['anim_timer'] = 0
      if zombie_frames:
        zombie['anim_index'] = (zombie['anim_index'] + 1) % len(zombie_frames)

    # Попадание пуль
    hit_zombie = False
    for bullet in bullets[:]:
      if zombie_rect.collidepoint(bullet['x'], bullet['y']):
        bullets.remove(bullet)
        hit_zombie = True

        # Звук попадания в зомби
        if hit_sound:
          hit_sound.play()

        # Шанс хедшота 20%
        is_headshot = random.random() < 0.2
        if is_headshot:
          zombie['hp'] = 0
          headshot_texts.append(
              {'x': zombie['x'] + 10, 'y': ground_y - 95, 'timer': 45}
          )
        else:
          zombie['hp'] -= 1
        break

    if hit_zombie and zombie['hp'] <= 0:
      zombies.remove(zombie)
      continue

    # Отрисовка зомби
    if zombie_frames:
      z_image = zombie_frames[zombie['anim_index']]
      if not zombie['facing_right']:
        z_image = pygame.transform.flip(z_image, True, False)
      screen.blit(z_image, (zombie['x'] - camera_x, ground_y - 80))

    # Полоска здоровья зомби
    bar_w, bar_h = 40, 5
    bar_x = zombie['x'] - camera_x + 20
    bar_y = ground_y - 92
    hp_ratio = zombie['hp'] / zombie['max_hp']
    pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_w, bar_h))
    pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))

  # --- ТЕКСТЫ ХЕДШОТОВ И ХИЛЛА ---
  for hs in headshot_texts[:]:
    hs['timer'] -= 1
    if hs['timer'] <= 0:
      headshot_texts.remove(hs)
    else:
      hs_surf = font.render("HEADSHOT!", True, YELLOW)
      screen.blit(hs_surf, (hs['x'] - camera_x, hs['y']))

  for ft in floating_texts[:]:
    ft['y'] -= 0.5
    ft['timer'] -= 1
    if ft['timer'] <= 0:
      floating_texts.remove(ft)
    else:
      ft_surf = font.render(ft['text'], True, GREEN)
      screen.blit(ft_surf, (ft['x'] - camera_x, ft['y']))

  # --- ВЫБОР СПРАЙТА ИГРОКА ---
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

  if not facing_right:
    current_image = pygame.transform.flip(current_image, True, False)

  screen.blit(current_image, (player_x - camera_x, player_y))

  # Вспышка выстрела
  if is_shooting:
    fx = player_x + 72 if facing_right else player_x + 8
    pygame.draw.circle(
        screen, (255, 255, 0), (int(fx - camera_x), int(player_y + 24)), 5
    )
    pygame.draw.circle(
        screen, (255, 120, 0), (int(fx - camera_x), int(player_y + 24)), 2
    )

  # --- ПОЛОСКА ЗДОРОВЬЯ ИГРОКА ---
  p_bar_w, p_bar_h = 50, 6
  p_bar_x = player_x - camera_x + 15
  p_bar_y = player_y - 14
  p_ratio = player_health / max_player_health
  pygame.draw.rect(screen, RED, (p_bar_x, p_bar_y, p_bar_w, p_bar_h))
  pygame.draw.rect(
      screen, GREEN, (p_bar_x, p_bar_y, int(p_bar_w * p_ratio), p_bar_h)
  )

  # --- ИНТЕРФЕЙС: ПАТРОНЫ ---
  ammo_text = font_hud.render(f"Патроны: {ammo}/{max_ammo}", True, WHITE)
  ammo_rect = ammo_text.get_rect(bottomright=(WIDTH - 20, HEIGHT - 20))
  pygame.draw.rect(screen, (0, 0, 0, 150), ammo_rect.inflate(16, 10), border_radius=4)
  screen.blit(ammo_text, ammo_rect)

  # --- ПОДСКАЗКИ ВЗАИМОДЕЙСТВИЯ ---
  if near_object:
    prompt_text = font.render(
        f"Нажмите [E] — {near_object['name']} ({near_object['state']})",
        True,
        WHITE,
    )
    text_rect = prompt_text.get_rect(center=(WIDTH // 2, 40))
    pygame.draw.rect(
        screen, (30, 30, 30), text_rect.inflate(20, 10), border_radius=6
    )
    screen.blit(prompt_text, text_rect)

  if message_timer > 0:
    message_timer -= 1
    msg_surface = font_large.render(interaction_message, True, YELLOW)
    msg_rect = msg_surface.get_rect(center=(WIDTH // 2, 85))
    screen.blit(msg_surface, msg_rect)

  pygame.display.flip()
  clock.tick(60)

pygame.quit()