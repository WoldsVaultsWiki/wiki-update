import json
import numpy

from mwcleric import AuthCredentials
from mwcleric import TemplateModifierBase
from mwcleric import WikiggClient
from mwparserfromhell.nodes import Template

credentials = AuthCredentials()
# the following login has been changed to edit gg.wiki.gg rather than sorcererbyriver.wiki.gg
# gg.wiki.gg is our sandbox wiki that anyone may edit for any reason to test scripts
# so while you are testing your code, you can leave this as-is and view changes at gg.wiki.gg
# then change it to your wiki afterwards
site = WikiggClient('vaulthunters', credentials=credentials)
summary = 'Update Loot tables from config (bot update)'

# this file contains locations for any configs not locateed in the config/ root directory
# such as the chest loot tables
with open('config_translator.json', 'r', encoding='utf-8') as f:
    data = json.load(f)


class TemplateModifier(TemplateModifierBase):
    def update_template(self, template: Template):
        # TemplateModifier is a generic framework for modifying templates
        # It will iterate through all pages containing at least one instance
        # of the specified template in the initialization call below and then
        # update every instance of the template in question with one batched edit per page
        if self.current_page.namespace != 0:
            # don't do anything outside of the main namespace
            # for example, we don't want to modify template documentation or user sandboxes
            return
        
        key = str(template.get("id").value.get(0)).strip()

        try: 
            loc = data[key]
        except KeyError:
            loc = key + ".json"
        try:
            file = open('config/' + loc, 'r')
        except FileNotFoundError:
            file = open('config/gen/1.0/loot_tables/' + loc, 'r')
        config = json.load(file)

        # To return
        items = []
        quantities = []
        chances = []

        if 'entries' in config.keys():
            # Loot table in gen/
            loot = config['entries'][0]

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
                
                pool_total_weight = 0
                for pool_weight_counter in pool_data['pool']:
                    pool_total_weight += pool_weight_counter['weight']
                
                for pool in pool_data['pool']:
                    item = pool['item']
                    weight = pool['weight']
                    minquant = item['count']['min']
                    maxquant = item['count']['max']
                    if (minquant == maxquant):
                        quant = str(minquant)
                    else:
                        quant = str(minquant) + " - " + str(maxquant)

                    items.append(item['id'])
                    quantities.append(quant)
                    chances.append(str(round(((float(weight) / float(pool_total_weight)) * (float(pool_weight) / float(total_weight))) * 100, 2)) + "%")

        template.add('Items', ', '.join(items))
        template.add('Quantity', ', '.join(quantities))
        template.add('Chances', ', '.join(chances))
        # any changes made before returning will automatically be saved by the runner

TemplateModifier(site, 'LootTable', summary=summary).run()
