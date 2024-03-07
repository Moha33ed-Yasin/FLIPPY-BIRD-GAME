from random import randint
from sys import exit
from settings import *
from statics import *
from Objects import *

# project
LIST = [HALF_WIDTH // 2.2, HEIGHT // 2.8]
BUTTON = [2 * HALF_WIDTH // 3, 3 * HEIGHT // 4]
class App():
    def __init__(self):
        self.screen = pg.display.set_mode(RES)
        self.timer = 0
        self.end_timer = 0
        self.fps = FPS
        self.clock = pg.time.Clock()

        self.start = False
        self.pause = False
        self.is_reseted = False
        self.list_enable = False
        self.mouse_on = False

        self.grass_loop = 0
        
        self.info = GameInfo(self, TIMEFACTOR)
        self.sound = GameSound() 
        self.bird = Bird((60, 45), 100, 3, 10, self)

        pg.display.set_caption("Flippy Brid🐤")

        #loads assets from resource
        self.background = {
            0:load_image("assets/background/background1.png", RES),
            1:load_image("assets/background/background2.png", RES),
            2:load_image("assets/background/background3.png", RES),
            3:load_image("assets/background/background4.png", RES)
        }
        self.daytime = randint(0, len(self.background)-1)

        grass_size = (WIDTH, LAND_HIGHT)
        self.grass = {
            0:load_image("assets/grass/0001.png", grass_size),
            1:load_image("assets/grass/0002.png", grass_size),
            2:load_image("assets/grass/0003.png", grass_size),
            3:load_image("assets/grass/0004.png", grass_size),
            4:load_image("assets/grass/0005.png", grass_size),
            5:load_image("assets/grass/0006.png", grass_size),
            6:load_image("assets/grass/0007.png", grass_size),
            7:load_image("assets/grass/0008.png", grass_size),
            8:load_image("assets/grass/0009.png", grass_size),
            9:load_image("assets/grass/0010.png", grass_size),
            10:load_image("assets/grass/0011.png", grass_size),
            11:load_image("assets/grass/0012.png", grass_size),
            12:load_image("assets/grass/0013.png", grass_size),
            13:load_image("assets/grass/0014.png", grass_size),
            14:load_image("assets/grass/0015.png", grass_size)
        }

        fen_size = BLOCKS_SIZE
        self.fens = {
            0:load_image("assets/fens/0001.png", fen_size),
            1:load_image("assets/fens/0002.png", fen_size),
            2:load_image("assets/fens/0003.png", fen_size),
            3:load_image("assets/fens/0004.png", fen_size),
            4:load_image("assets/fens/0005.png", fen_size)
        }

        self.blocks = TwoStandBlocks(self, self.fens[randint(0, len(self.fens)-1)], RANGERAN, FSPACE)

    def reset(self):
        self.info.set_breakscore(False)
        self.__init__()
        self.is_reseted = True 

    def score_track(self):
        if self.blocks.face(self.bird).gate_pass(self.bird, 10) and not self.blocks.face(self.bird).is_passed and not self.bird.is_died:
            self.info.score_up()
            if self.info.uniscore % TIMEFACTOR == 0:
                self.sound.spass.play()
                self.blocks.face(self.bird).is_passed = True

    def drawinfo(self):
        self.info.drawIcons()
        self.info.drawScore(pos=[HALF_WIDTH - self.info.score_size[0] // 4, self.info.score_size[0] // 8], score_color=WHITE_1)
        if self.bird.is_died:self.info.drawGameOver([HALF_HEIGHT//2, HALF_WIDTH//2])

    def mouse_track(self, event, pos, _region):
        click = self.info.on_mouse_click(event, pos, (pos[0] + _region[0], pos[1] + _region[1]))
        over = self.info.retry_anime
        if over and not self.mouse_on:self.sound.smouse_over.play() 
        if click:self.reset()
        self.mouse_on = over
    
    def rate_gameplay(self):
        if 10 <= self.info.score < 20: return 0
        if 20 <= self.info.score < 40: return 1
        if 40 <= self.info.score: return 2


    def input(self):
        for event in pg.event.get():
            
            if event.type == pg.QUIT:
                pg.quit()
                exit()

            elif event.type == pg.KEYDOWN:
                if not self.pause: self.bird.input(event.key)
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    exit()
                if event.key == pg.K_SPACE and not self.start: self.start = True
                if event.key == pg.K_TAB and self.start and not self.bird.is_died:self.pause = not self.pause
            
            if self.list_enable: self.mouse_track(event, BUTTON, self.info.button_size) # [195, 45]
            elif self.bird.is_died and event.type == pg.MOUSEBUTTONDOWN:self.list_enable = True

    def update(self):
        self.screen.blit(self.background[self.daytime], [0, 0])
        if not self.start:
            if self.is_reseted:
                sprites = self.blocks.group.sprites()
                def move_away(s): 
                    s.rect.x = -BLOCKS_WIDTH
                    s.inverse_rect.x = -BLOCKS_WIDTH
                    s.intersection_rect.x = -BLOCKS_WIDTH
                [move_away(s) for s in sprites]
            else:self.info.drawIntro(animate=True, delay=int(DELAYTIME * 8000), _hint=True, hint_pos= [HALF_WIDTH // 2, self.bird.rect.y])
        elif self.start and self.timer < 1500 and not self.pause:self.timer += 1
        elif self.timer >= 1500:
            sprites = TwoStandBlocks.group.sprites()
            if sprites[-1].rect.x <=  HALF_WIDTH: self.blocks = TwoStandBlocks(self, self.fens[randint(0, 4)], RANGERAN, FSPACE)
            [block.slide(-BLOCKS_WIDTH, DELAYTIME * (not self.pause and not self.bird.fail())) for block in sprites]

            self.score_track()
            self.drawinfo()

        self.screen.blit(train_animate(self.grass_loop, int(DELAYTIME * 2000 / self.fps) if self.fps != 0 else 1, self.grass), [0, HEIGHT - LAND_HIGHT])
        self.bird.update()

        # pause handle tab
        if self.pause:
            self.fps = 0
        else:
            self.fps = FPS

        # ending the game style
        if self.bird.is_died:
            if self.end_timer <= 50 and self.bird.is_collide:
                self.sound.scollide.play()
                self.screen.fill(WHITE)
            if self.list_enable:
                if self.info.score > self.info.bestscore:
                    self.info.set_bestscore(self.info.score)
                    self.info.set_breakscore(True)
                self.info.drawGameList(pos=LIST, 
                                       button_pos=BUTTON, 
                                       result_pos=[35, 50], 
                                       result_size=(35, 60), 
                                       result_color=WHITE_2, 
                                       best_score_pos=[35, 190], 
                                       best_score_color=GOLD, 
                                       medal=self.rate_gameplay(), 
                                       medal_pos=[308, 64], 
                                       stamp_pos=[65, 35]
                                      )

            self.end_timer += 1
        elif not self.pause:self.grass_loop += 1
        
        #back sound play
        pg.display.flip()

    def run(self):
        while True:
            self.input()
            self.update()
 
# Game Running ...
if __name__ == "__main__":
    game = App()
    game.run()
