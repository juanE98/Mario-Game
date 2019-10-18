"""Class for representing a Player entity within the game."""

__version__ = "1.1.0"

from game.entity import DynamicEntity
import time


class Player(DynamicEntity):
    """A player in the game"""
    _type = 3

    def __init__(self, name: str = "Mario", max_health: float = 20):
        """Construct a new instance of the player.

        Parameters:
            name (str): The player's name
            max_health (float): The player's maximum & starting health
        """
        super().__init__(max_health=max_health)
        

        self._name = name
        self._score = 0
        self._invinc = False 
        self._star_collected_time = time.time()
        self._switch_time = time.time()
        self._on_tunnel = False 
        self._on_flag = False 
        self._proceed = False 
        self._next_level = None
        self._switch_status = True 
        self._brick_list = []   
        self._brick_pos_x= [] 
        self._brick_pos_y = []
        self._mass = int(300)
        self._max_velocity = 100

    def set_mass(self, mass): 
        ''' sets the mass of the player.
        Parameters: 
                (float): Mass of player. 
        ''' 
        self._mass = mass 

    def get_mass(self): 
        ''' get mass of player. ''' 
        return self._mass

    def get_name(self) -> str:
        """(str): Returns the name of the player."""
        return self._name

    def set_name(self, name): 
        ''' sets name of player.
        Parameters: 
            (str): Name of player 
        '''
        self._name = name 

    def get_score(self) -> int:
        """(int): Get the players current score."""
        return self._score

    def change_score(self, change: float = 1):
        """Increase the players score by the given change value."""
        self._score += change

    def get_invinc(self):
        ''' gets player invincibility status ''' 
        return self._invinc

    def set_invinc(self, change: bool): 
        ''' change the player's invincibility status ''' 
        self._invinc = change

    def star_power(self): 
        ''' sets the time when a star is collected.''' 
        self._star_collected_time = time.time()

    def get_star_time(self): 
        ''' (time<float>): gets the time when player collected the star. ''' 
        return self._star_collected_time

    def on_tunnel(self): 
        '''(bool): returns player tunnel status. '''
        return self._on_tunnel 

    def set_on_tunnel(self, change: bool): 
        '''sets if player is on tunnel'''
        self._on_tunnel = change
    
    def on_flag(self): 
        '''(bool): returns if player is on top of flag. '''
        return self._on_flag 

    def set_on_flag(self,change:bool): 
        ''' set True if player is on top of flag. '''
        self._on_flag = change

    def get_proceed(self): 
        ''' (bool): gets whether or not player can proceed to next level status ''' 
        return self._proceed 
    
    def set_proceed(self, change: bool): 
        ''' set True if player is allowed to proceed to next level. ''' 
        self._proceed = change 

    def next_level(self, next_level): 
        ''' (str) Sets next level of player ''' 
        self._next_level = next_level

    def get_next_level(self): 
        ''' (str) Gets next level of player ''' 
        return self._next_level

    def switch_pressed_time(self): 
        '''Sets the time when switch is pressed. ''' 
        self._switch_time = time.time()

    def get_switch_time(self):
        ''' (time <float>): Gets the time when switch is pressed ''' 
        return self._switch_time

    def switch_status(self):
        ''' (bool): gets the status of the Switch being pressed or not. '''
        return self._switch_status
    
    def set_switch_status(self, change: bool): 
        ''' sets to False if switch is being pressed. '''
        self._switch_status = change

    def set_brick_pos_x (self, brick_posx): 
        ''' (list<tuple>): sets the x coordinates of the bricks removed. ''' 
        self._brick_pos_x.append(brick_posx) 

    def set_brick_pos_y (self, brick_posy): 
        ''' (list<tuple>): sets the y coordinates of the bricks removed. ''' 
        self._brick_pos_y.append(brick_posy) 

    def get_brick_pos_x(self): 
        ''' returns (list<tuple>) of x coordinates of the bricks removed. '''
        return self._brick_pos_x

    def get_brick_pos_y(self): 
        ''' returns (list<tuple>) of  y coordinates of the bricks removed. '''
        return self._brick_pos_y

    def __repr__(self):
        return f"Player({self._name!r})"
