""" Tilemap game """

import sys
from sprites import *
from tilemap import *


# HUD functions
def draw_player_health(surf, x, y, pct):
    if pct < 0:
        pct = 0
    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, round(fill), BAR_HEIGHT)
    if pct > 0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED
    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)


class Game:
    """ initialize pygame and create game window
    """
    def __init__(self):
        pg.mixer.pre_init(44100, -16, 1, 2048)
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        # self.running = True
        # self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()

    def draw_text(self, text, font_name, size, color, x, y, align='nw'):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == 'nw':
            text_rect.topleft = (x, y)
        if align == 'ne':
            text_rect.topright = (x, y)
        if align == 'sw':
            text_rect.bottomleft = (x, y)
        if align == 'se':
            text_rect.bottomright = (x, y)
        if align == 'n':
            text_rect.midtop = (x, y)
        if align == 's':
            text_rect.midbottom = (x, y)
        if align == 'e':
            text_rect.midright = (x, y)
        if align == 'w':
            text_rect.midleft = (x, y)
        if align == 'center':
            text_rect.center = (round(x), round(y))
        self.screen.blit(text_surface, text_rect)

    # noinspection PyShadowingNames,PyAttributeOutsideInit
    def load_data(self):
        """ Load game images and sounds
        """
        game_dir = path.dirname(__file__)
        img_dir = path.join(game_dir, 'img')
        snd_dir = path.join(game_dir, 'snd')
        music_dir = path.join(game_dir, 'music')
        cover_dir = path.join(img_dir, 'cover_img')
        self.map_dir = path.join(game_dir, 'maps')

        self.title_font = path.join(img_dir, 'Catwalzhari-ywL2Y.ttf')
        self.hud_font = path.join(img_dir, 'CardinalRegular-vmY4.ttf')
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))

        # self.test_img = pg.image.load(
        #     path.join(img_dir, TEST_IMG)).convert_alpha()
        # self.test_img = pg.transform.scale(self.test_img, (64, 64))

        self.player_img = pg.image.load(
            path.join(img_dir, PLAYER_IMG)).convert_alpha()

        self.flash_img_up = pg.image.load(
            path.join(img_dir, FLASH_IMG[0])).convert_alpha()
        self.flash_img_dn = pg.image.load(
            path.join(img_dir, FLASH_IMG[1])).convert_alpha()
        self.flash_img_lt = pg.image.load(
            path.join(img_dir, FLASH_IMG[2])).convert_alpha()
        self.flash_img_rt = pg.image.load(
            path.join(img_dir, FLASH_IMG[3])).convert_alpha()

        self.mob_img = pg.image.load(
            path.join(img_dir, MOB_IMG)).convert_alpha()
        self.mob_img = pg.transform.scale2x(self.mob_img)
        self.splat = pg.image.load(
            path.join(img_dir, SPLAT)).convert_alpha()
        self.splat = pg.transform.scale(self.splat, (64, 64))

        self.cover_images = {}
        for item in COVER_IMGS:
            self.cover_images[item] = pg.image.load(
                path.join(cover_dir, COVER_IMGS[item])).convert_alpha()

        # Load spritesheet image
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))
        self.spidersheet = Spritesheet(path.join(img_dir, SPIDERSHEET))
        self.watersheet_b = Spritesheet(path.join(img_dir, WATERSHEET_B))
        self.watersheet_t = Spritesheet(path.join(img_dir, WATERSHEET_T))

        # Lighting effect
        self.fog = pg.Surface((WIDTH, HEIGHT))
        self.fog.fill(NIGHT_COLOR)
        self.light_mask = pg.image.load(
            path.join(img_dir, LIGHT_MASK)).convert_alpha()
        self.light_mask = pg.transform.scale(self.light_mask, LIGHT_RADIUS)
        self.light_rect = self.light_mask.get_rect()

        # Load sound
        music_dir = path.join(game_dir, 'music')
        snd_dir = path.join(game_dir, 'snd')

        pg.mixer.music.load(path.join(music_dir, BG_MUSIC))
        # snd = self.atk_snds
        # if snd.get_num_channels() > 2:
        #     snd.stop()
        # snd.play()
        # self.atk_snds = pg.mixer.Sound(path.join(snd_dir, PLAYER_ATK))
        #     s.set_volume(0.3)

    # noinspection PyAttributeOutsideInit
    def new(self):
        """ Initialize all variables and do all setup for a new game
        """
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.water = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.cover = pg.sprite.Group()
        self.flash = pg.sprite.Group()
        self.map = TiledMap(path.join(self.map_dir, 'redo_map1.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

        for tile_object in self.map.tmxdata.objects:
            t_obj = tile_object
            obj_center = vec(
                t_obj.x + t_obj.width / 2, t_obj.y + t_obj.height / 2)
            obj_list = ['wall', 'edge', 'border',
                        'nature_obs', 'falls_b', 'falls_t']

            if t_obj.name in self.cover_images:
                CoverLayer(
                    self, obj_center, t_obj.name)

            if t_obj.name == 'Player':
                self.player = Player(self, t_obj.x, t_obj.y)
            if t_obj.name == 'spider':
                self.mob = Mob(self, t_obj.x, t_obj.y)
            if t_obj.name == 'falls_b':
                FallsBtm(self, t_obj.x, t_obj.y, t_obj.width, t_obj.height)
            if t_obj.name == 'falls_t':
                FallsTop(self, t_obj.x, t_obj.y, t_obj.width, t_obj.height)

            for i in obj_list:
                if t_obj.name == i in obj_list:
                    Obstacle(
                        self, t_obj.x, t_obj.y, t_obj.width, t_obj.height)

        self.camera = Camera(self.map.width, self.map.height)
        self.draw_debug = False
        self.paused = False
        self.night = False

    # noinspection PyAttributeOutsideInit
    def run(self):
        """ Game loop - set self.playing = False to end the game
        """
        self.playing = True
        pg.mixer.music.play(loops=-1)
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        """ Update portion of the game loop
        """
        self.all_sprites.update()
        self.camera.update(self.player)

        # Mobs hit player
        hits = pg.sprite.spritecollide(
            self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            # if random() < 0.7:
            #     choice(self.plr_hit_snds).play()
            self.player.health -= MOB_DMG
            hit.vel = vec(0, 0)
            if self.player.health <= 0:
                self.playing = False
        if hits:
            # self.player.hit()
            self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)

        # Flash hits Mob
        hits = pg.sprite.groupcollide(self.mobs, self.flash, False, True)
        for mob in hits:
            for flash in hits[mob]:
                mob.health -= flash.damage
            mob.vel = vec(0, 0)

    def draw_grid(self):
        """ Draws background grid
        """
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def render_fog(self):
        # Draw light mask (gradient) onto fog image
        self.fog.fill(NIGHT_COLOR)
        self.light_rect.center = self.camera.apply(self.player).center
        self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_MULT)

    def draw(self):
        """ Draws images to the screen
        """
        # Framerate display
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))

        # Apply camera
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        # self.draw_grid() # Older code

        # Draws sprites to screen
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            if self.draw_debug:
                pg.draw.rect(
                    self.screen, CYAN, self.camera.apply_rect(
                        sprite.hit_rect), 1)

        # Display for hit rect debug - 'h' key to toggle in game
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(
                    self.screen, CYAN, self.camera.apply_rect(wall.rect), 1)
            for obj in self.cover:
                pg.draw.rect(
                    self.screen, WHITE, self.camera.apply_rect(obj.rect), 1)
        # pg.draw.rect(self.screen, WHITE, self.camera.apply(self.player), 2)

        if self.night:
            self.render_fog()

        # HUD functions
        draw_player_health(
            self.screen, 10, 10, self.player.health / PLAYER_HEALTH)

        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text(
                "Paused", self.title_font, 105, LIGHTBLUE, WD2, HD2,
                align="center")

        pg.display.flip()

    # noinspection PyAttributeOutsideInit
    def events(self):
        """ Catch all events here
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pg.K_p:
                    self.paused = not self.paused
                if event.key == pg.K_n:
                    self.night = not self.night

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        self.screen.fill(BLACK)
        self.draw_text(
            GO_TXT, self.title_font, 100, RED, WD2, HD2, align='center')
        self.draw_text(
            START_TXT, self.title_font, 50, WHITE, WD2, HT34, align='center')
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False


# Create game object
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()

# pg.quit()
