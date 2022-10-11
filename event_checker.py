import pygame
pygame.init()
            
class EventChecker:
    """A class that checks events, which can be bound to pygame keystates"""
    
    __slots__ = ['aliases', 'states']

    def __init__(self, events: dict[str: set[int]]): 
        # events stored in form {'alias' : set[keys]}
        #   NOTE: pygame keys & events are just ints
        self.aliases = {'quit': {pygame.QUIT}} | events #merge dict passed in with default using binary OR

        # the actual states of an alias
        #   {alias : state}
        self.states = {key: False for key in self.aliases}

    def register_event(self, alias: str, events: set[int]) -> None: 
        "Add/replace a keystate corresponding to an alias"

        self.aliases[alias] = events
        self.states[alias] = False

    def remove_event(self, alias: str) -> None:
        "Remove an alias and its corresponding keystate"

        del self.aliases[alias]
        del self.states[alias]

    def check_key_press(self) -> None:
        "Must be called each frame, updates internal state of EventChecker"

        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                self.states['quit'] = True

            if (event.type == pygame.KEYDOWN):
                
                for alias in self.aliases:
                    if (event.key in self.aliases[alias]):
                        self.states[alias] = True
                        break

            elif (event.type == pygame.KEYUP):

                for alias in self.aliases:
                    if (event.key in self.aliases[alias]):
                        self.states[alias] = False
                        break

    def get_state(self, alias: str) -> bool:
        "Convenience method to look up keystate given an alias"

        return self.states[alias]
