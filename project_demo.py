import os
import sys
import pygame
import math
import random
from pygame.math import Vector2

pygame.init()
pygame.mixer.music.load('data/Grimes - Kill V Maim.mp3')
pygame.mixer.music.set_volume(0.4)
vystrel = pygame.mixer.Sound('data/vystrel.wav')
death = pygame.mixer.Sound('data/death.wav')
pygame.mixer.Sound.set_volume(vystrel, 0.5)
pygame.mixer.Sound.set_volume(death, 0.7)
size = width, height = 1000, 1000
fps = 60
clock = pygame.time.Clock()
screen = pygame.display.set_mode(size)
screen_rect = (0, 0, width, height)
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
particles = pygame.sprite.Group()
enemies_sprites = pygame.sprite.Group()


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "data/" + filename
    if not os.path.isfile(filename):
        print(f"Файл с изображением '{filename}' не найден")
        terminate()
    else:
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
        max_width = max(map(len, level_map))
        return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def start_screen():
    fon = pygame.transform.scale(load_image('fon.png'), (width, height))
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return 1
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                transit = credits()
                return transit
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return 'off'

        pygame.display.flip()
        clock.tick(fps)


def credits():
    fon = pygame.transform.scale(load_image('credits.png'), (width, height))
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_TAB):
                return 'credits'
        pygame.display.flip()
        clock.tick(fps)


def dead_screen():
    fon = load_image('dead_screen.png', -1)
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                fon.fill((0, 0, 0, 0))
                return 'restart'
        pygame.display.flip()
        clock.tick(fps)


def pause_screen():
    fon = load_image('pause_screen.png')
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                fon.fill((0, 0, 0, 0))
                return 'restart'
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                fon.fill((0, 0, 0, 0))
                return 'continue'
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                return 'start_screen'
        pygame.display.flip()
        clock.tick(fps)


def continue_screen():
    fon = load_image('continue_screen.png', -1)
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                fon.fill((0, 0, 0, 0))
                return 1
        pygame.display.flip()
        clock.tick(fps)


def final_screen():
    fon = load_image('final_screen.png', -1)
    screen.blit(fon, (0, 0))
    count = 0
    while True:
        if count == 99:
            create_particles((random.randint(50, 950), random.randint(1, 600)))
            count = 0
        count += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                fon.fill((0, 0, 0, 0))
                return 'start_screen'
        particles.update()
        screen.blit(fon, (0, 0))
        particles.draw(screen)
        pygame.display.flip()
        clock.tick(50)


class Particle(pygame.sprite.Sprite):
    fire = [load_image("star.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(particles)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        self.gravity = 1

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(screen_rect):
            self.kill()


def create_particles(position):
    particle_count = 10
    numbers = range(-7, 8)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.count = 0
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        if self.count == 59:
            self.count = 0
        else:
            self.count += 1
        self.cur_frame = self.count // 30
        self.image = self.frames[self.cur_frame]


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


tile_width = tile_height = 50
tile_images = {
    'wall': pygame.transform.scale(load_image('bricks2.png'), (50, 50)),
    'empty': pygame.transform.scale(load_image('floor.jpg'), (50, 50))
              }


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Bullet:
    def __init__(self, x, y, mx, my, speed, sender):
        self.pos = (x, y)
        self.speed = speed
        self.sender = sender
        self.dir = (mx - x, my - y)
        length = math.hypot(*self.dir)
        if length == 0.0:
            self.dir = (0, -1)
        else:
            self.dir = (self.dir[0] / length, self.dir[1] / length)
        angle = math.degrees(math.atan2(-self.dir[1], self.dir[0]))

        self.bullet = pygame.Surface((7, 3)).convert_alpha()
        self.bullet.fill((255, 176, 0))
        self.bullet = pygame.transform.rotate(self.bullet, angle)

    def update(self):
        self.pos = (self.pos[0] + self.dir[0] * self.speed,
                    self.pos[1] + self.dir[1] * self.speed)
        self.rect = pygame.Rect(self.pos[0] - 2, self.pos[1] - 2, 4, 4)

    def draw(self, surf):
        bullet_rect = self.bullet.get_rect(center=self.pos)
        surf.blit(self.bullet, bullet_rect)


class Player(pygame.sprite.Sprite):
    def __init__(self, dx, dy, speed):
        super().__init__(all_sprites)
        self.speed = speed
        self.alive = True
        self.image = load_image("main_ch.png")
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(dx, dy))
        self.rect.x = dx
        self.rect.y = dy
        self.orig = self.image
        screen.blit(self.image, self.rect)

    def update(self):
        key = pygame.key.get_pressed()
        if self.alive:
            if key[pygame.K_s]:
                self.rect.y += self.speed
                for wall in walls_group:
                    if pygame.sprite.collide_mask(self, wall):
                        self.rect.y -= self.speed
            elif key[pygame.K_w]:
                self.rect.y -= self.speed
                for wall in walls_group:
                    if pygame.sprite.collide_mask(self, wall):
                        self.rect.y += self.speed
            if key[pygame.K_d]:
                self.rect.x += self.speed
                for wall in walls_group:
                    if pygame.sprite.collide_mask(self, wall):
                        self.rect.x -= self.speed
            elif key[pygame.K_a]:
                self.rect.x -= self.speed
                for wall in walls_group:
                    if pygame.sprite.collide_mask(self, wall):
                        self.rect.x += self.speed
            self.rotate()

    def rotate(self):
        x, y, w, h = self.rect
        direction = pygame.mouse.get_pos() - Vector2(x + w // 2, y + h // 2)
        radius, self.angle = direction.as_polar()
        self.image = pygame.transform.rotate(self.orig, - self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def shoot(self):
        vystrel.play()
        mx, my = pygame.mouse.get_pos()
        bullet = Bullet(self.rect.centerx, self.rect.centery, mx, my, 30, 'player')
        bullets.append(bullet)

    def dead(self):
        self.image = pygame.transform.scale(load_image('dead_main_ch.png'), (50, 50))
        self.image = pygame.transform.rotate(self.image, - self.angle)
        self.alive = False


class Enemy(pygame.sprite.Sprite):
    def __init__(self, dx, dy, speed, look_radius):
        super().__init__(enemies_sprites)
        self.speed = speed
        self.count = 99
        self.angle = 0
        self.alive = True
        self.flag = False
        self.image = load_image("vrag.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(dx, dy))
        self.rect.x = dx
        self.rect.y = dy
        self.orig = self.image
        self.look_radius = look_radius
        screen.blit(self.image, self.rect)

    def update(self, player):
        x1, y1 = self.rect.x, self.rect.y
        x2, y2 = player.rect.x - 3, player.rect.y - 6
        self.dir = (x2 - x1, y2 - y1)
        length = math.hypot(*self.dir)
        if length <= 200:
            self.flag = True
        if self.flag:
            if length <= 80:
                if self.count == 99 and self.alive and player.alive:
                    self.shoot(player)
                    self.count = 0
                else:
                    self.count += 1
            else:
                if self.alive and player.alive:
                    self.dir = (self.dir[0] / length, self.dir[1] / length)
                    self.rotate(player)
                    self.rect.x = self.rect.x + self.dir[0] * self.speed
                    for wall in walls_group:
                        if pygame.sprite.collide_mask(self, wall):
                            self.rect.x = self.rect.x + self.dir[0] * - self.speed
                    self.rect.y = self.rect.y + self.dir[1] * self.speed
                    for wall in walls_group:
                        if pygame.sprite.collide_mask(self, wall):
                            self.rect.y = self.rect.y + self.dir[1] * - self.speed

    def rotate(self, player):
        x1, y1, w1, h1 = self.rect
        x2, y2, w2, h2 = player.rect
        direction = Vector2(x2 + w2 // 2, y2 + h2 // 2) - Vector2(x1 + w1 // 2, y1 + h1 // 2)
        radius, self.angle = direction.as_polar()
        self.image = pygame.transform.rotate(self.orig, - self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def shoot(self, player):
        vystrel.play()
        x2, y2, w2, h2 = player.rect
        bullet = Bullet(self.rect.centerx, self.rect.centery, x2 + w2 // 2, y2 + h2 // 2, 30, 'enemy')
        bullets.append(bullet)

    def dead(self):
        self.image = pygame.transform.scale(load_image('dead_vrag.png'), (50, 50))
        self.image = pygame.transform.rotate(self.image, - self.angle)
        self.alive = False


arrow = AnimatedSprite(load_image('cross.png'), 2, 1, pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
arrow.rect = arrow.image.get_rect()


def generate_level(level):
    new_player, x, y = None, None, None
    enemies = []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
                walls_group.add(Tile('wall', x, y))
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x * tile_width, y * tile_height, 3)
            elif level[y][x] == 'E':
                Tile('empty', x, y)
                new_enemy = Enemy(x * tile_width, y * tile_height, 3, 100)
                enemies.append(new_enemy)
    return new_player, x, y, enemies


def main(level, music):
    running = True
    musica = music
    player, level_x, level_y, enemies = generate_level(load_level(level))
    if musica:
        pygame.mixer.music.play()
    for i in range(len(enemies)):
        enemy = enemies[i]
    camera = Camera()
    while running:
        pygame.mouse.set_visible(False)
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return -1
            if event.type == pygame.MOUSEBUTTONDOWN and player.alive:
                player.shoot()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                if musica:
                    pygame.mixer.music.pause()
                    musica = False
                else:
                    pygame.mixer.music.unpause()
                    musica = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                gameover = pause_screen()
                if gameover != 'continue':
                    return gameover, False
        player.update()
        for enemy in enemies:
            enemy.update(player)
        for bullet in bullets[:]:
            bullet.update()
            if not screen.get_rect().collidepoint(bullet.pos) or pygame.sprite.spritecollideany(bullet, walls_group):
                bullets.remove(bullet)
            for enemy in enemies:
                if bullet.rect.colliderect(enemy.rect) and bullet.sender == 'player' and enemy.alive:
                    enemy.dead()
                    death.play()
            if bullet.rect.colliderect(player.rect) and bullet.sender == 'enemy':
                player.dead()
                death.play()
        if pygame.mouse.get_focused():
            arrow.rect.x, arrow.rect.y = pygame.mouse.get_pos()[0] - 30, pygame.mouse.get_pos()[1] - 30
            arrow.update()
        camera.update(player)

        for sprite in all_sprites:
            camera.apply(sprite)

        for sprite in tiles_group:
            camera.apply(sprite)

        for enemy in enemies_sprites:
            camera.apply(enemy)

        tiles_group.draw(screen)
        enemies_sprites.draw(screen)
        all_sprites.draw(screen)

        for bullet in bullets:
            bullet.draw(screen)

        if all(not e.alive for e in enemies):
            gameover = continue_screen()
            return gameover, musica

        if not player.alive:
            gameover = dead_screen()
            return gameover, musica

        pygame.display.flip()
        clock.tick(fps)


if __name__ == '__main__':
    running = True
    while running:
        game = True
        level = start_screen()
        while game:
            all_sprites = pygame.sprite.Group()
            tiles_group = pygame.sprite.Group()
            walls_group = pygame.sprite.Group()
            enemies_sprites = pygame.sprite.Group()
            bullets = []
            arrow = AnimatedSprite(load_image('cross.png'), 2, 1, 0, 0)
            if level == 1:
                gameover, music = main('level.txt', music=True)
                if gameover == 1:
                    level = 2
                elif gameover == 'start_screen':
                    game = False
                    pygame.mixer.music.stop()
                elif gameover == 'restart':
                    continue
            elif level == 2:
                gameover, music = main('level2.txt', music=True)
                if gameover == 1:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load('data/twin_peaks.mp3')
                    pygame.mixer.music.play()
                    gameover = final_screen()
                    pygame.mixer.music.stop()
                    game = False
                elif gameover == 'start_screen':
                    game = False
                    pygame.mixer.music.stop()
                elif gameover == 'restart':
                    continue
            elif level == 'off':
                game = False
                running = False
            elif level == 'credits':
                game = False
    pygame.quit()
    sys.exit()

