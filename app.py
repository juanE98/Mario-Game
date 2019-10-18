"""
Simple 2d world where the player can interact with the items in the world.
"""

__author__ = "Juan Espares: 44317962" 
__date__ = "3/10/2019" 
__version__ = "1.1.0"
__copyright__ = "The University of Queensland, 2019"

import math
import tkinter as tk
import time


from typing import Tuple, List
from tkinter import messagebox , filedialog

import pymunk

from game.block import Block, MysteryBlock
from game.entity import Entity, BoundaryWall
from game.mob import Mob, CloudMob, Fireball
from game.item import DroppedItem, Coin
from game.view import GameView, ViewRenderer
from game.world import World
from game.util import get_collision_direction

from level import load_world, WorldBuilder , load_level
from player import Player

BLOCK_SIZE = 2 ** 4
MAX_WINDOW_SIZE = (1080, math.inf)

GOAL_SIZES = {
    "flag": (0.2, 9),
    "tunnel": (2, 2)
}

BLOCKS = {
    '#': 'brick',
    '%': 'brick_base',
    '?': 'mystery_empty',
    '$': 'mystery_coin',
    '^': 'cube', 
    'b': 'bounce_block' , 
    'I': 'flag' , 
    '=': 'tunnel' , 
    'S': 'switch'

}

ITEMS = {
    'C': 'coin' , 
    '*': 'star'
}

MOBS = {
    '&': "cloud", 
    '@': "mushroom"
}


class Switch(Block): 
    ''' A switch block that causes all bricks nearby to disappear. ''' 

    _id = 'switch'

    def __init__(self): 
        super().__init__() 
        self._active = True 

    def on_hit(self, event: pymunk.Arbiter, data):
        ''' 
         When switch is hit from the top, remove all bricks in a set radius. 

        '''
        world,player = data

        #Top of block is being hit in order to activate. 
        if get_collision_direction(player,self) != 'A': 
            return 

        if self._active:
            player.switch_pressed_time() 
            player.set_switch_status(False)
            x, y = self.get_position()

            brick_remove= world.get_things_in_range(x, y, 65)
            
            for b in brick_remove: 
                if isinstance(b, Block):
                    if b.get_id() == 'brick':
                        x , y = b.get_position()
                        player.set_brick_pos_x(x)
                        player.set_brick_pos_y(y)
                        world.remove_block(b)
                        
            self._active = False
        
    def step(self, time_delta , game_data): 
        ''' Advance switch block to next step''' 
        world, player= game_data

        if player.switch_status() == True: 
            self._active = True  
            
    def is_active(self) -> bool: 
        '''(bool) returns true if switch is not yet pressed. '''
        return self._active

def create_block(world: World, block_id: str, x: int, y: int, *args):
    """Create a new block instance and add it to the world based on the block_id.

    Parameters:
        world (World): The world where the block should be added to.
        block_id (str): The block identifier of the block to create.
        x (int): The x coordinate of the block.
        y (int): The y coordinate of the block.
    """
    block_id = BLOCKS[block_id]
    if block_id == "mystery_empty":
        block = MysteryBlock()
    elif block_id == "mystery_coin":
        block = MysteryBlock(drop="coin", drop_range=(3, 6))
    elif block_id == 'bounce_block': 
        block = BounceBlock() 

    elif block_id == "tunnel": 
        block = Tunnel(next_level = "level2.txt")

    elif block_id == "flag": 
        block = Flag(next_level = "level2.txt")

    elif block_id == 'switch': 
        block = Switch()

    else:
        block = Block(block_id)

    world.add_block(block, x * BLOCK_SIZE, y * BLOCK_SIZE)


def create_item(world: World, item_id: str, x: int, y: int, *args):
    """Create a new item instance and add it to the world based on the item_id.

    Parameters:
        world (World): The world where the item should be added to.
        item_id (str): The item identifier of the item to create.
        x (int): The x coordinate of the item.
        y (int): The y coordinate of the item.
    """
    item_id = ITEMS[item_id]
    if item_id == "coin":
        item = Coin()

    elif item_id == "star": 
        item = Star()
    else:
        item = DroppedItem(item_id)

    world.add_item(item, x * BLOCK_SIZE, y * BLOCK_SIZE)


def create_mob(world: World, mob_id: str, x: int, y: int, *args):
    """Create a new mob instance and add it to the world based on the mob_id.

    Parameters:
        world (World): The world where the mob should be added to.
        mob_id (str): The mob identifier of the mob to create.
        x (int): The x coordinate of the mob.
        y (int): The y coordinate of the mob.
    """
    mob_id = MOBS[mob_id]
    if mob_id == "cloud":
        mob = CloudMob()
    elif mob_id == "fireball":
        mob = Fireball()
    elif mob_id== "mushroom": 
        mob = Mushroom() 
    else:
        mob = Mob(mob_id, size=(1, 1))

    world.add_mob(mob, x * BLOCK_SIZE, y * BLOCK_SIZE)


def create_unknown(world: World, entity_id: str, x: int, y: int, *args):
    """Create an unknown entity."""
    world.add_thing(Entity(), x * BLOCK_SIZE, y * BLOCK_SIZE,
                    size=(BLOCK_SIZE, BLOCK_SIZE))


BLOCK_IMAGES = {
    "brick": "brick",
    "brick_base": "brick_base",
    "cube": "cube" , 
    "bounce_block" : "bounce_block" , 
    "flag" : "flag" , 
    "tunnel" : "tunnel" , 
    "switch" : "switch" 
    

}

ITEM_IMAGES = {
    "coin": "coin_item" , 
    "star": "star"
}

MOB_IMAGES = {
    "cloud": "floaty",
    "fireball": "fireball_down" , 
    "mushroom": "mushroom"
    
}


class MarioViewRenderer(ViewRenderer):
    """A customised view renderer for a game of mario."""

    @ViewRenderer.draw.register(Player)
    def _draw_player(self, instance: Player, shape: pymunk.Shape,
                     view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:

        if shape.body.velocity.x >= 0:
            image = self.load_image("mario_right")
        else:
            image = self.load_image("mario_left")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="player")]

    @ViewRenderer.draw.register(MysteryBlock)
    def _draw_mystery_block(self, instance: MysteryBlock, shape: pymunk.Shape,
                            view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:
        if instance.is_active():
            image = self.load_image("coin")
        else:
            image = self.load_image("coin_used")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="block")]

    
    @ViewRenderer.draw.register(Switch)
    def _draw_switch(self, instance: Switch, shape: pymunk.Shape,
                            view: tk.Canvas, offset: Tuple[int, int]) -> List[int]:

        if instance.is_active():
            image = self.load_image("switch")
        else:
            image = self.load_image("switch_pressed")

        return [view.create_image(shape.bb.center().x + offset[0], shape.bb.center().y,
                                  image=image, tags="block")]
                

class MarioApp:
    """High-level app class for Mario, a 2d platformer"""

    _world: World

    def __init__(self, master: tk.Tk):
        """Construct a new game of a MarioApp game.

        Parameters:
            master (tk.Tk): tkinter root widget
        """
        self._master = master

        world_builder = WorldBuilder(BLOCK_SIZE, gravity=(0, 300), fallback=create_unknown)
        world_builder.register_builders(BLOCKS.keys(), create_block)
        world_builder.register_builders(ITEMS.keys(), create_item)
        world_builder.register_builders(MOBS.keys(), create_mob)
        self._builder = world_builder
        self._text = tk.Text(self._master)
        
        self._config = {}
        self._current_level = 'level1.txt'
        self._playerPosx = int(30)
        self._playerPosy = int(30)

        self._start = True 
        self._player = Player(max_health= 5)
        self.reset_world(self._current_level)
        

        self._renderer = MarioViewRenderer(BLOCK_IMAGES, ITEM_IMAGES, MOB_IMAGES)

        size = tuple(map(min, zip(MAX_WINDOW_SIZE, self._world.get_pixel_size())))
        self._view = GameView(master, size, self._renderer)
        self._view.pack()
        self.bind()

        #Call Health and Score Status 
        self._statusDisplay = StatusDisplay(master, size)
        self._statusDisplay.pack(fill = tk.X )

        #Menubar function  
        self.file_menubar() 

        # Wait for window to update before continuing
        master.update_idletasks()
        self.step()
        

    def file_menubar(self):
        ''' Creates a menubar ''' 
        menubar = tk.Menu(self._master)
        self._master.config(menu = menubar)
        filemenu = tk.Menu(menubar)
        menubar.add_cascade(label='File', menu = filemenu)
        filemenu.add_command(label = 'Load Level', command = self.load_message)
        filemenu.add_command(label = 'Reset Level', command = self.reset_level)
        filemenu.add_command(label = 'Exit', command = self.quit)
      
            
    def popup_end(self): 
        ''' 
        popup window that gives user the option to restart or quit game upon death. 
        
        ''' 

        def restart(): 
            popup.destroy()
            self.reset_level() 
            self.step() 

        def quit(): 
            popup.destroy() 
            self.quit()
            
        popup = tk.Tk() 
        popup.wm_title (' Game Over !')
        label1 = tk.Label(popup, text = 'Restart or Quit ?')
        label1.pack()
        b1 = tk.Button(popup, text = 'Restart' , command = restart) 
        b2 = tk.Button(popup, text = 'Quit' , command = quit)
        b1.pack() 
        b2.pack() 
        
        popup.mainloop() 

    def load_message(self): 
        ''' loads file that player input ''' 

        def play_level(): 
            level = entry1.get()
            p_level = level.rstrip() 
            self.reset_world(p_level)
            popup.destroy()
            
        popup = tk.Tk()
        popup.wm_title('Load Level')
        lbl1 = tk.Label(popup, text= 'Enter Filename: ') 
        entry1= tk.Entry(popup)
        b1 = tk.Button(popup, text = 'Play', command = play_level)
        lbl1.pack(anchor = tk.W)
        entry1.pack()
        b1.pack()
        popup.mainloop

       
    def reset_level(self): 
        ''' resets game to level 1 ''' 
        
        self._player.change_score(-(self._player.get_score()))
        maxhealth = self._player.get_max_health() 
        self._player.change_health(maxhealth)
        self._player.set_invinc(False)
        self.reset_world(self._current_level)

    def quit(self): 
        ''' Option to quit the game and terminate program.  ''' 
        confirm = messagebox.askokcancel('Quit', 'Are you sure you want to quit?')
        if confirm: 
            self._master.destroy() 

    def reset_world(self, new_level):
        self._world = load_world(self._builder, new_level)
        self._world.add_player(self._player, self._playerPosx, self._playerPosy) 
        self._builder.clear()
        self._master.focus_force()

        self._setup_collision_handlers()

    def bind(self):
        """Bind all the keyboard events to their event handlers."""
        self._master.bind('<w>', lambda e: self._jump())
        self._master.bind('<Up>', lambda e: self._jump())
        self._master.bind('<space>', lambda e: self._jump())  

        x_speed = self._player._max_velocity
        self._master.bind('<a>', lambda e: self._move(-(x_speed), 0))
        self._master.bind('<Left>', lambda e: self._move(-(x_speed), 0) )  
        self._master.bind('<d>', lambda e: self._move(x_speed, 0))
        self._master.bind('<Right>', lambda e: self._move(x_speed, 0))
        self._master.bind('<s>', lambda e: self._duck() )
        self._master.bind('<Down>', lambda e: self._duck() )

    def redraw(self):
        """Redraw all the entities in the game canvas."""
        self._view.delete(tk.ALL)

        self._view.draw_entities(self._world.get_all_things())

    def scroll(self):
        """Scroll the view along with the player in the center unless
        they are near the left or right boundaries
        """
        x_position = self._player.get_position()[0]
        half_screen = self._master.winfo_width() / 2
        world_size = self._world.get_pixel_size()[0] - half_screen

        # Left side
        if x_position <= half_screen:
            self._view.set_offset((0, 0))

        # Between left and right sides
        elif half_screen <= x_position <= world_size:
            self._view.set_offset((half_screen - x_position, 0))

        # Right side
        elif x_position >= world_size:
            self._view.set_offset((half_screen - world_size, 0))


    def step(self):
        """Step the world physics and redraw the canvas."""

        if self._start == True: 
            filenameuser = filedialog.askopenfilename() 
            self._config = self.read_config(filenameuser)
            gravity = self.get_info(self._config, 'World.gravity ')
            self._world.set_gravity(0,int(gravity))
            start = self.get_info(self._config,'World.start ')
            start1 = start[1:]
            self.reset_world(start1)
            
            charr = self.get_info(self._config, 'Player.character ')
            charr1 = charr[1:]
            self._player.set_name(charr1)

            x_cor = self.get_info(self._config, 'Player.x ')
            self._playerPosx = int(x_cor) 

            y_cor = self.get_info(self._config, 'Player.y ')
            self._playerPosy = int(y_cor)

            playr_mass = self.get_info(self._config, 'Player.mass ')
            self._player.set_mass(playr_mass)

            playr_health = self.get_info(self._config, 'Player.health ')
            self._player._max_health = int(playr_health)
            self._player.change_health(int(playr_health))
            
            max_x = self.get_info(self._config, 'Player.max_velocity ')
            self._player._max_velocity = max_x

            self._start = False

        data = (self._world, self._player)
        self._world.step(data)

        #Step function method passed to Star Class. 
        if self._player.get_invinc() == True:
            if (time.time() - self._player.get_star_time() > 10):
                self._player.set_invinc(False)

        #Step function method passed to Switch Class. 
        if self._player.switch_status() == False: 
            if (time.time() - self._player.get_switch_time() > 3):
                self._player.set_switch_status(True)
                xlist =self._player.get_brick_pos_x()
                ylist =self._player.get_brick_pos_y()
                for x , y in zip(xlist, ylist): 
                    self._world.add_block(Block('brick'), x, y)  

        #Set variables to be passed on to StatusDisplay class. 
        plyr_health = self._player.get_health()
        plyr_score = self._player.get_score() 
        max_health = self._player.get_max_health() 
        score_update = StatusDisplay.set_score(self._player, plyr_score)
        health_update = StatusDisplay.set_health(self._player, plyr_health)
        invinc = self._player.get_invinc() 

        #Updates the health bar and score
        self._statusDisplay.update_bar(health_update, score_update, max_health, invinc)
        
        #Flagpole next level 
        if self._player.get_proceed() == True: 
            self._player.set_proceed(False)
            self.reset_world(self._player.get_next_level())

        self.scroll()
        self.redraw()
        #If player dies, a popup appears: Exit or Restart 
        if self._player.is_dead() == True:  
            self.popup_end()

        self._master.after(10, self.step)

        
    def _move(self, dx, dy):
        '''Moves player left or right 
            Parameters: 
                dx, dy <int> : the velocity of player moving. 
        ''' 
        plyr_velocity = tuple((dx,dy))
        self._player.set_velocity(plyr_velocity)
        
       
    def _jump(self):
        ''' Makes player jump. ''' 
        jump_check = self._player.is_jumping() 
        if jump_check == False: 
            velocity_current = self._player.get_velocity()
            velocity_current_list = list(velocity_current) 
            velocity_current_list[1] -= 150
            velocity_current = tuple(velocity_current_list)
            self._player.set_velocity(velocity_current)
            self._player.set_jumping(True)
        else: 
            self._player.set_jumping(False) 
             
    def _duck(self):    
        '''  Makes player crouch.
        '''  
        velocity_current = self._player.get_velocity()
        velocity_current_list = list(velocity_current) 
        velocity_current_list[1] += 160
        velocity_current = tuple(velocity_current_list)
        self._player.set_velocity(velocity_current)
        self._player.set_jumping(False)

        #Proceeds to next level when crouching on Tunnel
        if self._player.on_tunnel() == True: 
            self.reset_world(self._player.get_next_level())



    def read_config(self, filename): 

        ''' Config parser that reads a .txt file that stores information and  can be 
        accessed by the game. 
        Parameters:
                (str<.txt>): txt file that user wishes to load. 
        Return: 
                (dictionary): nested dictionary containing game information. 

        ''' 

        config ={}
        heading = None 
        with open(filename) as fin: 
            for line in fin: 
                line = line.strip() 
                if line.startswith('==') and line.endswith('=='): 
                    heading = line[2:-2]
                    config[heading] = {}
                elif line.count(':') <= 1 and heading is not None:
                    attr, _,value = line.partition(':')
                    config[heading][attr] = value
                else: 
                    messagebox.showinfo('Error', 'Invalid config file')
                    self._master.destroy()
                    raise ValueError('Invalid config file') 


        def remove_empty(orig): 

            ''' Function that deletes null keys and values within 
            the nested dictionary. 
            Parameters:
                    (dictionary): nested dictionary generated from txt file. 

            Return: 
                    (dictionary): nested dictionary with keys and values containing '' value removed. 
                    
            '''
            clean_dict = {} 
            for a, b in orig.items():
                if isinstance(b, dict):
                    b = remove_empty(b)
                if b != '':
                    clean_dict[a]=b
            return clean_dict

        return remove_empty(config)

    def get_info(self, config,setting): 
        '''    Gets the information (value) from config file 
    Parameters: 
            (dictionary): config file parsed and readable. 
            (str): Key of config file dictionary -> {tag.key of inner dictionary} 
    Return:
            (attribute): value of inner dictionary of config 
    ''' 
        heading, attr = setting.split('.')
        return config[heading][attr]   
    
        

    def _setup_collision_handlers(self):
        self._world.add_collision_handler("player", "item", on_begin=self._handle_player_collide_item)

        self._world.add_collision_handler("player", "block", on_begin=self._handle_player_collide_block,
                                          on_separate=self._handle_player_separate_block) 

        self._world.add_collision_handler("player", "mob", on_begin=self._handle_player_collide_mob)
        self._world.add_collision_handler("mob", "block", on_begin=self._handle_mob_collide_block)
        self._world.add_collision_handler("mob", "mob", on_begin=self._handle_mob_collide_mob)
        self._world.add_collision_handler("mob", "item", on_begin=self._handle_mob_collide_item)

    def _handle_mob_collide_block(self, mob: Mob, block: Block, data,
                                  arbiter: pymunk.Arbiter) -> bool:
        if mob.get_id() == "fireball":
            if block.get_id() == "brick":
                self._world.remove_block(block)
            self._world.remove_mob(mob)
        
        elif mob.get_id() == 'mushroom':
                if get_collision_direction(mob,block) == 'L':
                    mob.set_tempo(-40)
                    
                elif get_collision_direction(mob,block) == 'R': 
                    mob.set_tempo(40)
        return True 
                    
            
    def _handle_mob_collide_item(self, mob: Mob, block: Block, data,
                                 arbiter: pymunk.Arbiter) -> bool:
        return False

    def _handle_mob_collide_mob(self, mob1: Mob, mob2: Mob, data,
                                arbiter: pymunk.Arbiter) -> bool:
        if mob1.get_id() == "fireball" or mob2.get_id() == "fireball":
            self._world.remove_mob(mob1)
            self._world.remove_mob(mob2)

        elif mob1.get_id() == "mushroom" or mob2.get_id() == 'mushroom': 
            mob1tempo = mob1.get_tempo()
            mob2tempo = mob2.get_tempo()
            mob1tempo *= -1 
            mob2tempo *= -1 
            mob1.set_tempo(mob1tempo)
            mob2.set_tempo(mob2tempo)
        return False


    def _handle_player_collide_item(self, player: Player, dropped_item: DroppedItem,
                                    data, arbiter: pymunk.Arbiter) -> bool:
        """Callback to handle collision between the player and a (dropped) item. If the player has sufficient space in
        their to pick up the item, the item will be removed from the game world.

        Parameters:
            player (Player): The player that was involved in the collision
            dropped_item (DroppedItem): The (dropped) item that the player collided with
            data (dict): data that was added with this collision handler (see data parameter in
                         World.add_collision_handler)
            arbiter (pymunk.Arbiter): Data about a collision
                                      (see http://www.pymunk.org/en/latest/pymunk.html#pymunk.Arbiter)
                                      NOTE: you probably won't need this
        Return:
             bool: False (always ignore this type of collision)
                   (more generally, collision callbacks return True iff the collision should be considered valid; i.e.
                   returning False makes the world ignore the collision)
        """

        dropped_item.collect(self._player)
        self._world.remove_item(dropped_item)
        return False

    def _handle_player_collide_block(self, player: Player, block: Block, data,
                                     arbiter: pymunk.Arbiter) -> bool:
        if self._player.switch_status() == False and block.get_id() == 'switch': 
            return False 
        else: 
            block.on_hit(arbiter, (self._world, player)  )
            return True  

    def _handle_player_collide_mob(self, player: Player, mob: Mob, data,
                                   arbiter: pymunk.Arbiter) -> bool:

        if self._player.get_invinc() == True: 
            self._world.remove_mob(mob)
            return False 

        else: 
            mob.on_hit(arbiter, (self._world, player))  
            return True 

    def _handle_player_separate_block(self, player: Player, block: Block, data,
                                      arbiter: pymunk.Arbiter) -> bool:
        if block.get_id() == 'tunnel': 
            player.set_on_tunnel(False)

        elif block.get_id() == 'flag': 
            player.set_on_flag(False)

        return True

class StatusDisplay(tk.Frame):
    ''' Initialise frame with a frame inside of it. ''' 
    def __init__(self, parent, size):
        width , height = size 
        super().__init__(parent , width = width , height= height)
        
        #Creates a black frame and packs healthbar frame on it.  
        self._blackframe = tk.Frame(self, bg= 'black', height = 20)
        self._healthbar = tk.Frame(self._blackframe, bg = 'green', height = 20)
        score = 0  
        self._scorelabel = tk.Label(self, text = 'Score: ' + str(score))
        self._blackframe.pack(fill = tk.X)

        self._healthbar.pack(side = 'left')
        self._scorelabel.pack() 

    def set_health(self,health):
        '''Health setter method
        Parameters: 
                (int): Player health 
        
        ''' 
        health = self._health  
        return self._health
        
    def set_score(self,score):
        '''Score setter method 
        Parameters: 
                (int): Player score.         
        ''' 
        score = self._score 
        return self._score 

    def update_bar(self, health , score , max_health, invinc):    
        ''' updates the colour and width of the health bar. 
        Parameters: 
                    health (int) : player's health
                    score (int): player's score 
                    max_health (int): player's health at start of game.   
                    invinc (bool): player's invincibility status       
        '''
        health_percentage = (health / max_health)
        new_width = ( health_percentage * int(self.winfo_width()))
        

        if health_percentage >0.5 and invinc == False: 
            self._healthbar.config(bg ='green', width =int(new_width)  )
                  
        elif health_percentage > 0.25 and health_percentage <= 0.5 and invinc == False: 
            self._healthbar.config(bg = 'orange', width = int(new_width))
            
        elif health_percentage <0.25 and invinc == False: 
            self._healthbar.config(bg = 'red', width= int(new_width))

        elif invinc == True: 
            self._healthbar.config(bg ='yellow')
            
        self._scorelabel.config( text = 'Score: ' + str(score))

class Mushroom(Mob): 
    ''' Mushroom is a moving entity that damages player ''' 
    _id = 'mushroom'

    def __init__(self):
        ''' Constructs a mushroom mob. ''' 
        super().__init__(self._id, size=(20,25), tempo=40)

    def on_hit(self, event, data): 
        ''' What happens to the mushroom when it collides with entity. '''
        world, player = data  

        #Player kills Mushroom if player lands on top. 
        if get_collision_direction(player,self) == 'A': 
            player.set_velocity((0,-150))
            world.remove_mob(self)

        elif get_collision_direction(player,self) == 'L': 
            player.change_health(-1)
            player.set_velocity((-80,0))

        elif get_collision_direction(player,self) == 'R':  
            player.change_health(-1)
            player.set_velocity((80,0))

        
class Star(DroppedItem): 
    ''' A star item that grants invincibility for 10 seconds. Player takes no damage 
    and kills any mob that it collides with. ''' 

    _id = 'star'

    def __init__(self): 
        super().__init__()

    def collect(self, player: Player): 
        '''Grants player special powers -> Invincibility. 
        Parameters (Player): The player who obtained the star. 
        '''  
        player.set_invinc(True)
        player.star_power()
        
    def step(self, time_delta , game_data): 
        ''' Advance star to next step''' 


class BounceBlock(Block): 
    ''' 
        A bounce block which propels the player into the air when they jump on top of the 
    block. 
    ''' 
    _id = 'bounce_block'

    def __init__(self): 
        ''' Constructs a bounce block. 
        '''
        super().__init__()  
        self._active = True

    def on_hit(self, event:pymunk.Arbiter, data): 
        ''' callback collision with player event handler.  '''
        world, player = data
        if get_collision_direction(player,self) == 'A': 
            player.set_velocity((0,-300))
            
class Tunnel(Block): 
    """ A goal that allows a player to change and progress between levels.""" 

    _id = 'tunnel' 
    _cell_size = (2,2)

    def __init__(self, next_level: str = None): 
        super().__init__()
        self._id = 'tunnel'
        self._next_level = next_level 

    def on_hit(self, event:pymunk.Arbiter, data): 
        world, player = data 

        if get_collision_direction(player, self) == 'A': 
            player.set_on_tunnel(True)
            player.next_level(self._next_level)

        else: 
            pass 
        
class Flag(Block): 
    ''' Flag that allows player to progress to next level. ''' 

    _id = 'flag'
    _cell_size = (0.2 , 9)

    def __init__(self, next_level: str = None): 
        super().__init__()
        self._id = 'flag'
        self._next_level = next_level    

    def on_hit(self, event:pymunk.Arbiter, data): 
        world, player = data 

        if get_collision_direction(player,self) == 'A': 
            
            player.change_health(3)
            player.set_on_flag(True)

        else: 
            player.next_level(self._next_level)
            player.set_proceed(True)




if __name__ == "__main__": 

    root = tk.Tk() 
    app = MarioApp(root)
    root.title("Mario")
    root.iconbitmap(r'favicon.ico')
    root.mainloop()  




  