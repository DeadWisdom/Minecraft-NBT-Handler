import nbt
filename = "World3/level.dat"

root = nbt.load(filename)

def item(id, count, slot=0):
    return nbt.Tree(name=None, value=[
        nbt.Short(name='id', value=id),
        nbt.Short(name='Damage', value=0),
        nbt.Byte(name='Count', value=count % 127),
        nbt.Byte(name='Slot', value=slot),
    ])

def lots(id):
    return item(id, 64)

data = root['Data']
player = data['Player']
inventory = player['Inventory']

inventory.content_type = 10

# General
general = [
    lots(278),      # Pickax
    lots(277),      # Shovel
    lots(1),
    lots(1),
    lots(261),      # Bow
    item(50, 250),  # Torches
    None,
    None,
    item(345, 1),   # Compass

    lots(1),        # Stone
    lots(1),
    lots(1),
    lots(1),
    lots(46),       # TNT
    lots(46),
    lots(46),
    lots(65),       # Ladder
    lots(328),      # Cart

    lots(331),      # Redstone
    lots(331),      # Redstone
    lots(17),
    lots(17),
    lots(280),      # Poles
    lots(66),       
    lots(20),       # Glass
    lots(20),
    lots(330),       # Obsidian

    item(259, 1),   # Flint/Steel
    lots(53),       # Stairs
    lots(10),       # Water
    lots(8),        # Lava
    lots(266),      # Gold
    lots(69),       # switch
    item(262, 250), # Arrow
    item(262, 250),
    item(50, 250),  # Torches
]

tracking = [
    lots(278),      # Pickax
    lots(277),      # Shovel
    lots(1),
    lots(66),
    lots(261),      # Bow
    None,
    None,
    item(259, 1),   # Flint/Steel
    lots(328),      # Cart

    lots(66),       # Track
    lots(66),
    lots(76),       # Redstone Torches
    lots(66),
    lots(66),
    lots(17),       # Wood
    None,
    None,
    None,

    lots(1),        # Stone
    lots(1),
    None, 
    None,
    lots(69),       # switch
    lots(331),      # Redstone
    None, 
    item(75, 250),
    lots(8),       # Water

    item(50, 250),  # Torches
    item(262, 250), # Arrow
]

circuitry = [
    lots(1),        # Stone
    lots(277),      # Shovel
    lots(278),      # Pickax
    lots(76),       # Redstone Torches
    lots(331),      # Redstone
    None,
    None,
    None,

    lots(276),      # Sword
    lots(1),
    lots(1),
    lots(1),
    lots(46),       # TNT
    lots(46),       # TNT
    lots(46),       # TNT
    lots(46),       # TNT
    None,

    None,
    lots(331),      # Redstone
    lots(17),       # Wood
    lots(17),
    lots(280),      # Poles
    lots(280),
    lots(279),      # Axe
    lots(76),
    lots(76),

    lots(69),       # switch
    None,
    lots(261),      # Bow
    lots(8),       # Water
    item(345, 1),   # Compass
    item(259, 1),   # Flint/Steel
    item(262, 250), # Arrow
    item(262, 250),
    item(50, 250),  # Torches
]

inventory.value = [general, tracking, circuitry][1]

for i, it in enumerate(inventory.value):
    if it is not None:
        it['Slot'].value = i

inventory.append( item(302, 99, 103) )
inventory.append( item(303, 99, 102) )
inventory.append( item(304, 99, 101) )
inventory.append( item(305, 99, 100) )

data['Time'].value = 1
player['Health'].value = 20

data['SpawnX'] = player['Pos'][0]
data['SpawnY'] = player['Pos'][1]
data['SpawnZ'] = player['Pos'][2]

nbt.save(root, filename)
print "Done."

root = nbt.load(filename)
print "Verified"