# GBAFE-WeaponRelation-Randomizer
made for randomizing the weapon triangle used in the GBA Fire Emblem Games

## What this does
This program allows you to randomize the relationship between the weapon types in GBAFE.

You can randomize the bonus accuracy and damage given in a weapon relation

## Radnomizer Modes
  ### Triangle
  this tries to mimic the vanilla experience
  it creates sets of 3 weapon types where each has an advantage against one of the other types, and a disadvantage against the remaining one

  ### Circular
  creates a circular relationship where every weapon has an advantage against in the next one in the sequence and a disadvantage against the previous
  
  ### Pair
  this mode generates random relationship pairs. If A is set to have an advantage against B, then B will be set to have an equal disadvantage against A
  
  ### Chaos
  this mode generates random one sided relationships. it could lead to interesting situations like a weapon having the advantage against itself or having a disadvantage to almost every other type in the pool

## Weapons Pool
  this holds all of the attacking weapon types in the game (Staff,Ring,Item,etc. types are excluded for obvious reasons)
  you can remove a weapon type from the pool by clicking on it and then clicking remove
  if you want to add another weapon type to the pool, click the entry box below the remove button and type it in then click the Add button

Once you have finished with all the settings, click the Randomize button at the bottom to produce the randomizer event file
move or copy [WeaponRelationDefs.event](https://github.com/Teraspark/GBAFE-WeaponRelation-Randomizer/blob/main/WeaponRelationDefs.event) to the same directory and then run the randomizer event file with EA or FE_Builder_GBA to assemble it into the rom.
