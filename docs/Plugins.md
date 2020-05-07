# Plugins (WIP)
[Back Home](index.md)

## Using A Plugin
### Installation
All that should be required to install a plugin is dragging
the plugin folder into the plugins folder.

Depending on the plugin it may require you to write some configs,
which should be listed in the plugins docs. This should also list any
requirements they have used other than the ones are used in the base program.

Unless the plugin has been made by the author of this project,
take note that they are not controlled by the author and so may contain harmful
scripts, or may not be compatible with certain versions of the Home Terminal System.

## Making A Plugin
### Structure Of Plugins
- plugins/
    - `__init__.py` empty file that allows plugin folders to be imported
    - plugin-name
        - `__init__.py` with blueprint variable and PluginData class
        - `view.py`
        - templates/
        - models/ (if extra tables are required)

### Prefered Plugin Formats
- PluginData in `__init__.py` **must** have has_models that equals either True or False
- if plugin has api,  preference it with /api
- write your plugins view in a `view.py` file and import blueprint in `__init__.py`
- use the base.html template and site styles to keep it consistent for the user

Take to look at the example plugin
[here](https://github.com/enchant97/HTS-example-plugin) if you want a starting point.
