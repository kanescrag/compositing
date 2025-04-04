import nuke
from scripts import sg_creds
from gfoundation import gcontext
import re  # Regular expressions for validation

# Connect to Shotgun and get the current context
sg = sg_creds.sg_data()
ctx = gcontext.Gcontext.get_from_env()

# Function to get frame range from Shotgun using shot ID
def get_frame_range():
    shot_data = ctx.get_shot()  # Retrieve current shot data
    if shot_data:
        cut_in = shot_data.get("sg_cut_in", None)
        cut_out = shot_data.get("sg_cut_out", None)
        if cut_in and cut_out:
            return f"{cut_in}-{cut_out}"
    return ""

# Function to update frame range when the button is clicked
def update_frame_range():
    frame_range = get_frame_range()
    if frame_range:
        group_node["frame_range"].setValue(frame_range)
        nuke.message(f"Frame range updated to: {frame_range}")
    else:
        nuke.message("Unable to retrieve frame range from Shotgun.")

# Function to validate the Notes input
def validate_notes_input():
    notes_knob = group_node["notes"]
    current_value = notes_knob.value()
    
    # Allow only alphanumeric characters and spaces
    valid_value = re.sub(r"[^a-zA-Z0-9\s]", "", current_value)
    
    # Update the knob if the input was invalid
    if current_value != valid_value:
        notes_knob.setValue(valid_value)

# Function to update frame_range visibility based on override_frame_range checkbox
# Function to update frame_range visibility based on override_frame_range checkbox
def update_knob_visibility():
    if group_node["override_frame_range"].value():
        group_node["frame_range"].setEnabled(True)  # Enable the frame_range knob
    else:
        group_node["frame_range"].setEnabled(False)  # Disable the frame_range knob

# Add a knob changed callback to monitor override_frame_range changes
nuke.addKnobChanged(update_knob_visibility, node=group_node)

# Function to update write node channels based on the Alpha Data dropdown
def update_write_node_channels():
    alpha_data_value = group_node["alpha_data"].value()
    # Find the write node inside the group node
    write_node = group_node.node("giant_write_node")
    
    if alpha_data_value == "Include":
        write_node["channels"].setValue("rgba")  # Set channels to RGBA
    else:
        write_node["channels"].setValue("rgb")  # Set channels to RGB

# Function to handle the Publish button's functionality
def publish_action():
    # Find the write node inside the group
    write_node = group_node.node("giant_write_node")
    
    # Check if the Notes field is empty
    notes_value = group_node["notes"].value().strip()
    if not notes_value:
        nuke.message("Please add a note before publishing.")
        return
    
    # Get the selected publish type
    publish_type = group_node["publish_type"].value()
    
    # Set the exec_cmd based on the publish type
    if publish_type == "Publish Sequence to Farm":
        exec_cmd = "from nuke_pipeline import cmp_publish;cmp_publish.submit_farm_node_button(repr(write_node))"
    elif publish_type == "Publish Sequence Locally":
        exec_cmd = "from nuke_pipeline import cmp_publish;cmp_publish.submit_locally_node_button(repr(write_node))"
    elif publish_type == "Publish Scene File Only":
        exec_cmd = "from nuke_pipeline import cmp_publish;cmp_publish.publish_source_file_node_button()"
    else:
        nuke.message("Invalid Publish Type selected.")
        return
    
    # Execute the determined command
    exec(exec_cmd)

# Check if the group node already exists and delete it
existing_node = nuke.toNode("GIANT_WRITE")
if existing_node:
    nuke.delete(existing_node)

# Create the group node
group_node = nuke.createNode("Group")
group_node.setName("GIANT_WRITE")

# Disable Postage Stamp option
group_node["postage_stamp"].setValue(False)

# Set the node colour to purple
group_node["tile_color"].setValue(8388736)  # Hexadecimal #800080 as an integer

# Begin the group to add knobs
group_node.begin()

# Add user tab with renamed label
group_tab_knob = nuke.Tab_Knob("user", "Giant Write Options")
group_node.addKnob(group_tab_knob)

# Divider above Notes
divider_before_notes = nuke.Text_Knob("divider_before_notes", "")
group_node.addKnob(divider_before_notes)

# Notes Text Entry Box
notes_entry_knob = nuke.String_Knob("notes", "Notes")
group_node.addKnob(notes_entry_knob)

# Add a knob changed callback for the Notes input
nuke.addKnobChanged(validate_notes_input, node=group_node)

# Divider after Notes
divider_after_notes = nuke.Text_Knob("divider_after_notes", "")
group_node.addKnob(divider_after_notes)

# Publish Type Dropdown (1st)
publish_type_knob = nuke.Enumeration_Knob(
    "publish_type", "Publish Type", ["Publish Sequence to Farm", "Publish Sequence Locally", "Publish Scene File Only"]
)
group_node.addKnob(publish_type_knob)

# Render Type Dropdown (2nd)
dropdown_knob = nuke.Enumeration_Knob("render_type", "Render Type", ["comp_render", "comp_rsmb", "comp_sapphire"])
group_node.addKnob(dropdown_knob)

# Alpha Data Dropdown (3rd)
alpha_data_knob = nuke.Enumeration_Knob("alpha_data", "Alpha Data", ["Exclude", "Include"])
group_node.addKnob(alpha_data_knob)

# Add a knob changed callback for the Alpha Data dropdown
nuke.addKnobChanged(update_write_node_channels, node=group_node)

# Divider
divider = nuke.Text_Knob("divider", "")
group_node.addKnob(divider)

# Frame Range and Override Frame Range placed after the divider
# Text Entry for Frame Range (initially disabled)
frame_range_knob = nuke.String_Knob("frame_range", "Frame Range")
frame_range_knob.setValue(get_frame_range())  # Pre-fill with the frame range from Shotgun
frame_range_knob.setEnabled(False)  # Disabled by default
group_node.addKnob(frame_range_knob)

# Checkbox for Override Frame Range
frame_override_knob = nuke.Boolean_Knob("override_frame_range", "Override Frame Range")
frame_override_knob.setFlag(nuke.STARTLINE)  # Place on the same line as frame range
group_node.addKnob(frame_override_knob)

# Add a callback to monitor changes in the group node's knobs
nuke.addKnobChanged(update_knob_visibility, node=group_node)

# Update Frame Range Button
update_frame_range_button = nuke.PyScript_Knob("update_frame_range", "Update Frame Range")
update_frame_range_button.setCommand('update_frame_range()')  # Corrected to pass function call as string
group_node.addKnob(update_frame_range_button)

# Divider before Publish button
divider_before_publish = nuke.Text_Knob("divider_before_publish", "")
group_node.addKnob(divider_before_publish)

# Publish Python Button
publish_button = nuke.PyScript_Knob("publish", "Publish")
publish_button.setCommand('publish_action()')  # Corrected to pass function call as string
group_node.addKnob(publish_button)

# Divider before Open Shot Page button
divider_before_shot_page = nuke.Text_Knob("divider_before_shot_page", "")
group_node.addKnob(divider_before_shot_page)

# Open Shot Page Button
def open_shot_page():
    shot_data = ctx.get_shot()
    if shot_data:
        shot_id = shot_data.get("id")
        if shot_id:
            url = f"https://giantanimation.shotgunstudio.com/detail/Shot/{shot_id}"
            import webbrowser
            webbrowser.open(url)
        else:
            nuke.message("Shot ID not found.")
    else:
        nuke.message("Unable to retrieve shot data.")

# Create Open Shot Page Button and assign the function directly
open_shot_page_button = nuke.PyScript_Knob("open_shot_page", "Open Shot Page")
open_shot_page_button.setCommand('open_shot_page()')  # Corrected to pass function call as string
group_node.addKnob(open_shot_page_button)

# End the group to commit the changes
group_node.end()

# Create the input node inside the group using nuke.nodes
group_node.begin()
pipe_input_node = nuke.nodes.Input(name="pipe_input")
group_node.end()

# Create the write node inside the group using nuke.nodes
group_node.begin()
write_node = nuke.nodes.Write(name="giant_write_node")
write_node["file_type"].setValue("exr")  # Set file type to EXR
write_node["datatype"].setValue("16 bit")  # Set data type to 16-bit
write_node["compression"].setValue("zip")  # Set compression to ZIP (1 scanline)
write_node["create_directories"].setValue(True)  # Enable directory creation
write_node["channels"].setValue("rgb")  # Default channels to RGB
write_node.setInput(0, pipe_input_node)
group_node.end()

# Trigger an update on knob visibility
update_knob_visibility()
