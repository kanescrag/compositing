import nuke
import webbrowser
from scripts import sg_creds
from gfoundation import gcontext




# Update episode dropdown function ------------------------
def populate_episodes():
    if project_id:
        # Query ShotGrid for episodes in the current project
        episodes = sg.find("Episode", [["project", "is", {"type": "Project", "id": project_id}]], ["code"])
        episode_names = [episode["code"] for episode in episodes] if episodes else ["No Episodes Found"]
        
        # Sort the episode names alphabetically
        episode_names.sort()
    else:
        episode_names = ["Project Not Found"]

    # Update episode_knob options
    episode_knob.setValues(episode_names)

# Update shots dropdown function --------------------------
def populate_shots(selected_episode):
    if project_id and selected_episode:
        # First, retrieve the Episode ID based on the selected episode code
        episode_entity = sg.find_one("Episode", [["project", "is", {"type": "Project", "id": project_id}],
                                                 ["code", "is", selected_episode]], ["id"])
        
        # Proceed only if we have a valid episode ID
        if episode_entity:
            episode_id = episode_entity["id"]
            # Now retrieve shots linked to this episode ID
            shots = sg.find("Shot", [["project", "is", {"type": "Project", "id": project_id}],
                                     ["sg_episode", "is", {"type": "Episode", "id": episode_id}]], ["code"])
            shot_names = [shot["code"] for shot in shots] if shots else ["No Shots Found"]
            print("Shots List:", shot_names)  # Print to confirm the list of shots
            shot_knob.setValues(shot_names)
        else:
            print("Episode not found for code:", selected_episode)
            shot_knob.setValues(["Episode Not Found"])
    else:
        shot_knob.setValues(["No Shots Found"])

# Update asset dropdown function --------------------------
def populate_assets():
    if project_id:
        filters = [["project", "is", {"type": "Project", "id": project_id}], ["sg_asset_type", "is", "set"]]
        fields = ["code", "id"]
        all_project_sets = sg.find("Asset", filters, fields)
        set_assets = [asset['code'] for asset in all_project_sets] if all_project_sets else ["No Sets Found"]
        set_assets = sorted(set_assets)
    else:
        set_assets = ["Project Not Found"]

    # Update asset_knob options
    asset_knob.setValues(set_assets)

# Update task dropdown function ---------------------------
def populate_tasks():
    selected_asset = asset_knob.value()
    if project_id and selected_asset:
        asset_entity = sg.find_one(
            "Asset", 
            [["project", "is", {"type": "Project", "id": project_id}], ["code", "is", selected_asset]], 
            ["id"]
        )
        
        if asset_entity:
            asset_id = asset_entity["id"]
            tasks = sg.find("Task", [["entity", "is", {"type": "Asset", "id": asset_id}]], ["content"])
            task_names = [task["content"] for task in tasks] if tasks else ["No Tasks Found"]
        else:
            task_names = ["Asset Not Found"]
    else:
        task_names = ["Project Not Found"]

    task_knob.setValues(task_names)
    
# Shotgrid Button function
def open_shotgrid_page():
    n = nuke.thisNode()

    # Get the type from the 'type_knob' (either 'Shot' or 'Asset')
    type_value = n['type_knob'].value()

    # Initialize variables for the ID and URL type
    url_type = ''
    id_value = None

    # Query ShotGrid based on type ('Shot' or 'Asset')
    if type_value == "Shot":
        # Get the selected shot name
        shot_name = n['shot_knob'].value()
        url_type = "Shot"
        
        # Query ShotGrid to get the shot ID based on the shot name
        shot_entity = sg.find_one("Shot", [["code", "is", shot_name]], ["id"])
        if shot_entity:
            id_value = shot_entity["id"]
        else:
            print(f"Shot '{shot_name}' not found in ShotGrid.")
            return
    else:
        # Get the selected asset name
        asset_name = n['asset_knob'].value()
        url_type = "Asset"
        
        # Query ShotGrid to get the asset ID based on the asset name
        asset_entity = sg.find_one("Asset", [["code", "is", asset_name]], ["id"])
        if asset_entity:
            id_value = asset_entity["id"]
        else:
            print(f"Asset '{asset_name}' not found in ShotGrid.")
            return

    # Format the ShotGrid URL dynamically
    if id_value:
        url = f"https://giantanimation.shotgunstudio.com/detail/{url_type}/{id_value}"
        print(f"Opening {url_type.lower()} id: {id_value}")
        # Open the URL in the default web browser
        webbrowser.open(url)

# Update versions dropdown function ------------------------
def populate_versions(shot_code):
    selected_version = versions_knob.value()
    
    if project_id and selected_version:
        shot_entity = sg.find_one(
            'Shot',
            [['code', 'is', shot_code]],
            ['id']
        )
        
        if shot_entity:
            shot_id = shot_entity['id']
            versions = sg.find(
                'Version',
                [['entity', 'is', {'type': 'Shot', 'id': shot_id}]],
                ['sg_path_to_movie'],
                [{'column': 'created_at', 'direction': 'asc'}]
            )
            
            version_names = [
                version['sg_path_to_movie'].split('/')[-1] for version in versions
            ] if versions else ["No Versions Found"]
        else:
            version_names = ["Shot Not Found"]
    else:
        version_names = ["Project Not Found"]

    versions_knob.setValues(version_names)


# Change function -----------------------------------------
def command_change():
    """
    Callback function to handle knob changes in the custom group node.
    It ensures updates occur only when specific knobs are modified.
    """
    n = nuke.thisNode()
    k = nuke.thisKnob()

    if not k:  # Ensure there is an active knob change event
        return

    try:
        knob_name = k.name()

        # Handle 'type_knob' changes
        if knob_name == "type_knob":
            type_value = n["type_knob"].value()

            if n["type_knob"].value() == "Shot":
                n["shot_knob"].setVisible(True)
                n["mpco_knob"].setVisible(True)
                n["episode_knob"].setVisible(True)
                n["shotgrid_knob"].setVisible(True)
                n["notes_knob"].setVisible(True)
                n["notes_publish_knob"].setVisible(True)
                n["asset_knob"].setVisible(False)
                n["task_knob"].setVisible(False)
                n["task_knob"].setVisible(False)
                n["read_versions_knob"].setVisible(True)
                n["update_policy_knob"].setVisible(True)              
                

                # Update label with the value of mpco_knob
                mpco_value = n["mpco_knob"].value()
                if mpco_value:
                    formatted_label = f"----\nMPCO: {mpco_value}"
                    n["label"].setValue(formatted_label)
                    print(f"Label updated to: {formatted_label}")

            else:  # Asset mode
                n["shot_knob"].setVisible(False)
                n["mpco_knob"].setVisible(False)
                n["episode_knob"].setVisible(False)
                n["notes_knob"].setVisible(False)
                n["notes_publish_knob"].setVisible(False)
                n["asset_knob"].setVisible(True)
                n["task_knob"].setVisible(True)
                n["shotgrid_knob"].setVisible(True)
                n["read_versions_knob"].setVisible(True)
                n["update_policy_knob"].setVisible(True)

                # Update label with the value of task_knob
                task_value = n["task_knob"].value()
                if task_value:
                    formatted_label = f"----\nTask: {task_value}"
                    n["label"].setValue(formatted_label)
                    print(f"Label updated to: {formatted_label}")


            # Update the group name based on type
            if type_value == "Shot":
                shot_name = n["shot_knob"].value()
                if shot_name:
                    n.setName(f"{shot_name}_MPCO")
            elif type_value == "Asset":
                asset_name = n["asset_knob"].value()
                if asset_name:
                    n.setName(f"{asset_name}_MPCO")

        # Handle 'shot_knob' changes
        elif knob_name == "shot_knob":
            shot_name = n["shot_knob"].value()
            if shot_name:
                new_name = f"{shot_name}_MPCO"
                n.setName(new_name)
                print(f"Group node renamed to: {new_name}")

                # Fetch and update 'mpco_knob' from ShotGrid
                shot_entity = sg.find_one("Shot", [["code", "is", shot_name]], ["sg_mpco"])
                if shot_entity and "sg_mpco" in shot_entity:
                    mpco_value = shot_entity["sg_mpco"] or "-"
                    n["mpco_knob"].setValue(mpco_value)
                    print(f"mpco_knob updated to: {mpco_value}")
                    
                # Populate versions_knob based on the selected shot
                populate_versions(shot_name)

        # Handle 'asset_knob' changes
        elif knob_name == "asset_knob":
            asset_value = n["asset_knob"].value()
            if asset_value:
                new_name = f"{asset_value}_MPCO"
                n.setName(new_name)
                print(f"Group node renamed to: {new_name}")
                populate_tasks()  # Update task list based on asset

        # Handle 'mpco_knob' changes and update label
        if knob_name == "mpco_knob":
            mpco_value = n["mpco_knob"].value()
            if mpco_value:
                formatted_label = f"----\n{mpco_value}"
                n["label"].setValue(formatted_label)
                print(f"Label updated to: {formatted_label}")

        # Handle 'episode_knob' changes
        elif knob_name == "episode_knob":
            selected_episode = n["episode_knob"].value()
            if selected_episode:
                print(f"Episode changed to: {selected_episode}")
                populate_shots(selected_episode)  # Update shot dropdown...

                shot_name = n["shot_knob"].value()
                if shot_name:
                    new_name = f"{shot_name}_MPCO"
                    n.setName(new_name)
                    print(f"Group node renamed to: {new_name}")

        # Handle 'task_knob' changes
        elif knob_name == "task_knob":
            task_value = n["task_knob"].value()
            if task_value:
                formatted_label = f"{task_value}"
                n["label"].setValue(formatted_label)
                print(f"Label updated to: {formatted_label}")

        # Handle 'versions_knob' changes
        elif knob_name == "versions_knob":
            selected_version = n["versions_knob"].value()
            if selected_version:
                # Fetch the ShotGrid entity for the selected version (assuming it's a Shot version)
                shot_name = n["shot_knob"].value()
                if shot_name:
                    # Query ShotGrid to get the shot ID based on the shot name
                    shot_entity = sg.find_one("Shot", [["code", "is", shot_name]], ["id"])

                    if shot_entity:
                        shot_id = shot_entity["id"]
                        # Query the Version for the selected version
                        version_entity = sg.find_one(
                            'Version',
                            [['entity', 'is', {'type': 'Shot', 'id': shot_id}]],
                            ['sg_path_to_movie']
                        )
                        
                        if version_entity and "sg_path_to_movie" in version_entity:
                            version_path = version_entity["sg_path_to_movie"]
                            print(f"Selected version path: {version_path}")
                            
                            # Access the group node

                            n["file"].setValue(version_path)
                            print(f"Updated 'giant_mcpo_read' file path to: {version_path}")




        # Handle visibility updates
        #else:
        #    print(f"Unhandled knob change: {knob_name}")

    except Exception as e:
        print(f"Error in command_change: {e}")



# Create the group node -----------------------------------------

group_node = nuke.createNode("Group", "name MPCO")
group_node.begin()

# Initialise ShotGrid connection
sg = sg_creds.sg_data()

# Retrieve current project, sequence, and shot details from environment
ctx = gcontext.Gcontext.get_from_env()
current_show = ctx.show
current_sequence = ctx.sequence
current_shot = ctx.shot

# Get project ID
project_get = sg.find("Project", [['code', 'is', current_show]])
project_id = project_get[0]['id'] if project_get else None

# ---- Add Tab and elements ---- 

# Add a custom tab to the group
tab_knob = nuke.Tab_Knob('MPCO')
group_node.addKnob(tab_knob)

# Add the 'Type' dropdown knob
type_knob = nuke.Enumeration_Knob("type_knob", "Type", ["Shot", "Asset"])
group_node.addKnob(type_knob)

# Divider
divider_knob = nuke.Text_Knob("divider", "")
group_node.addKnob(divider_knob)

# --- Episode Section ---

episode_knob = nuke.Enumeration_Knob("episode_knob", "Episode", [])
group_node.addKnob(episode_knob)
populate_episodes()

# --- Shot Section ---

# Function to populate shot_knob with shot data from ShotGrid

# Shot dropdown with dynamic ShotGrid shot list
shot_knob = nuke.Enumeration_Knob("shot_knob", "Shot", [])
shot_knob.setFlag(nuke.STARTLINE)
group_node.addKnob(shot_knob)
shot_knob.setVisible(True)  # Make visible by default
populate_shots(episode_knob.value())  # Populate shots at build

###populate_shots(episode_knob.value())  # Populate shots at build

# MPCO dropdown for Shot category
mpco_knob = nuke.Enumeration_Knob("mpco_knob", "MPCO", ["Master", "Parent", "Child", "Orphan", "-"])
group_node.addKnob(mpco_knob)

# ShotGrid button to open a ShotGrid page
shotgrid_knob = nuke.PyScript_Knob("shotgrid_knob", "Open ShotGrid Page")
group_node.addKnob(shotgrid_knob)

# Divider
divider_knob = nuke.Text_Knob("divider", "")
group_node.addKnob(divider_knob)

# Add Task Type Review Knob
versions_knob = nuke.Enumeration_Knob("versions_knob", "versions", [])
group_node.addKnob(versions_knob)

update_policy_knob = nuke.Enumeration_Knob("update_policy_knob", "update policy", ["Automatic","Manual"])
group_node.addKnob(update_policy_knob)

# Divider
divider_knob = nuke.Text_Knob("divider", "")
group_node.addKnob(divider_knob)

# Notes text input knob
notes_knob = nuke.String_Knob("notes_knob", "Notes")
group_node.addKnob(notes_knob)

# Commit Notes button
notes_publish_knob = nuke.PyScript_Knob("notes_publish_knob", "Commit Notes")
group_node.addKnob(notes_publish_knob)

# --- Asset Section ---

# Function to populate asset_knob with asset data based on project ID


# Asset selection knob
asset_knob = nuke.Enumeration_Knob("asset_knob", "Asset", [])
group_node.addKnob(asset_knob)
populate_assets()

# Task dropdown for Asset category
task_knob = nuke.Enumeration_Knob("task_knob", "Task", [])
group_node.addKnob(task_knob)
populate_tasks()

# Callback function to control visibility based on 'type_knob' selection

# Set the label value during group build
initial_mpco_value = group_node["mpco_knob"].value()
formatted_initial_label = f"----\n{initial_mpco_value}"
group_node["label"].setValue(formatted_initial_label)

# Attach the callback function to run on knob changes
group_node.knob("type_knob").setValue("Shot")
group_node.knob("knobChanged").setValue("command_change()")
group_node.knob("asset_knob").setValue("command_change()")
group_node.knob("shot_knob").setValue("command_change()")
group_node.knob("episode_knob").setValue("command_change()")  # Add callback for asset_knob


# Define actions for the ShotGrid and Commit Notes buttons
shotgrid_knob.setCommand("open_shotgrid_page()")
notes_publish_knob.setCommand("print('Notes committed: {}'.format(group_node['notes_knob'].value()))")

# Attach the callback function to run on knob changes
group_node.knob("knobChanged").setValue("command_change()")

# Set default value for type_knob and ensure visibility is correct
group_node.knob("type_knob").setValue("Shot")  # Default to 'Shot'

group_node["shot_knob"].setVisible(True)
group_node["mpco_knob"].setVisible(True)
group_node["episode_knob"].setVisible(True)
group_node["shotgrid_knob"].setVisible(True)
group_node["notes_knob"].setVisible(True)
group_node["notes_publish_knob"].setVisible(True)
group_node["asset_knob"].setVisible(False)
group_node["task_knob"].setVisible(False)

# Set group name to shot code
#shot_name = group_node["shot_knob"].value()
#if shot_name:
#    new_name = f"{shot_name}_MPCO"
#    group_node.setName(new_name)
#    print(f"Group node renamed to: {new_name}")

# Set group name to unassigned placeholder
shot_name = group_node["shot_knob"].value()
if shot_name:
    new_name = "Unnasigned_MPCO"
    group_node.setName(new_name)
    print(f"Group node renamed to: {new_name}")

group_node["mpco_knob"].setValue("-")

# Run the callback to set initial visibility based on the default selection
command_change()

group_node["mpco_knob"].setValue("-")

#Add Group Nodes ------------------------------------
# Create input, read, and output nodes using nuke.nodes to avoid panel opening
giant_mpco_input = nuke.nodes.Input(name="giant_mpco_input")
giant_mpco_read = nuke.nodes.Read(name="giant_mpco_read")
giant_mpco_output = nuke.nodes.Output(name="giant_mpco_output")

file_knob = giant_mpco_read['file']  # Access the file knob of the Read node
group_node.addKnob(file_knob)

# Connect the input to the read node and the read node to the output
giant_mpco_read.setInput(0, giant_mpco_input)  # Input -> Read
giant_mpco_output.setInput(0, giant_mpco_read)  # Read -> Output

group_node["postage_stamp"].setValue(True)


group_node.end()


