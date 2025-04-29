import os


class ContentLoadingPlugin:
    """Represents a plugin for loading content."""

    def __init__(self, file: str):
        """Creates a new instance of this class."""
        self.File = file
        self.Title = os.path.basename(file)
        self.Texture = None
        self.Sound = None
        self.Object = None
        self.Route = None
        self.Train = None

    def Load(self, Host, FileSystem, Options, TrainManagerReference=None, RendererReference=None):
        """Loads all interfaces this plugin supports."""
        #미구현
        '''
        if self.Texture is not None:
            self.Texture.Load(Host)  # anything built against original API; nautilus basically, crummy code....
            self.Texture.Load(Host, FileSystem, Options)

        if self.Sound is not None:
            self.Sound.Load(Host)
        '''
        if self.Object is not None:
            self.Object.Load(Host, FileSystem)
        '''
            self.Object.SetObjectParser(Options.CurrentXParser)
            self.Object.SetObjectParser(Options.CurrentObjParser)
        '''
        '''
        if self.Route is not None:
            self.Route.Load(Host, FileSystem, Options, TrainManagerReference)

        if self.Train is not None:
            self.Train.Load(Host, FileSystem, Options, RendererReference)
        '''
    def Unload(self):
        """Unloads all interfaces this plugin supports."""

        if self.Texture is not None:
            self.Texture.Unload()

        if self.Sound is not None:
            self.Sound.Unload()

        if self.Object is not None:
            self.Object.Unload()

        if self.Route is not None:
            self.Route.Unload()
