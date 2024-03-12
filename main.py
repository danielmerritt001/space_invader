import pygame
from pygame import mixer
from pygame.locals import *
import random
# from pygame.sprite import _Group

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.font.init()

#fps
clock = pygame.time.Clock()
fps = 60

screen_width = 600
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Space Invaders')

#define fonts
font30  = pygame.font.SysFont('Constantia', 30)
font40  = pygame.font.SysFont('Constantia', 40)

#load sounds
explosion_fx = pygame.mixer.Sound("img/explosion.wav")
explosion_fx.set_volume(0.15)
explosion2_fx = pygame.mixer.Sound("img/explosion2.wav")
explosion2_fx.set_volume(0.15)
laser_fx = pygame.mixer.Sound("img/laser.wav")
laser_fx.set_volume(0.15)

#define game variables
rows = 5
columns = 5
alien_cooldown = 1000
last_alien_shot = pygame.time.get_ticks()
max_enemy_bullets = 100
countdown = 3
last_count = pygame.time.get_ticks()
game_over = 0

#colors
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)

#load image
bg = pygame.image.load("img/bg.png")

def draw_bg():
  screen.blit(bg, (0, 0))

def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

# create spaceship class
class Spaceship(pygame.sprite.Sprite):
  def __init__(self, x, y, health):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.image.load("img/spaceship.png")
    self.rect = self.image.get_rect()
    self.rect.center = [x, y]
    self.health_start = health
    self.health_remaining = health
    self.last_shot = pygame.time.get_ticks()

  def update(self):
    #set movement speed
    speed = 8
    cooldown = 500 #milliseconds
    game_over = 0

    #keypresses
    key = pygame.key.get_pressed()
    if key[pygame.K_LEFT] and self.rect.left > 0:
      self.rect.x -= speed
    if key[pygame.K_RIGHT] and self.rect.right < screen_width:
      self.rect.x += speed
      #record current time
    time_now = pygame.time.get_ticks()
      # Shooting
    # if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
    #   bullet = Bullets(self.rect.centerx, self.rect.top)
    #   bullet_group.add(bullet)
    #   self.last_shot = time_now


    #update mask
    self.mask = pygame.mask.from_surface(self.image)

    #draw health bar
    pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
    if self.health_remaining > 0:
      pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * self.health_remaining / self.health_start), 15))
    elif self.health_remaining <= 0:
      explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
      explosion_group.add(explosion)
      game_over = -1
      self.kill()
    return game_over

class Bullets(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.image.load("img/bullet.png")
    self.rect = self.image.get_rect()
    self.rect.center = [x, y]
  
  def update(self):
    self.rect.y -= 5
    if self.rect.bottom < 0:
      self.kill()
    if pygame.sprite.spritecollide(self, alien_group, True):
      self.kill()
      explosion_fx.play()
      explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
      explosion_group.add(explosion)


# create Alien class
class Aliens(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.image.load("img/alien" + str(random.randint(1,5)) + ".png")
    self.rect = self.image.get_rect()
    self.rect.center = [x, y]
    self.move_counter = 0
    self.move_direction = 1
  
  def update(self):
    self.rect.x += self.move_direction
    self.move_counter += 1
    if abs(self.move_counter) > 75:
      self.move_direction *=-1
      self.move_counter *= self.move_direction
    
#create alien bullets class
class Alien_Bullets(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.image.load("img/alien_bullet.png")
    self.rect = self.image.get_rect()
    self.rect.center = [x, y]
  
  def update(self):
    self.rect.y += 2
    if self.rect.top > screen_height:
      self.kill()
    if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
      self.kill()
      spaceship.health_remaining -= 1
      explosion2_fx.play()
      explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
      explosion_group.add(explosion)

#create Explosions class
class Explosion(pygame.sprite.Sprite):
  def __init__(self, x, y, size):
    self.images = []
    pygame.sprite.Sprite.__init__(self)
    for num in range(1,6):
      img = pygame.image.load(f"img/exp{num}.png")
      if size == 1:
        img = pygame.transform.scale(img, (20, 20))
      if size == 2:
        img = pygame.transform.scale(img, (40, 40))
      if size == 3:
        img = pygame.transform.scale(img, (160, 160))
      self.images.append(img)
    self.index= 0
    self.image = self.images[self.index]
    self.rect = self.image.get_rect()
    self.rect.center = [x, y]
    self.counter = 0

  def update(self):
    explosion_speed = 3
    self.counter += 1
    if self.counter >= explosion_speed and self.index< len(self.images) - 1:
      self.counter = 0
      self.index +=1
      self.image = self.images[self.index]
    if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
      self.kill()


#create sprite groups
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

def create_aliens():
  for row in range(rows):
    for item in range(columns):
      alien = Aliens(100 + item * 100, 100 + row * 100 )
      alien_group.add(alien)

create_aliens()

#create player
spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
spaceship_group.add(spaceship)
run = True

while run:

  clock.tick(fps)

  #draw background
  draw_bg()

  if countdown == 0:
  #create random alien bullets
  #record current time
    time_now = pygame.time.get_ticks()
    if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < max_enemy_bullets and len(alien_group) > 0:
      attacking_alien = random.choice(alien_group.sprites())
      alien_bullet = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
      alien_bullet_group.add(alien_bullet)
      last_alien_shot = time_now

    #check for win
    if len(alien_group) == 0:
      game_over = 1
    
    #update spaceship and check for loss
    if game_over == 0:
      game_over = spaceship.update()

    
      #update sprite groups
      bullet_group.update()
      alien_group.update()
      alien_bullet_group.update()
    else:
      if game_over == -1:
        draw_text('GAME OVER!', font40, white, int(screen_width / 2 - 110), int(screen_height / 2 + 140))
      if game_over == 1:
        draw_text('YOU WIN!', font40, white, int(screen_width / 2 - 110), int(screen_height / 2 + 140))

  
  if countdown > 0:
    draw_text('GET READY!', font40, white, int(screen_width / 2 - 110), int(screen_height / 2 + 140))
    draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 200))
    count_timer = pygame.time.get_ticks()
    if count_timer - last_count > 1000:
      countdown -= 1
      last_count = count_timer
  
  explosion_group.update()
  
  #event handlers
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False
    #allow for fast shooting but no holding down the space bar
    if event.type == pygame.KEYDOWN and event.key == 32 and countdown == 0 and game_over == 0:
      print('Thanks for testing this Caleb')
      laser_fx.play()
      bullet = Bullets(spaceship.rect.centerx, spaceship.rect.top)
      bullet_group.add(bullet)
      # self.last_shot = time_now

  #draw spaceship
  spaceship_group.draw(screen)
  bullet_group.draw(screen)
  alien_group.draw(screen)
  alien_bullet_group.draw(screen)
  explosion_group.draw(screen)

  pygame.display.update()

pygame.quit()