from pydoc import text
import re
import pygame as pg

class Pole_vvoda():
    def __init__(self, x, y, width, height) -> None:
        self.font = pg.font.Font(None, 20)
        self.input_box = pg.Rect(x, y, width, height)
        self.color = pg.Color('white')
        self.text = ''
        self.active = False

    def draw(self, text, screen):
        txt_surface = self.font.render(self.text, True, self.color)
        screen.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 5))
        pg.draw.rect(screen, self.color, self.input_box, 2)

    def get_act(self):
        return self.active

    def get_box(self):
        return self.input_box

    def change_act(self, act):
        self.active = act

    def change_text(self, text):
        self.text = text
    
    def get_text(self):
        return self.text


pg.init()
screen = pg.display.set_mode((640, 480))
clock = pg.time.Clock()
text_input = Pole_vvoda(100, 100, 300, 30)
done = False

while done == False:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        if event.type == pg.MOUSEBUTTONDOWN:
            if text_input.get_box().collidepoint(event.pos):
                text_input.change_act(not text_input.get_act())
            else:
                text_input.change_act(False)
        if event.type == pg.KEYDOWN:
            if text_input.get_act():
                if event.key == pg.K_RETURN:
                    print(text_input.get_text())
                    text_input.change_text('')
                elif event.key == pg.K_BACKSPACE:
                    text_input.change_text(text_input.get_text()[:-1])
                else:
                    text_input.change_text(text_input.get_text() + event.unicode)
    screen.fill((30, 30, 30))
    text_input.draw(text, screen)
    pg.display.flip()
    clock.tick(30)


if __name__ == '__main__':
    pg.init()
    pg.quit()