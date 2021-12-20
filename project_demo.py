import os
import sys
import pygame
import time
from pygame.math import Vector2

pygame.init()
size = width, height = 1000, 1000
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()


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


class Pers(pygame.sprite.Sprite):
    def __init__(self, dx, dy, speed):
        super().__init__(all_sprites)
        self.speed = speed
        self.image = load_image("sprite.png")
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(dx, dy))
        self.rect.x = dx
        self.rect.y = dy
        self.orig = self.image
        screen.blit(self.image, self.rect)

    def update(self, keys):
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
        radius, angle = direction.as_polar()
        self.image = pygame.transform.rotate(self.orig, - angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def shoot(self):
        x, y, w, h = self.rect
        direction = pygame.mouse.get_pos() - Vector2(x + w // 2, y + h // 2)
        radius, angle = direction.as_polar()
        bullet = pygame.sprite.Sprite(all_sprites)
        bullet.image = load_image('shot.jpg', -1)
        bullet.rect = bullet.image.get_rect()
        dx, dy, dw, dh = bullet.rect
        bullet.image = pygame.transform.scale(bullet.image, (dw // 15, dh // 15))
        orig = bullet.image
        bullet.image = pygame.transform.rotate(orig, - angle)
        bullet.rect.x = self.rect.x
        bullet.rect.y = self.rect.y
        screen.blit(bullet.image, bullet.rect)


arrow = pygame.sprite.Sprite(all_sprites)
arrow.image = load_image("cross.png")
arrow.rect = arrow.image.get_rect()


def main():
    running = True
    fps = 60
    clock = pygame.time.Clock()
    pers = Pers(width // 2, height // 2, 3)
    camera = Camera()
    while running:
        pygame.mouse.set_visible(False)
        screen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pers.shoot()
        pers.update(pygame.key.get_pressed())
        if pygame.mouse.get_focused():
            arrow.rect.x, arrow.rect.y = pygame.mouse.get_pos()[0] - 30, pygame.mouse.get_pos()[1] - 30
        camera.update(pers)
        for sprite in all_sprites:
            camera.apply(sprite)
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(fps)


if __name__ == '__main__':
    main()
