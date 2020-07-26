# MinecraftRawMaterialCalculator
An application, that lets you calculate the raw materials needed for a build from a litematica material list.
## Installation
### Install Requirements
- A minecraft install that has at least one non-modded version installed that needs to be 1.14 or higher
- A working internet connection
### Install instructions (Binary)
Go to the release section of this repository and download the right binary for your platform. If your platform is not there, you can still run this program by running from source.
### Install instructions (Source)
1. Install python 3.6 or newer from [python.org](https://www.python.org) or using your package manager.  
2. Download or clone this repository.
3. Install the dependencies: `pip install -r requirements.txt` (Only do this if you plan on using the gui. The command line version doesn't need these dependencies)
4. Start it for the first time. It will greet you with an import dialog. Impot your assets from 1.14 or higher.
5. Try using it.
## Usage (Gui)
To launch into the gui you just need to execute the `main.py` file (or the desktop shortcut or the appimage depending on your installation) without any arguments. The rest should be obvious.
## Usage (Command line)
Depending on your installation you will have to execute a different command to start the program. If you ran the installer for windows you will be able to run `mrmc help` in the cmd to get this message. If you downloaded the appimage you will have to run the appimage from terminal with the right arguments, otherwise you can just run `main.py` with some arguments.
```
Usage:
main.py <command> <file> <options>
Commands:
    help    show this help
    calc    calculate the raw materials needed
    show    show the specified material list
    import  import new assets
Options:
    -h --help                  show this help
    -g --gui                   use the gui to display dialogs
    -m --multiplier  <number>  multiply the material counts with this multiplier
Supported filetypes:
    litematica material lists (txt format)
    litematica material lists (csv format)
```
### Config
The main config file is always called `config.json` and consists of the following variables:  
`theme`: The theme the gui will use (You probably want to change this with the gui not by editing the file)  
`config`: The config file that will be used to calculate the raw materials  
`minecraft`: Path to your `.minecraft` folder (The import script should have set this already)  
The config file for your calculations looks like this:  
`Ignore`: A list of items that will be ignored from the material list. Useful if you're building with resource blocks.  
`StopAt`: A list of items the program should stop at. For example if you have a lot of sticks you don't want the program to count them as planks because you already have them.  
`lang`: The language code your game is in. That is required, because litematica converts the block ids to the actual names and this program uses it to ask questions about how you want to craft things.  
## Example (Command line)
So for example a material list generated using litematica usually looks like this:
```
+-------------------+-------+---------+-----------+
| Area Analysis for selection 'myselection'       |
+-------------------+-------+---------+-----------+
| Item              | Total | Missing | Available |
+-------------------+-------+---------+-----------+
| Piston            |    15 |       0 |         0 |
+-------------------+-------+---------+-----------+
| Item              | Total | Missing | Available |
+-------------------+-------+---------+-----------+
```
You can use this tool on it:
```
$ python main.py calc /path/to/my/material/list.txt
How do you make Redstone Dust?
0 Blast Furnace: 1x Redstone Ore = 1x Redstone Dust
1 Crafting Table: 1x Block of Redstone = 9x Redstone Dust
2 Furnace: 1x Redstone Ore = 1x Redstone Dust
The number:1
What planks do you use?
0 Oak Planks
1 Spruce Planks
2 Birch Planks
3 Jungle Planks
4 Acacia Planks
5 Dark Oak Planks
6 Crimson Planks
7 Warped Planks
The number:0
What Oak Log do you use?
0 Oak Log
1 Oak Wood
2 Stripped Oak Log
3 Stripped Oak Wood
The number:0
How do you make Iron Ingot?
0 Crafting Table: 1x Block of Iron = 9x Iron Ingot
1 Blast Furnace: 1x Iron Ore = 1x Iron Ingot
2 Furnace: 1x Iron Ore = 1x Iron Ingot
3 Crafting Table: 9x Iron Nugget = 1x Iron Ingot
The number:0

Materials:
Redstone Dust: 15 / Block of Redstone: 2
Cobblestone: 60
Oak Log: 12
Iron Ingot: 15 / Block of Iron: 2

```
As you can see it asks a few questions because most things in the game can be crafted, smelted, ... in different ways.
Also it rounds up to full blocks as you can see with the iron and redstone.
