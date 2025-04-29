import os
import importlib.util
from typing import Optional

from OpenBveApi.Plugins.ContentLoadingPlugin import ContentLoadingPlugin


class PluginLoader:
    def __init__(self):
        self.Plugins = []

    def LoadPlugins(self, fileSystem, currentOptions, TrainManagerReference=None, RendererReference=None):
        """Load plugins from the 'Plugins' directory and handle loading errors."""
        errorMessage = ""

        if self.Plugins:
            # Plugins already loaded
            return True, errorMessage

        folder = fileSystem.GetDataFolder("Plugins")
        files = []
        try:
            files = os.listdir(folder)
        except Exception as ex:
            pass  # ignored

        plugin_list = []
        builder = []

        for file in files:
            if file.lower().endswith(".dll"):
                try:
                    plugin = ContentLoadingPlugin(file)
                    try:
                        # Dynamically loading the plugin file (if it's a .dll assembly)
                        spec = importlib.util.spec_from_file_location(file, os.path.join(folder, file))
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        types = [getattr(module, name) for name in dir(module) if
                                 isinstance(getattr(module, name), type1)]

                        iruntime = False
                        for type1 in types:
                            '''
                            if issubclass(type, TextureInterface):
                                plugin.Texture = type()
                            if issubclass(type, SoundInterface):
                                plugin.Sound = type()
                            '''
                            from OpenBveApi.Objects.ObjectInterface import ObjectInterface
                            if issubclass(type1, ObjectInterface):
                                plugin.Object = type1()
                            from OpenBveApi.Routes.RouteInterface import RouteInterface
                            if issubclass(type1, RouteInterface):
                                plugin.Route = type1()
                            '''
                            if issubclass(type, TrainInterface):
                                plugin.Train = type()
                            if issubclass(type, Runtime.IRuntime):
                                iruntime = True
                            '''
                        if any([plugin.Texture, plugin.Sound, plugin.Object, plugin.Route, plugin.Train]):
                            plugin.Load(self, fileSystem, currentOptions, TrainManagerReference, RendererReference)
                            plugin_list.append(plugin)
                        elif not iruntime:
                            builder.append(f"Plugin {file} does not implement compatible interfaces.\n")
                    except Exception as ex:
                        builder.append(f"Could not load plugin {file}: {ex}\n")
                except Exception as ex:
                    builder.append(f"Plugin {file} failed to load: {str(ex)}\n")

        self.Plugins = plugin_list

        if not self.Plugins:
            errorMessage = "No available content loading plugins were found.\nPlease re-download OpenBVE."
            return False, errorMessage

        if builder:
            errorMessage = "\n".join(builder).strip()

        return True, errorMessage

    def AddMessage(self, message_type, flag, message):
        """Method to handle adding messages (e.g., logging or showing them)."""
        # Placeholder for message handling logic
        print(message)
