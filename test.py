import json
import string
import numpy

loc = input("Enter the location of the file to read from: ")
template = {} 

with open(loc, 'r') as f:
    data = json.load(f)

# To return
items = []
quantities = []
chances = []

if 'entries' in data.keys():
    # Loot table in gen/
    loot = data['entries'][0]

    # Calculate average number of pools for this loot table, to be multiplied in at the end (or not)
    rolls = [loot['roll']['min'], loot['roll']['min']]
    roll_count = numpy.average(rolls)

    pool_list = loot['pool']
    total_weight = 0
    for weight_counter in pool_list:
        # Count up total weight for all pools in the table
        total_weight += weight_counter['weight']
    for pool_data in pool_list:
        pool_weight = pool_data['weight']

        pool_entries = []
        
        pool_total_weight = 0
        for pool_weight_counter in pool_data['pool']:
            pool_total_weight += pool_weight_counter['weight']
        
        for pool in pool_data['pool']:
            item = pool['item']
            weight = pool['weight']
            quant = str(item['count']['min']) + " - " + str(item['count']['max'])

            items.append(item['id'])
            quantities.append(quant)
            chances.append(str(round(((float(weight) / float(pool_total_weight)) * (float(pool_weight) / float(total_weight))) * 100, 2)) + "%")

    print(items)
    print(quantities)
    print(chances)

# print(data)