import pygame

TEXTURE_NOT_FOUND = "./assets/Missing.png"

class Atlas:
    __slots__ = ['aliases', 'textures']

    def __init__(self, default=TEXTURE_NOT_FOUND):
        # dict of texture names, mapped to their place in texture list
        self.aliases : dict[str:int] = {'':0}
        # list of actual textures; tex data stored as list indexes (int)
        self.textures: list = [pygame.surfarray.array3d(pygame.image.load(default))]

    def add_tex(self, alias, texture):
        "Adds texture, updating list of textures as needed (duplicates are overwritten)"
        if (alias in self.aliases):
            self.textures[self.aliases[alias]] = texture
        else:
            self.aliases[alias] = len(self.textures)
            self.textures.append(texture)

    def alias_lookup(self, alias):
        "Convenience method to lookup texture given alias"
        return self.textures[self.aliases[alias]]
    
    def __getitem__(self, key):
        return self.textures[key] if (isinstance(key, int)) else self.aliases[key]
    
    def __contains__(self, item):
        return item in self.aliases

# add tests
