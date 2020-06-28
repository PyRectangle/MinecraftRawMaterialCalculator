# MinecraftRawMaterialCalculator
An application, that lets you calculate the raw materials needed for a build from a litematica material list.
## Installation
### Install Requirements
- A minecraft install that has at least one non-modded version installed that needs to be 1.14 or higher
- A working internet connection
### Install instructions
1. Install python 3.6 or newer from [python.org](https://www.python.org) or using your package manager.  
2. Download or clone this repository.
3. Install the dependencies: `pip install -r requirements.txt` (Only do this if you plan on using the gui. The command line version doesn't need these dependencies)
4. Run the `import.py` script with your minecraft path as parameter. (`python import.py <pathToYour.minecraftFolder>`) It will ask you from what version it should import the assets. It should work with 1.14 and higher. But I mostly tested with 1.15.2, so you might encounter some bugs.
5. Try using it.
## Usage (Gui)
To launch into the gui you just need to execute the `main.py` file without any arguments. The rest should be obvious.
## Usage (Command line)
```
Usage:
main.py <command> <file> <options>
Commands:
    help  show this help
    calc  calculate the raw materials needed
    show  show the specified material list
Options:
    -h --help  show this help
    -g --gui   use the gui to display dialogs
Supported filetypes:
    litematica material lists (txt format)
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
$ python main.py calc materiallist.txt
How do you make Redstone Dust?
0 Blast Furnace: Redstone Ore: 1 
1 Crafting Table: Block of Redstone: 1 
2 Furnace: Redstone Ore: 1 
The Number:1
What planks do you use?
0 Birch Planks
1 Acacia Planks
2 Jungle Planks
3 Oak Planks
4 Spruce Planks
5 Dark Oak Planks
The Number:0
How do you make Iron Ingot?
0 Crafting Table: Block of Iron: 1 
1 Blast Furnace: Iron Ore: 1 
2 Furnace: Iron Ore: 1 
3 Crafting Table: Iron Nugget: 9 
The Number:0

Material list:
Redstone Dust: 15 / Block of Redstone: 2
Cobblestone: 60
Birch Log: 12
Iron Ingot: 15 / Block of Iron: 2
```
As you can see it asks a few questions because most things in the game can be crafted, smelted, ... in different ways.
Also it rounds up to full blocks as you can see with the iron and redstone.
