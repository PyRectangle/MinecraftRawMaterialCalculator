# MinecraftRawMaterialCalculator
A command line tool, that lets you calculate the raw materials needed for a build from a litematica material list.
## Installation
1. Install python 3.6 or newer from [python.org](https://www.python.org) or using your package manager.  
2. Download or clone this repository.
3. Run the `import.py` script with your minecraft path as parameter. (```python import.py <pathToYour.minecraftFolder>```) It will ask you from what version it should import the language and recipe files. It should work with 1.12 and higher. But I mostly tested with 1.15.2, so you might encounter some bugs.
4. Try using it.
## Usage
`python main.py <config> <materialList>`  
The config file is a json file that defines the following variables:  
Ignore: A list of items that will be ignored from the material list. Useful if you're building with resource blocks.  
StopAt: A list of items the program should stop at. For example if you have a lot of sticks you don't want the program to count them as planks because you already have them.  
lang: The language code your game is in. That is required, because litematica converts the block ids to the actual names and this program uses it to ask questions about how you want to craft things.  
A config could look like [this](config.json).
## Example
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
$ python main.py config.json materiallist.txt
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
