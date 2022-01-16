import pygame as pg


class Pole_vvoda():
    def __init__(self, x, y, width, height, limit) -> None:
        self.font = pg.font.Font(None, 20)
        self.input_box = pg.Rect(x, y, width, height)
        self.color = pg.Color('white')
        self.text = ''
        self.active = False
        self.limit = limit

    def draw(self, screen):
        txt_surface = self.font.render(self.text, True, self.color)
        screen.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 5))
        pg.draw.rect(screen, self.color, self.input_box, 2)

    def update(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.get_box().collidepoint(event.pos):
                self.change_act(not self.get_act())
            else:
                self.change_act(False)
        if event.type == pg.KEYDOWN:
            if self.get_act():
                if event.key == pg.K_BACKSPACE:
                    self.change_text(self.get_text()[:-1])
                else:
                    self.change_text(self.get_text() + event.unicode)

    def get_act(self):
        return self.active

    def get_box(self):
        return self.input_box

    def change_act(self, act):
        self.active = act

    def change_text(self, text):
        if len(text) <= self.limit:
            self.text = text
    
    def get_text(self):
        return self.text


if __name__ == '__main__':
    pg.init()
    display = pg.display.set_mode((500, 500))
    clock = pg.time.Clock()
    text_input = Pole_vvoda(100, 100, 300, 30, 20)
    done = False
    while not done:
        for event in pg.event.get():
            text_input.update(event)
        display.fill((30, 30, 30))
        text_input.draw(display)
        pg.display.flip()
        clock.tick(30)
