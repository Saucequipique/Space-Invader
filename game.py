from typing import Any
from pygame import mixer
import pygame
from pygame.locals import *
import random

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 120

screen_width = 600
screen_height = 800
  
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Space Invanders')

font30 = pygame.font.SysFont('Constentia', 30)
font40 = pygame.font.SysFont('Constentia', 40)


explosion_fx = pygame.mixer.Sound("image/explosion.wav")
explosion_fx.set_volume(0.10)

explosion2_fx = pygame.mixer.Sound("image/explosion2.wav")
explosion2_fx.set_volume(0.10)

laser_fx = pygame.mixer.Sound("image/laser.wav")
laser_fx.set_volume(0.10)

rows = 5
cols = 5
alien_cooldown = 1000
last_alien_shot = pygame.time.get_ticks()
countdown = 3
last_count = pygame.time.get_ticks()
game_over = 0

red = (255,0,0)
green = (0,255,0)
white = (255,255,255)

bg = pygame.image.load("image/bg.png")

def draw_bg():
    screen.blit(bg,(0,0))
    
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('image/player.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()
    
    def update(self):
        speed = 8
        cooldown = 500
        game_over = 0
        
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT]and self.rect.right < screen_width:
            self.rect.x += speed
            
        time_now = pygame.time.get_ticks()
        
        if key[pygame.K_SPACE]and time_now - self.last_shot > cooldown :
            laser_fx.play()
            laser = Laser(self.rect.centerx, self.rect.top)
            laser_group.add(laser)
            self.last_shot = time_now
        
        self.mask = pygame.mask.from_surface(self.image)
        
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 15))
        elif self.health_remaining <= 0 :
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            game_over = -1
        return game_over

class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('image/laser.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
    
    def update(self):
        self.rect.y -= 5  
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self,aliens_group, True, pygame.sprite.collide_mask) :
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
        

class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('image/Alien' + str(random.randint(1,3))+ '.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1
        
    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction  *= -1
            self.move_counter *= self.move_direction

class Alien_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('image/alien_bullets.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
    
    def update(self):
        self.rect.y += 2  
        if self.rect.top > screen_height:
            self.kill() 
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            spaceship.health_remaining -= 1   
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)
            

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range (1,6):
            img = pygame.image.load(f"image/exp{num}.png")
            if size == 1:           
               img = pygame.transform.scale(img, (20, 20))
            if size == 2:
               img = pygame.transform.scale(img, (40, 40))
            if size == 3:
               img = pygame.transform.scale(img, (160, 160))
            self.images.append(img)
        self.index = 0    
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]      
        self.counter = 0
    
    def update(self):     
        explosion_speed = 3
        self.counter += 1
        
        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]  
            
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
                 self.kill()

spaceship_group = pygame.sprite.Group()
laser_group = pygame.sprite.Group()
aliens_group = pygame.sprite.Group()
alien_bullets_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

def create_aliens():
    for row in range(rows):
        for item in range(cols):
            aliens = Aliens(100 + item * 100, 100 + row * 70)
            aliens_group.add(aliens)

create_aliens()

spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
spaceship_group.add(spaceship)

run = True
while run : 
    
    clock.tick(fps)
    
    draw_bg()
    
    if countdown == 0:
    
        time_now = pygame.time.get_ticks()
        if time_now - last_alien_shot > alien_cooldown and len(alien_bullets_group) < 5 and len(aliens_group)> 0:
            attacking_alien = random.choice(aliens_group.sprites())
            alien_bullet = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
            alien_bullets_group.add(alien_bullet)
            last_alien_shot = time_now
        
        if len(aliens_group) == 0:
            game_over = 1
            
        if game_over == 0:
    
            game_over = spaceship.update()
    
            laser_group.update()
            aliens_group.update()
            alien_bullets_group.update()
        else:
            if game_over == -1:
                 draw_text('LE CANCER TA EU !', font40, white, int(screen_width / 2 - 130), int(screen_height / 2 + 50))
            if game_over == 1:
                 draw_text('TU EST UN SORCIER !', font40, white, int(screen_width / 2 - 150), int(screen_height / 2 + 50))     
        
    if countdown > 0:
        draw_text('FUME TOUTES LA ZAZA !', font40, white, int(screen_width / 2 - 150), int(screen_height / 2 + 50))
        draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 100))
        count_timer = pygame.time.get_ticks()
        if count_timer - last_count > 1000 :
            countdown -= 1
            last_count = count_timer
    
    explosion_group.update()
    
    spaceship_group.draw(screen)
    laser_group.draw(screen)
    aliens_group.draw(screen)
    alien_bullets_group.draw(screen)
    explosion_group.draw(screen)
 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    pygame.display.update()
    
pygame.quit()