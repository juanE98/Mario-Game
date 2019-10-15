"""
Simple 2d world where the player can interact with the items in the world.
"""

__author__ = "Juan Espares: 44317962" 
__date__ = "3/10/2019" 
__version__ = "1.1.0"
__copyright__ = "The University of Queensland, 2019"

import math
import tkinter as tk


from typing import Tuple, List
from tkinter import messagebox , filedialog


import pymunk

from game.block import Block, MysteryBlock
from game.entity import Entity, BoundaryWall
from game.mob import Mob, CloudMob, Fireball
from game.item import DroppedItem, Coin
from game.view import GameView, ViewRenderer
from game.world import World


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
    '^': 'cube'
}

ITEMS = {
    'C': 'coin'
}

MOBS = {
    '&': "cloud"
}
  
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
    "cube": "cube"
}

ITEM_IMAGES = {
    "coin": "coin_item"
}

MOB_IMAGES = {
    "cloud": "floaty",
    "fireball": "fireball_down"
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

        self._player = Player(max_health=5)
        self.reset_world('level1.txt')

        self._renderer = MarioViewRenderer(BLOCK_IMAGES, ITEM_IMAGES, MOB_IMAGES)

        size = tuple(map(min, zip(MAX_WINDOW_SIZE, self._world.get_pixel_size())))
        self._view = GameView(master, size, self._renderer)
        self._view.pack()
        self.bind()
        

        
    
        #Call Health and Score Status 
        self._statusDisplay = StatusDisplay(master, size)
        self._statusDisplay.pack(fill = tk.X )

        #Retrieve player health and score and pass it to StatusDisplay class. 
        
        
        
        
        
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
        filemenu.add_command(label = 'Load Level', command = self.load_file)
        filemenu.add_command(label = 'Reset Level', command = self.reset_level)
        filemenu.add_command(label = 'Exit', command = self.quit)

        #Restart or exit game level if player has no health left. 
        
            
        
    def popup_end(self): 
        ''' popup function that gives user the option to restart or quit game upon death. 
        (i.e. Score = 0 )

        ''' 
        popup = tk.Tk() 

        def leavepop(): 
            popup.destroy() 
            self.reset_world('level1.txt')

        popup.wm_title (' Game Over !')
        label1 = tk.Label(popup, text = 'Restart or Quit ?')
        label1.pack()
        b1 = tk.Button(popup, text = 'Restart' , command = leavepop)
        b2 = tk.Button(popup, text = 'Quit' , command = self.quit)
        b1.pack() 
        b2.pack() 
        popup.mainloop() 

    def load_file(self): 
        ''' loads file requested ''' 
        filename = filedialog.askopenfilename() 
        try: 
            self.reset_world(filename)

        except FileNotFoundError: 
            print(' File not found ')
        
       
    def reset_level(self): 
        ''' resets game to level 1 ''' 
       
        self._player.change_score(-(self._player.get_score()))
        maxhealth = self._player.get_max_health() 
        self._player.change_health(maxhealth)
        self.reset_world('level1.txt')

    def quit(self): 
        ''' Option to quit the game and terminate program.  ''' 
        confirm = messagebox.askokcancel('Quit', 'Are you sure you want to quit?')
        if confirm: 
            self._master.destroy() 

    

    def reset_world(self, new_level):
        self._world = load_world(self._builder, new_level)
        self._world.add_player(self._player, BLOCK_SIZE, BLOCK_SIZE)
        self._builder.clear()

        self._setup_collision_handlers()

    def bind(self):
        """Bind all the keyboard events to their event handlers."""
        #Jumping 
        self._master.bind('<w>', lambda e: self._jump())
        self._master.bind('<Up>', lambda e: self._jump())
        self._master.bind('<space>', lambda e: self._jump())  
        
        #Left and Right 
        self._master.bind('<a>', lambda e: self._move(-80, 0))
        self._master.bind('<Left>', lambda e: self._move(-80, 0) )  
        
        self._master.bind('<d>', lambda e: self._move(80, 0))
        self._master.bind('<Right>', lambda e: self._move(80, 0))

        #Duck 
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
        data = (self._world, self._player)
        self._world.step(data)
        
        plyr_health = self._player.get_health()
        plyr_score = self._player.get_score() 
        max_health = self._player.get_max_health() 
        score_update = StatusDisplay.set_score(self._player, plyr_score)
        health_update = StatusDisplay.set_health(self._player, plyr_health)
        
        self._statusDisplay.update_bar(health_update, score_update, max_health)

        if plyr_health < 1 : 
            self.popup_end()

        self.scroll()
        self.redraw()

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
             
    def _duck(self):   #Need to fix when pipes are implemented.  
        ''' Makes player crouch.
        '''  
        velocity_current = self._player.get_velocity()
        velocity_current_list = list(velocity_current) 
        velocity_current_list[1] += 160
        velocity_current = tuple(velocity_current_list)
        self._player.set_velocity(velocity_current)
        self._player.set_jumping(False)

        

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
        return True

    def _handle_mob_collide_item(self, mob: Mob, block: Block, data,
                                 arbiter: pymunk.Arbiter) -> bool:
        return False

    def _handle_mob_collide_mob(self, mob1: Mob, mob2: Mob, data,
                                arbiter: pymunk.Arbiter) -> bool:
        if mob1.get_id() == "fireball" or mob2.get_id() == "fireball":
            self._world.remove_mob(mob1)
            self._world.remove_mob(mob2)

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

        block.on_hit(arbiter, (self._world, player))
        return True

    def _handle_player_collide_mob(self, player: Player, mob: Mob, data,
                                   arbiter: pymunk.Arbiter) -> bool:
        mob.on_hit(arbiter, (self._world, player))
        return True

    def _handle_player_separate_block(self, player: Player, block: Block, data,
                                      arbiter: pymunk.Arbiter) -> bool:
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
        health = self._health  
        return self._health
        
    def set_score(self,score):
        score = self._score 
        return self._score 


    def update_bar(self, health , score , max_health):    
        health_percentage = (health / max_health)
        new_width = ( health_percentage * int(self.winfo_width()))

        if health_percentage >0.5: 
            self._healthbar.config(bg ='green', width =int(new_width)  )
                  
        elif health_percentage > 0.25 and health_percentage <= 0.5: 
            self._healthbar.config(bg = 'orange', width = int(new_width))
            
        elif health_percentage <0.25: 
            self._healthbar.config(bg = 'red', width= int(new_width))

        self._scorelabel.config( text = 'Score: ' + str(score))




class BounceBlock(Block): 
    def __init__(self): 
        super().__init__()  



         
            

if __name__ == "__main__": 

    root = tk.Tk() 
    app = MarioApp(root)
    root.title("Mario")
    root.iconbitmap(r'favicon.ico')
    root.mainloop()  




  