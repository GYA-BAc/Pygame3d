import pygame
pygame.init()

class EventChecker:
    """A class that checks events, which can be bound to pygame keystates"""
    
    __slots__ = ['aliases', 'states']

    def __init__(self, events: dict): 
        #events stored in form {'alias' : keybinding}
        self.aliases = {'quit': pygame.QUIT} | events #merge dict passed in with default using binary OR

        #the actual states of keybindings in aliases
        #   {keybinding : state}
        self.states = {self.aliases[key]: False for key in self.aliases}

        #calling this function limits the keys pygame keeps track of
        pygame.event.set_allowed([key for key in self.states])

    def register_event(self, alias: str, event: pygame.event) -> None: 
        "Add/replace a keystate corresponding to an alias"

        self.aliases[alias] = event
        self.states[event] = False

        pygame.event.set_allowed([key for key in self.states])

    def remove_event(self, alias: str) -> None:
        "Remove an alias and its corresponding keystate"

        del self.states[self.aliases[alias]]
        del self.aliases[alias]

        pygame.event.set_allowed([key for key in self.states])


    def check_key_press(self) -> None:
        "Must be called each frame, updates internal state of EventChecker"

        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                self.states[pygame.QUIT] = True

            if (event.type == pygame.KEYDOWN):

                if (event.key in self.states):
                    self.states[event.key] = True

            elif (event.type == pygame.KEYUP):

                if (event.key in self.states):
                    self.states[event.key] = False

    def get_state(self, alias: str) -> bool:
        "Convenience method to look up keystate given an alias"

        return self.states[self.aliases[alias]]
            
