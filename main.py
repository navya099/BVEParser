from Plugins.RouteCsvRw.Plugin import Plugin
from RouteManager2.CurrentRoute import CurrentRoute

def main():
    path = 'D:/BVE/루트/Railway/Route/연습용루트/신분당선연장.csv'
    plugin = Plugin()
    plugin.LoadRoute(
        path,'utf-8',None,None,None,True,plugin)
    
if __name__ == "__main__":
    main()
    
