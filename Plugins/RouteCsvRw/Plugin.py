from RouteManager2.CurrentRoute import CurrentRoute
from .CsvRwRouteParser import Parser
from OpenBveApi.Routes.RouteInterface import RouteInterface 
from OpenBveApi.System.Path import Path

class Plugin(RouteInterface):
    def __init__(self):
        super().__init__()
        self.CurrentRoute = CurrentRoute()

    def CanLoadRoute(self, path: str) -> bool:
        return path.lower().endswith((".csv", ".rw"))
    
    def LoadRoute(self, path: str, encoding: str, trainPath: str,
                  objectPath: str, soundPath: str,
                  previewOnly: bool, route: object) -> bool:
        if encoding is None:

            encoding = 'utf-8'

        self.LastException = None
        self.Cancel = False
        self.CurrentProgress = 0.0
        self.IsLoading = True
        self.CurrentRoute = route
        print(f"Loading route file: {path}")
        print(f"INFO: Route file hash {Path.get_checksum(path)}");

	#First, check the format of the route file
	#RW routes were written for BVE1 / 2, and have a different command syntax
        isrw = path.lower().endswith(".rw")
        print(f"Route file format is: {'RW' if isrw else 'CSV'}\n")
        try:
            parser = Parser()
            parser.ParseRoute(path, isrw, encoding,
                              trainPath, objectPath,soundPath,
                              previewOnly ,self)
            self.IsLoading = False
            return True

        except Exception as ex:
            route = None
            print("An unexpected error occured whilst attempting to load the following routefile: " + path)
            self.IsLoading = False
            self.LastException = ex
            print("Error loading route:", ex)
            return False
