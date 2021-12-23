import os
import sys
import random
import pygame
import math
from pygame.math import Vector2

pygame.init()
size = width, height = 1000, 1000
screen = pygame.display.set_mode(size)
screen_rect = (0, 0, width, height)
all_sprites = pygame.sprite.Group()
enemies_sprites = pygame.sprite.Group()


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


class Bullet:
    def __init__(self, x, y, mx, my, speed):
        self.pos = (x, y)
        self.speed = speed
        self.dir = (mx - x, my - y)
        length = math.hypot(*self.dir)
        if length == 0.0:
            self.dir = (0, -1)
        else:
            self.dir = (self.dir[0] / length, self.dir[1] / length)
        angle = math.degrees(math.atan2(-self.dir[1], self.dir[0]))

        self.bullet = pygame.Surface((7, 2)).convert_alpha()
        self.bullet.fill((255, 176, 46))
        self.bullet = pygame.transform.rotate(self.bullet, angle)

    def update(self):
        self.pos = (self.pos[0] + self.dir[0] * self.speed,
                    self.pos[1] + self.dir[1] * self.speed)

    def draw(self, surf):
        bullet_rect = self.bullet.get_rect(center=self.pos)
        surf.blit(self.bullet, bullet_rect)


class Pers(pygame.sprite.Sprite):
    def __init__(self, dx, dy, speed):
        super().__init__(all_sprites)
        self.speed = speed
        self.image = load_image("sprite.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(dx, dy))
        self.rect.x = dx
        self.rect.y = dy
        self.orig = self.image
        screen.blit(self.image, self.rect)

    def update(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_s]:
            self.rect.y += self.speed
        elif key[pygame.K_w]:
            self.rect.y -= self.speed
        if key[pygame.K_d]:
            self.rect.x += self.speed
        elif key[pygame.K_a]:
            self.rect.x -= self.speed
        self.rotate()

    def rotate(self):
        x, y, w, h = self.rect
        direction = pygame.mouse.get_pos() - Vector2(x + w // 2, y + h // 2)
        radius, self.angle = direction.as_polar()
        self.image = pygame.transform.rotate(self.orig, - self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def shoot(self):
        mx, my = pygame.mouse.get_pos()
        bullet = Bullet(self.rect.centerx, self.rect.centery, mx, my, 30)
        bullets.append(bullet)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, dx, dy, speed, look_radius):
        super().__init__(enemies_sprites)
        self.speed = speed
        self.image = load_image("enemy.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(dx, dy))
        self.rect.x = dx
        self.rect.y = dy
        self.orig = self.image
        self.look_radius = look_radius
        screen.blit(self.image, self.rect)

    def update(self, player):
        self.rotate(player)

    def rotate(self, player):
        x1, y1, w1, h1 = self.rect
        x2, y2, w2, h2 = player.rect
        direction = Vector2(x2 + w2 // 2, y2 + h2 // 2) - Vector2(x1 + w1 // 2, y1 + h1 // 2)
        radius, self.angle = direction.as_polar()
        if radius <= self.look_radius:
            self.image = pygame.transform.rotate(self.orig, - self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)


van = pygame.sprite.Sprite(all_sprites)
van.image = load_image("dust.png")
van.rect = van.image.get_rect()

arrow = pygame.sprite.Sprite(all_sprites)
arrow.image = load_image("cross.png")
arrow.rect = arrow.image.get_rect()
bullets = []


def main():
    running = True
    fps = 60
    clock = pygame.time.Clock()
    pers = Pers(width // 2, height // 2, 3)
    enemy = Enemy(width // 2, height // 2, 3, 100)
    camera = Camera()
    while running:
        pygame.mouse.set_visible(False)
        screen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pers.shoot()
        pers.update()
        enemy.update(pers)
        for bullet in bullets[:]:
            bullet.update()
            if not screen.get_rect().collidepoint(bullet.pos):
                bullets.remove(bullet)
        if pygame.mouse.get_focused():
            arrow.rect.x, arrow.rect.y = pygame.mouse.get_pos()[0] - 30, pygame.mouse.get_pos()[1] - 30
        camera.update(pers)
        for sprite in all_sprites:
            camera.apply(sprite)
        for enemy in enemies_sprites:
            camera.apply(enemy)
        all_sprites.draw(screen)
        enemies_sprites.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        pygame.display.flip()
        clock.tick(fps)


if __name__ == '__main__':
    main()