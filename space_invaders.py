import pygame, time
from pygame import mixer
import random

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width, screen_height = 600, 800

screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Space Invaders')

# fonts
font30 = pygame.font.SysFont('impact', 40)
font40 = pygame.font.SysFont('impact', 50)

# sounds
bg_music = pygame.mixer.Sound('Music/bg_music.wav')
bg_music.set_volume(0.25)
explosion_fx = pygame.mixer.Sound("Music/explosion.wav")
explosion_fx.set_volume(0.25)
explosion2_fx = pygame.mixer.Sound("Music/explosion2.wav")
explosion2_fx.set_volume(0.25)
shoot_wav = pygame.mixer.Sound("Music/shoot.wav")
shoot_wav.set_volume(0.25)

# game variables
cols = 5
rows = 5
enemy_cooldown = 1000
last_enemy_shot = pygame.time.get_ticks()
countdown = 3
last_count = pygame.time.get_ticks()
game_over = 0

# colors
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)

#define function for creating text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

class BG(pygame.sprite.Sprite):
    def __init__(self,groups,scale_factor):
        super().__init__(groups)
        bg_image = pygame.image.load('Documents/graphics/blue_bg.png').convert_alpha()
        bg_music.play()

        full_height = bg_image.get_height() * scale_factor
        full_width = bg_image.get_width() * scale_factor
        full_sized_image = pygame.transform.scale(bg_image, (full_width,full_height))

        self.image = pygame.Surface((full_width, full_height * 2))
        self.image.blit(full_sized_image,(0,0))
        self.image.blit(full_sized_image,(0, full_height))

        self.rect = self.image.get_rect(topleft = (0,0))
        self.pos = pygame.math.Vector2(self.rect.topleft)

    def update(self,dt):
        self.pos.y -= 250 * dt
        if self.rect.centery <= 0:
            self.pos.y = 0
        self.rect.y = round(self.pos.y)


#create spaceship class
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        #self.image = pygame.image.load("Documents/graphics/spaceship.png")
        self.image = pygame.image.load('Documents/graphics/space_ship.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.image = pygame.transform.rotate(self.image, 360)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        speed = 8
        cooldown = 500
        game_over = 0

        # player movement
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed

        time_now = pygame.time.get_ticks()
        # shoot
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            shoot_wav.play()
            bullet = Bullets(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = time_now

        #update mask
        self.mask = pygame.mask.from_surface(self.image)

        #draw health bar
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 15))
        elif self.health_remaining <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            game_over = -1
        return game_over


#create Aliens class
class Enemy(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.image.load('Documents/graphics/enemy' + str(random.randint(1, 5)) + '.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.image = pygame.transform.rotate(self.image, 180)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= self.move_direction


#create Bullets class
class Bullets(pygame.sprite.Sprite): 
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.image.load('Documents/graphics/redone.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 15))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, enemy_group, True):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)


#create Alien Bullets class
class Enemy_Bullets(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.image.load('Documents/graphics/bullet.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 25))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y += 2
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            #reduce spaceship health
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)


#create Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self,x,y,size):
        super().__init__()
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'Documents/graphics/exp{num}.png')
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            #add the image to the list
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0


    def update(self):
        explosion_speed = 3
        #update explosion animation
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        #if the animation is complete, delete explosion
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()
            
            
#BG
all_sprites = pygame.sprite.Group()
bg_height = pygame.image.load('Documents/graphics/blue_bg.png').get_height()
scale_factor = screen_height / bg_height
BG(all_sprites,scale_factor)

#create sprite groups
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
enemy_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()


def create_enemy():
    #generate aliens
    for row in range(rows):
        for item in range(cols):
            enemy = Enemy(100 + item * 100, 100 + row * 80)
            enemy_group.add(enemy)

create_enemy()


#create player
spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
spaceship_group.add(spaceship)

last_time = time.time()

run = True
while run:

    clock.tick(fps)
    dt = time.time() - last_time
    last_time = time.time()

    #BG game logic
    screen.fill('black')
    all_sprites.update(dt)
    all_sprites.draw(screen)


    if countdown == 0: 
        #create random alien bullets
        #record current time
        time_now = pygame.time.get_ticks()
        #shoot
        if time_now - last_enemy_shot > enemy_cooldown and len(enemy_bullet_group) < 5 and len(enemy_group) > 0:
            attacking_enemy = random.choice(enemy_group.sprites())
            enemy_bullet = Enemy_Bullets(attacking_enemy.rect.centerx, attacking_enemy.rect.bottom)
            enemy_bullet_group.add(enemy_bullet)
            last_enemy_shot = time_now

        #check if all the aliens have been killed
        if len(enemy_group) == 0:
            game_over = 1

        if game_over == 0:
            #update spaceship
            game_over = spaceship.update()

            #update sprite groups
            bullet_group.update()
            enemy_group.update()
            enemy_bullet_group.update()
            
        else:
            if game_over == -1:
                draw_text('GAME OVER!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))
                
            if game_over == 1:
                draw_text('YOU WIN!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 - 50))
        
    if countdown > 0:
        draw_text('GET READY', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))
        draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 100))
        count_timer = pygame.time.get_ticks()
        if count_timer - last_count > 1000:
            countdown -= 1
            last_count = count_timer


    # update explosion   
    explosion_group.update()

    #draw sprite group
    spaceship_group.draw(screen)
    bullet_group.draw(screen)
    enemy_group.draw(screen)
    enemy_bullet_group.draw(screen)
    explosion_group.draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False


    pygame.display.update()

pygame.quit()    
