
import nuke
import sg_creds

sg = sg_creds.sg_data()

def build_light_rig_group():


                    #callback for light rig parent knob
    inputName= '''

n = nuke.thisNode()
k = nuke.thisKnob()
if k.name() == 'parent_code_knob':


    n = nuke.thisNode()

    selection = n['parent_code_knob'].value()   


    sg = sg_creds.sg_data()
    #get project id and sequence
    from gfoundation import gcontext
    ctx = gcontext.Gcontext.get_from_env()
    current_show =  ctx.show
    current_sequence = ctx.sequence
    current_shot = ctx.shot

    #get project id
    project_get = sg.find("Project",[['code','is',current_show]])
    project_id = [d['id'] for d in project_get]
    project_id_string = str(project_id)
    project_id_string_number = ''.join(c for c in project_id_string if c in '0123456789')
    project_id_num = int(project_id_string_number)


    #get set asset data
    filters = [["project", "is", project_get], ["sg_asset_type", "is", "set"]]
    fields = ["code"]
    all_project_sets = sg.find("Asset", filters, fields)


    asset = next(item for item in all_project_sets if item["code"] == selection)
    asset_id = asset['id']
    filters = [["project", "is", project_get], ["entity.Asset.id", "in", [asset_id]]]
    fields = ["code","name","content"]
    all_asset_tasks = sg.find("Task", filters, fields)

    asset_tasks = []
    asset_list = [d['content'] for d in all_asset_tasks]
    asset_list.append('none')



    #update asset task list
    n['parent_name_knob'].setValues(asset_list)


    #update knobs
    light_rig = n['parent_code_knob'].value()
    #n["name"].setValue(str(light_rig))



    light_rig_name = n['parent_name_knob'].value()
    n["label"].setValue(str(rig_name) + ' ' + str(light_rig_name))



    n["shot_id_knob"].setValue(str(asset_id))   


    rig_name = n['parent_code_knob'].value()
    n['name_knob'].setValue(str(rig_name))




if k.name() == 'parent_name_knob':
    
    light_rig_name = n['parent_name_knob'].value()
    n["label"].setValue(str(rig_name) + ' ' + str(light_rig_name))




        



                         
     
    '''






    #get data #############################################

    #get project id and sequence
    from gfoundation import gcontext
    ctx = gcontext.Gcontext.get_from_env()
    current_show =  ctx.show
    current_sequence = ctx.sequence
    current_shot = ctx.shot

    #get project id
    project_get = sg.find("Project",[['code','is',current_show]])
    project_id = [d['id'] for d in project_get]
    project_id_string = str(project_id)
    project_id_string_number = ''.join(c for c in project_id_string if c in '0123456789')
    project_id_num = int(project_id_string_number)


    #get set asset data
    filters = [["project", "is", project_get], ["sg_asset_type", "is", "set"]]
    fields = ["code"]
    all_project_sets = sg.find("Asset", filters, fields)
    set_assets = [d['code'] for d in all_project_sets]
    parent_light_rig_name = set_assets[0]

    #find asset in set asset list
    asset = next(item for item in all_project_sets if item["code"] == parent_light_rig_name)
    asset_id = asset['id']
    filters = [["project", "is", project_get], ["entity.Asset.id", "in", [asset_id]]]
    fields = ["code","name","content"]
    all_asset_tasks = sg.find("Task", filters, fields)

    #get list of tasks for the asset
    asset_tasks = [d['content'] for d in all_asset_tasks]
    asset_tasks.append('none')


    #create group #########################################
    giant_light_rig_group =nuke.nodes.Group(name = 'light rig node',label= '', tile_color='0xcef9ffff')
    giant_light_rig_group['postage_stamp'].setValue(0)
    giant_light_rig_group.knob("tile_color").setValue(0xc1ffff)
    giant_light_rig_group_name = giant_light_rig_group.name()


    #create read node
    with giant_light_rig_group:

        #giant_input_node = nuke.nodes.Input(name = 'light_rig_input') 

        giant_light_rig_node = nuke.nodes.Read(name = 'light_rig_Read')
        #giant_mpco_node['file'].fromUserText(path_to_movie)
        giant_light_rig_node['on_error'].setValue('checkerboard')
        #giant_mpco_node['after'].setValue('black')
        giant_light_rig_node_name = giant_light_rig_node.name()
        nuke.nodes.Output().setInput(0, nuke.toNode(giant_light_rig_node_name))       
        
        #create custom tab
        tab = nuke.Tab_Knob('%s custom_tab' % giant_light_rig_node_name, '%s options' % giant_light_rig_node_name)
        giant_light_rig_group.addKnob(tab)

        #divider line 0
        d0 = nuke.Text_Knob("divName","","")
        giant_light_rig_group.addKnob(d0)


    #add controls---------------------------------------------------

     
        #set up parent light rig knob
        light_rig_parent = nuke.CascadingEnumeration_Knob('parent_code_knob', '  light rig parent ', set_assets)
        giant_light_rig_group.addKnob(light_rig_parent)
        giant_light_rig_group['knobChanged'].setValue(inputName)

        #set up parent light rig name knob==========
        light_rig_name = nuke.CascadingEnumeration_Knob('parent_name_knob', '  light rig name  ', asset_tasks)
        giant_light_rig_group.addKnob(light_rig_name) 
        #giant_light_rig_group['knobChanged'].setValue(inputNameTask)


        #divider line 2
        d2 = nuke.Text_Knob("divName","","")
        giant_light_rig_group.addKnob(d2)


        #add tab###########################################################################################################
        tab1 = nuke.Tab_Knob("tab1_knob","shot data")
        giant_light_rig_group.addKnob(tab1)



        #divider line 3
        d3 = nuke.Text_Knob("divName","","")
        giant_light_rig_group.addKnob(d3)   


        #asset_name
        asset_title = nuke.String_Knob('name_knob', '  name')
        giant_light_rig_group.addKnob(asset_title)
        rig_name = giant_light_rig_group['parent_code_knob'].value()
        nuke.toNode(giant_light_rig_group_name).knob('name_knob').setValue(str(rig_name))
        giant_light_rig_group.knob('name_knob').setEnabled(False)

        #asset_id
        asset_type = nuke.String_Knob('type_knob', '  node type')
        giant_light_rig_group.addKnob(asset_type)
        nuke.toNode(giant_light_rig_group_name).knob('type_knob').setValue('Asset')
        giant_light_rig_group.knob('type_knob').setEnabled(False)


        #set up shot id knob
        shot_id = nuke.String_Knob('shot_id_knob', '  asset id ')
        giant_light_rig_group.addKnob(shot_id)
        value = str(asset_id)
        nuke.toNode(giant_light_rig_group_name).knob('shot_id_knob').setValue(str(asset_id))
        giant_light_rig_group.knob('shot_id_knob').setEnabled(False)

        #set name knob

        giant_light_rig_group['knobChanged'].setValue(inputName)













