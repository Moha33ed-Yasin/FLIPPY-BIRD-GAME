from os.path import join, split, abspath
from settings import HALF_HEIGHT, HALF_WIDTH, WIDTH
import pygame as pg

main_dir = split(abspath(__file__))[0]

def load_image(image_name, size):
    img = pg.image.load(join(main_dir, image_name)).convert_alpha()
    return pg.transform.scale(img, size)

def train_animate(timer, _delay, _frames:list, replay = True):
    return _frames[timer // _delay % len(_frames)] if replay else _frames[-1 if timer // _delay >= len(_frames) - 1 else timer // _delay]

def loadsound(_path):
    if not pg.mixer.get_init():pg.mixer.init()
    return pg.mixer.Sound(join(main_dir, _path))


class GameInfo():

    bestscore = 0
    breakscore = False

    def __init__(self, game, factor):
        pg.font.init()

        label_size = (HALF_WIDTH * 1.2, HALF_HEIGHT//2)
        cell_size = (25, 30)
        medal_size = (63, 45) 

        self.game = game
        self.screen = game.screen
        self.timer = 0
        self.font = pg.font.SysFont(["Fixedsys", "OCR A Extended", "Small Fonts Regular"], 100, False, True)
        self.mfont = pg.font.SysFont(["Fixedsys", "OCR A Extended", "Small Fonts Regular"], 50, False, False)
        #score
        self.factor = factor
        self.uniscore = 0
        self.scoreshow = None
        self.scoreresult = None
        self.hintshow = False

        #load features
        self.intro = [
            load_image("assets/empty.png", label_size),
            load_image("assets/_icon0.png", label_size),
            load_image("assets/_icon1.png", label_size),
            load_image("assets/icon.png", label_size)]

        self.icons = [
            load_image("assets/pause.png", cell_size), 
            load_image("assets/play.png", cell_size)]

        self.medels = [
            pg.transform.rotate(load_image("assets/medal_1.png", medal_size), 30), 
            pg.transform.rotate(load_image("assets/medal_2.png", medal_size), 30), 
            pg.transform.rotate(load_image("assets/medal_3.png", medal_size), 30)
        ]
        self.instruc = load_image("assets/hint1.png", (65, 50))
        self.arrow = load_image("assets/hint2.png", (25, 25))
        self.hand = load_image("assets/hint3.png", (60, 50))
        self.game_over = load_image("assets/over.png", label_size)
        self.game_list = load_image("assets/list.png", (HALF_WIDTH, HALF_HEIGHT))
        self.best_stamp =  load_image("assets/stamp.png", (80, 60))
        self.best_stamp =  pg.transform.rotate(self.best_stamp, 20)
        self.retry_button_1 = load_image("assets/retry_button.png", (HALF_WIDTH // 2, HALF_HEIGHT// 6.7))
        self.retry_button_2 = pg.transform.scale(self.retry_button_1, [x / 1.1 for x in self.retry_button_1.get_size()])
        self.retry_anime = False

    @property
    def score(self): return self.uniscore // self.factor

    @property
    def score_size(self):
        return self.font.size(f"{self.score}")
    @property
    def button_size(self):
        return self.retry_button_1.get_size()

    def score_up(self): self.uniscore += 1


    def drawHints(self, pos):
        self.screen.blit(self.instruc, pos)
        self.screen.blit(self.arrow, [pos[0] + 22, pos[1] + 50])
        self.screen.blit(self.hand, [pos[0] + 22, pos[1] + 80])

    def drawIntro(self, animate=True, delay=50, _hint=True, hint_pos = (0, 0)):
        hinted = False
        f = train_animate(self.timer, delay, self.intro, False)
        self.screen.blit(f, [HALF_WIDTH//2.5, HALF_HEIGHT//5])
        if _hint and self.timer >= 8000:
            self.drawHints(hint_pos)
            hinted = True
        if animate and not hinted: self.timer += 1

    def drawIcons(self): self.screen.blit(self.icons[self.game.pause], [WIDTH - 40, 10])

    def drawScore(self, pos:list|tuple = [380, 20], score_color= (0, 0, 0)):
        self.scoreshow = self.font.render(f"{self.score}", False, score_color)
        self.screen.blit(self.scoreshow, pos)

    def drawGameOver(self, pos:list|tuple = [160, 200]):self.screen.blit(self.game_over, pos)

    def drawGameList(self, pos, button_pos, result_pos, result_size, result_color, best_score_pos, best_score_color, medal, medal_pos, stamp_pos):
        rX, rY = result_pos
        bX, bY = best_score_pos
        sX, sY = stamp_pos
        sX, sY = stamp_pos
 
        color = result_color
        self.screen.blit(self.game_list, pos)

        #record best score
        if self.score >= self.bestscore: color = best_score_color
        if self.breakscore: 
            self.screen.blit(self.best_stamp, [pos[0] + sX, pos[1] + sY])

        self.scoreresult = self.mfont.render(f"{self.score}", False, color)
        self.best = self.mfont.render(f"{self.bestscore}", False, result_color)
        self.screen.blit(pg.transform.scale(self.scoreresult, result_size), (pos[0] + rX, pos[1] + rY))
        self.screen.blit(pg.transform.scale(self.best, result_size), (pos[0] + bX, pos[1] + bY))
        self.screen.blit([self.retry_button_1, self.retry_button_2][self.retry_anime], [button_pos, [button_pos[0] + 10, button_pos[1] + 10]][self.retry_anime])
        if medal != None:self.screen.blit(self.medels[medal], (pos[0] + medal_pos[0], pos[1] + medal_pos[1]))

    def on_mouse_click(self,  event:pg.event.Event, postop:list|tuple = (600, 510), posbottom:list|tuple = (400, 450)):
        mx, my = pg.mouse.get_pos()
        tx, ty = postop
        bx, by = posbottom
        self.retry_anime = tx <= mx <= bx and ty <= my <= by
        return event.type == pg.MOUSEBUTTONDOWN

    @classmethod
    def set_bestscore(cls, newbest):cls.bestscore = newbest

    @classmethod
    def set_breakscore(cls, _:bool):cls.breakscore = _

class GameSound:
    sjump = loadsound("assets/sounds/sfx_wing.wav")
    spass = loadsound("assets/sounds/sfx_point.wav")
    scollide = loadsound("assets/sounds/sfx_hit.wav")
    sdied = loadsound("assets/sounds/sfx_die.wav")
    smouse_over = loadsound("assets/sounds/sfx_swooshing.wav")