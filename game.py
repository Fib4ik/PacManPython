from superwires import games, color
import random
import finder

CELL_SIZE = 32
MAP_WIDTH = 16
MAP_HEIGHT = 16

LIST_MAP = [list("################"), 
            list("#..............#"), 
            list("#.#.#.########.#"), 
            list("#.#.###.#.#..#.#"), 
            list("#.#.#.....#..#.#"), 
            list("#.....### ##.#.#"), 
            list("#.#...#    #.#.#"), 
            list("#.#####    #.#.#"), 
            list("#.#...######.#.#"), 
            list("#.#.#..........#"), 
            list("#.#.#.###.##.#.#"), 
            list("#.#.#...#..#.#.#"), 
            list("#............#.#"), 
            list("#.############.#"), 
            list("#..............#"), 
            list("################")]

BLOCK_MAP = "".join("".join(x) for x in LIST_MAP)

def cor(value):
    return (value - 1) * CELL_SIZE + CELL_SIZE / 2
def pos(value):
    return int(value // CELL_SIZE)

class BlockMap(object):
    def __init__(self, block_map):
        num_map = []
        temp = []
        self.points = 0
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                char_block = block_map[y * MAP_WIDTH + x]
                if char_block == "#":
                    Block(x = x + 1, y = y + 1)
                elif char_block == ".":
                    Point(x = x + 1, y = y + 1)
                    self.points += 1
    def get_max_points(self):
        return self.points

class WorldSetter(games.Sprite):
    def __init__(self, image, x = 1, y = 1):
        super(WorldSetter, self).__init__(image = image, x = cor(x), y = cor(y))
        games.screen.add(self)

class Point(WorldSetter):
    def __init__(self, x, y):
        super(Point, self).__init__(games.load_image("sprites/point.png"), x, y)

class Block(WorldSetter):
    def __init__(self, x, y):
        super(Block, self).__init__(games.load_image("sprites/block.png", transparent=False), x, y)

class Entity(games.Animation):
    # UP RIGHT DOWN LEFT
    def get_map_point(self, x, y):
        return BLOCK_MAP[y * MAP_WIDTH + x]

    # for redef
    def get_key_by_num(self, number):
        return (games.K_w, games.K_d, games.K_s, games.K_a)[number]
    def check_key(self, number):
        return games.keyboard.is_pressed(self.get_key_by_num(number))

    def __init__(self, game, imgs, x, y, speed = 1, angg = 90):
        super(Entity, self).__init__(imgs, x = cor(x), y = cor(y),
                                     n_repeats = 0, repeat_interval = 5)
        self.speed = speed
        self.angg = angg
        self.game = game
        games.screen.add(self)

    def update(self):
        # moving
        MOVES = {
            0:(0, -self.speed, -self.angg),
            1:(self.speed, 0, 0),
            2:(0, self.speed, self.angg),
            3:(-self.speed, 0, 2 * self.angg)}
        AVAIBLE = {
            0:(0, -1),
            1:(1, 0),
            2:(0, 1),
            3:(-1, 0)}
        CURRENT = {
            0:(0, -self.speed),
            1:(self.speed, 0),
            2:(0, self.speed),
            3:(-self.speed, 0)}
        cm = (pos(self.x), pos(self.y))
        for key in MOVES:
            tx, ty = AVAIBLE[key]
            if self.check_key(key) and (self.y + self.x) % CELL_SIZE == 0:
                self.dx, self.dy, self.angle = MOVES[key]
            if (self.y + self.x) % CELL_SIZE == 0 and self.get_map_point(cm[0] + tx, cm[1] + ty) == "#" and (self.dx, self.dy) == CURRENT[key]:
                self.dx = 0
                self.dy = 0


class Ghost(Entity):

    def check_key(self, number):
        return number == self.moving
    def __init__(self, game):
        super(Ghost, self).__init__(game, ["sprites/ghost.png"],
                                     8, 8, 4, 0)
        self.moving = 0
    def update(self):
        # UP RIGHT DOWN LEFT
        pacman = self.game.get_pacman_coord()
        ghost = self.game.get_ghost_coord()

        # x:y
        try:
            new_ghost = finder.Graph.nums(self.game.gramap.find_from_to(str(ghost[0]) + ":" + str(ghost[1]), str(pacman[0]) + ":" + str(pacman[1]))[-2])
            if ghost[1] > new_ghost[1]:
                self.moving = 0
            elif ghost[0] < new_ghost[0]:
                self.moving = 1
            elif ghost[1] < new_ghost[1]:
                self.moving = 2
            else:
                self.moving = 3
        except:
            pass
        finally:
            super(Ghost, self).update()


class Pacman(Entity):
    def __init__(self, game):
        super(Pacman, self).__init__(game, ["sprites/pacman_1.png", "sprites/pacman_2.png", "sprites/pacman_3.png"],
                                     10, 11, 4)
        self.sounds = games.load_sound("sounds/point.wav"), games.load_sound("sounds/death.wav")
    def update(self):
        super(Pacman, self).update()
        for obj in self.overlapping_sprites:
            if type(obj) == Point:
                self.sounds[0].play()
                obj.destroy()
                self.game.add_point()
            if type(obj) == Ghost:
                games.music.stop()
                self.sounds[1].play()
                self.game.lose()
                self.destroy()

class Game(object):
    score = 0
    def __init__(self):
        games.init(screen_width=CELL_SIZE * MAP_WIDTH, 
                   screen_height=CELL_SIZE * MAP_HEIGHT, fps=30)

        self.max_points = BlockMap(BLOCK_MAP).get_max_points()
        
        self.pacman = Pacman(self)
        self.ghost = Ghost(self)

        self.score = games.Text(value = "Score: 0", size = 30, color = color.white, x = 50, y = 15)
        games.screen.add(self.score)

        self.gramap = finder.Graph(LIST_MAP, ["#"])

        games.music.load("sounds/music.mp3")
        games.music.play(-1)

        games.screen.mainloop()

    def get_pacman_coord(self):
        return pos(self.pacman.x), pos(self.pacman.y)

    def get_ghost_coord(self):
        return pos(self.ghost.x), pos(self.ghost.y)


    def add_point(self):
        Game.score += 1
        self.score.value = "Score: " + str(Game.score)
        if Game.score == self.max_points:
            self.win()
    
    def win(self):
        games.screen.add(games.Message(size = 72, value = "You win", x = games.screen.width / 2, y = games.screen.height / 2, color = color.green,
                      lifetime = 150, after_death = games.screen.quit))
        self.ghost.destroy()

    def lose(self):
        games.screen.add(games.Message(size = 72, value = "You lose", x = games.screen.width / 2, y = games.screen.height / 2, color = color.red,
                      lifetime = 150, after_death = games.screen.quit))

if __name__ == "__main__":
    Game()
