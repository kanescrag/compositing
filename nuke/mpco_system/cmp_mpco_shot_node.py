
'''
-----------------------------------------------------------------------
cmp_mpco_shot_node
-----------------------------------------------------------------------
Description:   A custom read node for the mpco plotter with traffic light system and data returns. Part of the MPCO plotter toolset.
Authors:       Craig Kane
Email:         craig.kane@giant.ie
Affiliation:   Giant Animation
Version:       0.1 - 02/09/2024
Tested on:     Maya 2022.3
Updated by:    Craig Kane
-----------------------------------------------------------------------

Update History:
- <Date of Update>: <Description of changes> (Updated by <Your Name>)

'''


import nuke
import webbrowser
import inspect
import nuke
import os
from scripts import sg_creds
from gfoundation import gcontext
sg = sg_creds.sg_data()


no_mov_icon = r"Z:/studio_tools/pipe2/show/fopr/nuke/utilities/icons/no_mov.png"

mpco_options = ['Master', 'Parent', 'Child', 'Orphan', '-']

# Colour code dictionary
color_codes = {
    "Grey": "0xbababaff",
    "Green": "0xff00ff",
    "Blue": "0x9bffff",
    "Orange": "0xff6600ff",
    "Red": "0xff0000ff",
    "Purple": "0xff00bfff",
    "Master": "0xff00ff",
    "Parent": "0xff9bff",
    "Child": "0xb9ff00ff",
    "Orphan": "0xd754ffff",
    "Blank": "0xffffffff"
}

# Shotgrid pop-open button
open_shotgrid_page = '''

n = nuke.thisNode()

shot_id = n['shot_id_knob'].getValue()

import subprocess

# Format the URL with the project ID
url = f"https://giantanimation.shotgunstudio.com/detail/Shot/{shot_id}"

print ("Opening shot id: " + str(shot_id))

# Open URL in Chrome
webbrowser.open(url)


'''

# Knob change commands
parent_input_change_command = '''


n = nuke.thisNode()
k = nuke.thisKnob()

# Check if the knob that triggered the event is 'inputChange', 'mpco_dropdown_knob', or 'notes_name_knob'

if k.name() in ['inputChange', 'mpco_dropdown_knob', 'notes_name_knob']:

    from scripts import sg_creds
    sg = sg_creds.sg_data()

    # Handling inputChange knob

    if k.name() in ['inputChange', 'mpco_dropdown_knob']:

        if n.input(0) is not None:
        
            # Get knob data

            current_shot_id = n["shot_id_knob"].value()
            current_shot_code = n["shot_code_knob"].value()

            parent_code = n.input(0)["shot_code_knob"].value()
            parent_id = int(n.input(0)["shot_id_knob"].value())
            parent_type = n.input(0)["type_knob"].value()

            n['parent_code_knob'].setValue(parent_code)

            # Update the corresponding field in ShotGrid --------------------------

            if parent_type == 'Shot':
                entity_type = 'Shot'
            elif parent_type == 'Asset':
                entity_type = 'Asset'


            # Update sg_light_rig_parent --------------------------------------------
            filters = [['id', 'is', int(parent_id)]]
            fields = ['code']
            parent_asset = sg.find_one(entity_type, filters,fields)
            parent_data = {'sg_light_rig_parent': parent_asset}
            asset = sg.find_one(entity_type, filters, fields)

            
            try:
                update_parent_rig = sg.update('Shot', int(current_shot_id), parent_data)
                print (f"Successfully assigned [  {entity_type}  ] {parent_code}  as the parent for {current_shot_code}")
            except:
                print (f"Failed to assign {parent_code} as the parent for {current_shot_code}")
     
            
            # Update sg_light_rig_name --------------------------------------------
            if parent_type == 'Shot':
                n['parent_name_knob'].setValue('')
                parent_task = None
            elif parent_type == 'Asset':
                parent_task = n.input(0)["parent_name_knob"].value()
                n['parent_name_knob'].setValue(parent_task)
                sg.update('Shot', int(current_shot_id), {'sg_light_rig_name': parent_task})

            # Update knobs ---------------------------------------------------------
            n['parent_id_knob'].setValue(str(parent_id))
            n['parent_type_knob'].setValue(parent_type)
            n['shotgun_rig_knob'].setValue(parent_code)
            n['shotgun_rig_name_knob'].setValue(parent_task)
    
            
            # Update MPCO ----------------------------------------
            sg_mpco = n['mpco_dropdown_knob'].value()
            sg.update('Shot', int(n['shot_id_knob'].value()), {'sg_mpco': sg_mpco})

            n["shotgrid_mpco_knob"].setValue(sg_mpco)
            n["label"].setValue(sg_mpco)
            
            col = 0xffffffff

            if sg_mpco == "Master":
                col = 0xff00ff
            elif sg_mpco == "Parent":
                col = 0xff9bff
            elif sg_mpco == "Child":
                col = 0xb9ff00ff
            elif sg_mpco == "Orphan":
                col = 0xd754ffff
            elif sg_mpco == "-":
                col = 0xffffffff  
            
            n["tile_color"].setValue(col)
       
       
        elif n.input(0) is None:
        
            n['parent_code_knob'].setValue("")
            n['parent_name_knob'].setValue("")
            n['parent_id_knob'].setValue("")
            n['parent_type_knob'].setValue("")
            n['shotgun_rig_knob'].setValue("")
            n['shotgun_rig_name_knob'].setValue("")

            #Update sg_light_rig_parent and sg_light_rig_name
            parent_data = {'sg_light_rig_parent': None}
            asset = sg.find_one(entity_type, filters, fields)

            # Update MPCO ----------------------------------------
            sg.update('Shot', int(n['shot_id_knob'].value()), {'sg_light_rig_parent': None})
            sg.update('Shot', int(n['shot_id_knob'].value()), {'sg_light_rig_name': None})

            n["shotgrid_mpco_knob"].setValue(sg_mpco)
            n["label"].setValue(sg_mpco)
            
            col = 0xffffffff 
            
            n["tile_color"].setValue(col)

            print (f"Successfully disconnected inputs. Settings parent assignment values to none")

            
     
'''

def add_knob(group, knob_type, name, label, value='', visible=True, enabled=None):
    knob = knob_type(name, label)
    group.addKnob(knob)
    group.knob(name).setValue(value)
    group.knob(name).setVisible(visible)
    if enabled is not None:
        group.knob(name).setEnabled(enabled)

def add_divider(group):
    divider = nuke.Text_Knob("divName", "", "")
    group.addKnob(divider)

# ----------------------------------------------------------------------------


def get_shot_data(shot_id):

    # Get Shot data
    fields = ["id", "code", "sg_light_rig_parent", "sg_light_rig_name", "sg_mpco", "sg_lgt_cmp_notes", "type"]
    entity_details = sg.find_one("Shot", [["id", "is", shot_id]], fields)

    shot_code = entity_details['code']
    shot_id = entity_details['id']
    shot_mpco = entity_details['sg_mpco']
    shot_notes = entity_details['sg_lgt_cmp_notes']
    shot_type = entity_details['type']

    # Check if sg_light_rig_parent is not None before accessing its attributes
    if entity_details['sg_light_rig_parent']:
        parent_id = entity_details['sg_light_rig_parent']['id']
        parent_code = entity_details['sg_light_rig_parent']['name']
        parent_type = entity_details['sg_light_rig_parent']['type']
    else:
        parent_id = None
        parent_code = None
        parent_type = None

    parent_task = entity_details['sg_light_rig_name']

    # Get path to movie
    filters = [['entity', 'is', {'type': 'Shot', 'id': shot_id}]]
    fields = ['sg_path_to_movie']
    sorting = [{'column': 'created_at', 'direction': 'desc'}]
    # Query for the latest version
    latest_version = sg.find_one('Version', filters, fields, sorting)
    # Check if the result is valid and the field exists
    if latest_version and 'sg_path_to_movie' in latest_version:
        path_to_movie = latest_version['sg_path_to_movie']
    else:
        path_to_movie = None  # Or handle it as needed


    return shot_code, shot_id, shot_mpco, shot_notes, parent_id, parent_code, parent_type, parent_task, path_to_movie, shot_type


def create_giant_mpco_node(shot_id):

    #Unpack data
    shot_code, shot_id, shot_mpco, shot_notes, parent_id, parent_code, parent_type, parent_task, path_to_movie, shot_type = get_shot_data(shot_id)

      

    # Create Group Node ----------

    giant_mpco_group = nuke.nodes.Group(name=shot_code, label=shot_mpco, tile_color= "0xbababaff") # Grey tile colour
    giant_mpco_group['postage_stamp'].setValue(1)
    giant_mpco_group_name = giant_mpco_group.name()


    # Create Read Node and nest it inside the group ----------

    with giant_mpco_group:

        giant_input_node = nuke.nodes.Input(name='parent') 
        giant_mpco_node = nuke.nodes.Read(name='%s_Read' % giant_mpco_group.name())

        if path_to_movie:
            giant_mpco_node['file'].fromUserText(path_to_movie)
        else:
            giant_mpco_node['file'].fromUserText(no_mov_icon)

        giant_mpco_node['on_error'].setValue('checkerboard')
        giant_mpco_node_name = giant_mpco_node.name()
        nuke.nodes.Output().setInput(0, nuke.toNode(giant_mpco_node_name))
        tab = nuke.Tab_Knob('%s custom_tab' % giant_mpco_group_name, '%s options' % giant_mpco_node_name)
        giant_mpco_group.addKnob(tab)


    # Create knobs and add them to the group ----------   
    giant_mpco_group_name = "giant_mpco_group"
    add_divider(giant_mpco_group)


    # Light rig parent knob
    add_knob(giant_mpco_group, nuke.String_Knob, 'parent_code_knob', '  light rig parent ')
    giant_mpco_group.knob('parent_code_knob').setVisible(True)
    giant_mpco_group['parent_code_knob'].setValue(parent_code)


    # Light rig name knob
    add_knob(giant_mpco_group, nuke.String_Knob, 'parent_name_knob', '  light rig task ')
    add_divider(giant_mpco_group)
    giant_mpco_group.knob('parent_code_knob').setVisible(True)
    mpco_dropdown_knob = nuke.Enumeration_Knob('mpco_dropdown_knob', 'MPCO', mpco_options)
    giant_mpco_group.addKnob(mpco_dropdown_knob)
    mpco_dropdown_knob.setValue("-")
    giant_mpco_group['parent_name_knob'].setValue(parent_task)

    add_knob(giant_mpco_group, nuke.PyScript_Knob, 'open_shotgrid_page_knob', '  open shotgrid page ', value=open_shotgrid_page, enabled=True)


    # Shot Data Tab ----------

    shot_data_tab = nuke.Tab_Knob("shot_data_tab_knob", "shot data")
    giant_mpco_group.addKnob(shot_data_tab)
    
    # Shot data text ----------

    add_divider(giant_mpco_group)
    add_knob(giant_mpco_group, nuke.String_Knob, 'shot_code_knob', 'shot code')
    giant_mpco_group.knob('shot_code_knob').setEnabled(False)
    giant_mpco_group.knob('shot_code_knob').setValue(shot_code)
    add_knob(giant_mpco_group, nuke.String_Knob, 'shot_id_knob', 'shot id')
    giant_mpco_group.knob('shot_id_knob').setEnabled(False)
    giant_mpco_group.knob('shot_id_knob').setValue(str(shot_id))
    add_knob(giant_mpco_group, nuke.String_Knob, 'type_knob', 'shot type')
    giant_mpco_group.knob('type_knob').setEnabled(False)
    giant_mpco_group.knob('type_knob').setValue(str(shot_type))
    add_knob(giant_mpco_group, nuke.String_Knob, 'shotgrid_mpco_knob', 'shot mpco')
    giant_mpco_group.knob('shotgrid_mpco_knob').setEnabled(False)
    giant_mpco_group.knob('shotgrid_mpco_knob').setValue(str(shot_mpco))
    giant_mpco_group.knob('mpco_dropdown_knob').setValue(str(shot_mpco))
    add_divider(giant_mpco_group)

    # Parent Data
    add_knob(giant_mpco_group, nuke.String_Knob, 'parent_id_knob', 'parent id')
    giant_mpco_group.knob('parent_id_knob').setEnabled(False)
    giant_mpco_group.knob('parent_id_knob').setValue(str(parent_id))
    add_knob(giant_mpco_group, nuke.String_Knob, 'parent_type_knob', 'parent type')
    giant_mpco_group.knob('parent_type_knob').setEnabled(False)
    giant_mpco_group.knob('parent_type_knob').setValue(str(parent_type))
    add_knob(giant_mpco_group, nuke.String_Knob, 'shotgun_rig_knob', 'current parent code')
    giant_mpco_group.knob('shotgun_rig_knob').setEnabled(False)
    giant_mpco_group.knob('shotgun_rig_knob').setValue(parent_code)
    add_knob(giant_mpco_group, nuke.String_Knob, 'shotgun_rig_name_knob', 'current parent name')
    giant_mpco_group.knob('shotgun_rig_name_knob').setEnabled(False)
    giant_mpco_group.knob('shotgun_rig_name_knob').setValue(str(parent_task))


    # Update MPCO ----------------------------------------


    giant_mpco_group.knob("shotgrid_mpco_knob").setValue(shot_mpco)
    giant_mpco_group.knob("label").setValue(shot_mpco)
    
    col = 0xffffffff

    if shot_mpco == "Master":
        col = 0xff00ff
    elif shot_mpco == "Parent":
        col = 0xff9bff
    elif shot_mpco == "Child":
        col = 0xb9ff00ff
    elif shot_mpco == "Orphan":
        col = 0xd754ffff
    elif shot_mpco == "-":
        col = 0xffffffff  
    
    giant_mpco_group.knob("tile_color").setValue(col)
    
    giant_mpco_group['knobChanged'].setValue(parent_input_change_command)
    print(f"MPCO < SHOT >  node created for shot [ >> {shot_code} << ]")
    return shot_code


