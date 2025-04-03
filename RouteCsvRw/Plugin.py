class Plugin:
    def __init__(self):
        pass
    def LoadRoute(path: str,Encoding,PreviewOnly: bool,route) -> bool:
        if Encoding == None:

            Encoding = 'utf-8'

        LastException = None
        Cancel = False
        CurrentProgress = 0.0
        IsLoading = True
        print(f"Loading route file: {path}")
        print(f"INFO: Route file hash  + path")
        if isinstance(route, CurrentRoute):
            current_route = route
	#First, check the format of the route file
	#RW routes were written for BVE1 / 2, and have a different command syntax
        is_rw = path.lower().endswith(".rw")
        print(f"Route file format is: {'RW' if is_rw else 'CSV'}\n")
        try:
            parser = Parser()
            parser.ParseRoute(path, isRw, Encoding, trainPath, objectPath, soundPath, PreviewOnly, this);
            IsLoading = false;
            return true;

        except Exception as ex:
            route = None
            CurrentHost.AddMessage(MessageType.Error, false, "An unexpected error occured whilst attempting to load the following routefile: " + path);
            IsLoading = false;
            LastException = ex;
            return false;
