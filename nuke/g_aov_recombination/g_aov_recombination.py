import nuke

def shuffleAOV():
    class ObjectNode:
        """Node Object Instance
        You can retrieve the following information :
        - Node's name
        - Node's type
        - Node's location inside Nuke's memory
        - Node's AOVs (all and only lights)
        - Node's filepath if existing
        """

        def __init__(self, name):
            ##### OBJECT DATA ______________________________________________________
            self.name = name                          # Object's name
            self.node = nuke.toNode(name)             # Object's node informations
            self.type = self.node.Class()             # Object's class

            self.aovs = self._getAovs()[0]            # Object's AOVs (ALL)
            self.lgtAovs = self._getAovs()[1]         # Object's AOVs (Lights)

            if self.node.knob('file'):
                self.filePath = self._getFileType()[0]      # Object's file full path
                self.fileName = self._getFileType()[1]      # Object's file name and extension
                self.fileType = self._getFileType()[2]      # Object's file type (BG000, CH000, CH001, SD000, ...)
                self.passType = self.fileType[:2]           # Object's pass type (BG, CH or SD)

            ##### FOCUS ON OBJECT __________________________________________________
            nukescripts.clear_selection_recursive()   # Unselect (All)
            self.node.knob('selected').setValue(True) # Select (OBJECT)


        def _getAovs(self):
            """
            Get all AOVS from node and determine which one is a Light AOV
            Use self.node variable from __init__
            """

            aovs = []; lgtAovs = []; nodeChannels = self.node.channels()

            ##### GET ALL AOVS _____________________________________________________
            for channel in nodeChannels:
                channelName = channel.split('.', 1)[0]
                if channelName not in aovs:
                    aovs.append(channelName)
            
            ##### GET LIGHTS GROUPS AOVS ___________________________________________
            lgtAovs = [ aov for aov in aovs if 'Beauty' in aov ]

            return aovs, lgtAovs


        def _getFileType(self):
            """
            Get path and full name of node's file and define pass name (for example " CH001 ")
            """

            filePath = self.node['file'].value()
            fileName = os.path.basename(filePath)

            a = fileName.rpartition('_')
            b = a[-1].split('.')
            fileType = b[0]

            return filePath, fileName, fileType


        def _isEmpty(self, n):
            """
            Check pixels' areas from selected node. Return " True " if all of them are under a specified number
            """

            num = 7
            minPvalue = 1e-03

            width = nuke.root().width()
            height = nuke.root().height()

            xPos = []
            yPos = []
            xDis = (width/num)
            yDis = (height/num)

            for i in range(num):
                xPos.append(xDis*i)
                yPos.append(yDis*i)

            channels = ['r', 'g', 'b']
            min = 0
            for channel in channels:
                for i in xPos:
                    for j in yPos:
                        sampleArea = n.sample(channel, i, j, xDis, yDis)
                        if sampleArea > min:
                            min = sampleArea

            if min >= minPvalue:
                isEmpty = False
            else:
                isEmpty = True
           
            return isEmpty


        def shuffleLgts(self):
            """
            Create GUIZMO for each lights AOVS if not empty.
            return lgtGroup : Gizmo's node
            """

            knobsList = []
            multList = []
            testList = []
            multList = []

            if self.type == 'Read':
                gArray = []; i = 0; xPos = 200; first = False

                # Increment Group Name
                nodesList = [each.name() for each in nuke.allNodes()]
                name = self.name+'_Group_'; version = 1; grpName = name+str(version)
                while grpName in nodesList:version+=1;grpName = name+str(version)
                # Lights Group Creation
                lgtGroup = nuke.nodes.Group(name= grpName, label='Lights', tile_color='3685094657')
                lgtGroup.setInput(0, nuke.toNode(self.name))


        
                ##### ENTER GROUP NODE  _________________________________________________
                lgtGroup.begin()
        
                input = nuke.nodes.Input(); input['tile_color'].setValue(421075201); input['name'].setValue(self.fileType); input.setXYpos(0, 0)
                dot = nuke.nodes.Dot(); dot['name'].setValue(self.fileType+' Main Dot'); dot.setInput(0, input); dot.setXYpos(34, 50)
        
                # Sort Lights AOVs variable
                self.lgtAovs.sort()

                keys = [ lgtAov for lgtAov in self.lgtAovs if 'key' in lgtAov.lower() ]
                fills = [ lgtAov for lgtAov in self.lgtAovs if 'fill' in lgtAov.lower() ]
                other = [ lgtAov for lgtAov in self.lgtAovs if 'other' in lgtAov.lower() ]
                any = [ lgtAov for lgtAov in self.lgtAovs if not 'key' and 'fill' and 'other' in lgtAov.lower() ]

                self.lgtAovs = other+keys+fills+any
                
                # Lights Passes Shuffles and Multiply
                for lgtPass in self.lgtAovs:
                    dotLgt = nuke.nodes.Dot(); dotLgt.setInput(0,dot); dotLgt.setXYpos(xPos, 50)
                    # Create SHUFFLE for LGT pass
                    shuffle = nuke.nodes.Shuffle(postage_stamp=True)
                    shuffle['in'].setValue(lgtPass)
                    shuffle['name'].setValue(lgtPass.split('_', 1)[1].upper())
                    shuffle.setInput(0,dotLgt)


                    # Create Multiply for LGT pass and its outputDot
                    mult = nuke.nodes.Multiply(label=lgtPass, channels='rgb')
                    mult['value'].setValue([1,1,1,1])
                    mult.setInput(0, shuffle)

                    if first == True:
                        gDot = nuke.nodes.Dot(); gDot.setInput(0, mult); gDot.setXYpos(xPos, 254)
                        gArray.append(gDot)
                    else:
                        gArray.append(mult)
                        first = True
                    # Create KNOB and set expression to Multiply
                    knobMultName = str(lgtPass)+'mult'
                    knobMult = nuke.Color_Knob(knobMultName, (lgtPass))
                    knobMult.setRange(0,4)

                    xPos += 100

                    if self._isEmpty(shuffle) == True:
                        shuffle['label'].setValue('EMPTY PASS')
                        shuffle['tile_color'].setValue(2139062017)
                        testList.append([knobMult, knobMultName, mult])
                        multList.append([knobMult, knobMultName, mult])
                    else:
                        knobsList.append([knobMult, knobMultName, mult])
                        multList.append([knobMult, knobMultName, mult])
        
                # Merge
                mergeLgts = nuke.nodes.Merge2(); mergeLgts['operation'].setValue('plus'); mergeLgts['maskChannelMask'].setValue('none'); mergeLgts.setXYpos(166, 250)
                for mult in gArray:
                    if i == 2:
                        i += 1
                        mergeLgts.setInput(i,mult)
                    else:
                        mergeLgts.setInput(i,mult)
                        nom = mult['name'].value()
                    i += 1
        
                # Shuffle Copy and its Dot
                alphaDot = nuke.nodes.Dot(); alphaDot.setInput(0, input); alphaDot.setXYpos(34, 300)
                alpha = nuke.nodes.ShuffleCopy(); alpha.setInput(1, alphaDot); alpha.setInput(0, mergeLgts); alpha.setXYpos(166, 296)
        
                # Output
                output = nuke.nodes.Output(); output['tile_color'].setValue(421075201); output['name'].setValue('OUTPUT'); output.setInput(0, alpha); output.setXYpos(166, 400)

                # Switch Node
                switch = nuke.nodes.Switch()
                switch.setInput(0, mergeLgts)
                switch.setXYpos(166, 375)
                switch['hide_input'].setValue(True)
                i = 1
                for k in multList:
                    switch.setInput(i, k[2])
                    i += 1

                output.setInput(0, switch)
        
                lgtGroup.end()
                ##### EXIT GROUP NODE  __________________________________________________



                ##### CREATE KNOBS  _____________________________________________________
                switchKnobs = []

                # Help Text
                lgtGroup.addKnob(nuke.Text_Knob('Help', 'How to -', "\nDon't forget to make sure that ALL LIGHTS button is selected\nbefore rendering (Button is gray)"))

                # Current Display Text
                lgtGroup.addKnob(nuke.Text_Knob('Displaying', '<b>Current Display -</b>', "<b>ALL LIGHTS</b>"))
                lgtGroup.addKnob(nuke.Text_Knob('\t', '', ''))

                # Combined Lights Button - Default state is Selected
                k = nuke.PyScript_Knob('AllLights', '\t\t\t\t\t\t\t\t\t\t ALL LIGHTS  \t\t\t\t\t\t\t\t\t\t', "switchNode = nuke.toNode('{SWITCH}')\nswitchNode['which'].setValue(0)\nk = 'AllLights'\nlgtGroup = nuke.toNode('{GROUP}')\nfor knob in lgtGroup.knobs():\n if knob == k:\n  lgtGroup[knob].setEnabled(False)\n if not knob == k:\n  lgtGroup[knob].setEnabled(True)\n".format(SWITCH= switch.fullName(), GROUP=lgtGroup.fullName())); k.setEnabled(False)
                lgtGroup.addKnob(k); lgtGroup.addKnob(nuke.Text_Knob('\n', '\n', '\n',))
                switchKnobs.append(k)

                # Main Lights Tab
                lgtGroup.addKnob(nuke.BeginTabGroup_Knob())

                lgtGroup.addKnob(nuke.Tab_Knob('MAIN LIGHTS PASSES \t\t\t\t\t'))
                i = 1
                firstK=True; firstF=True; firstA=True; firstO=False

                dividerKeys=False; dividerFills=False; dividerAny=False;
                for lgtpass in multList:
                    if lgtpass in knobsList:

                        if 'other' in lgtpass[1]:
                            dividerKeys=True
                            lgtGroup.addKnob(nuke.Text_Knob('\t', '<font color=#408bff>GI</font>', ''))
                        if 'key' in lgtpass[1]:
                            dividerFills=True
                            if firstK==True:
                                if dividerKeys==True:
                                    lgtGroup.addKnob(nuke.Text_Knob('\n', '\n', '\n'))
                                lgtGroup.addKnob(nuke.Text_Knob('\t', '<font color=#ffc400>Keys</font>', ''))
                                firstK=False
                        if 'fill' in lgtpass[1]:
                            dividerAny=True
                            if firstF==True:
                                if dividerFills==True:
                                    lgtGroup.addKnob(nuke.Text_Knob('\n', '\n', '\n'))
                                lgtGroup.addKnob(nuke.Text_Knob('\t', '<font color=#ffc400>Fills</font>', ''))
                                firstF=False
                        if 'any' in lgtpass[1]:
                            if firstA==True:
                                if dividerAny==True:
                                    lgtGroup.addKnob(nuke.Text_Knob('\n', '\n', '\n'))
                                lgtGroup.addKnob(nuke.Text_Knob('\t', '<font color=#ffc400>Others</font>', ''))
                                firstA=False

                        lgtGroup.addKnob(lgtpass[0])
                        lgtGroup[lgtpass[1]].setValue(1)
        
                        # Isolation Button
                        kName = 'display_'+str(lgtpass[1].split('Beauty_')[1].split('mult')[0])
                        k = nuke.PyScript_Knob(kName, '👁️', "k = '{KNOB}'\nlgtGroup = nuke.toNode('{GROUP}')\nfor knob in lgtGroup.knobs():\n if knob == k:\n  lgtGroup[knob].setEnabled(False)\n if not knob == k:\n  lgtGroup[knob].setEnabled(True)\nswitchNode = nuke.toNode('{SWITCH}')\nfor i in range(switchNode.inputs()):\n if '{NODE}' == switchNode.input(i)['name'].value():\n  switchNode['which'].setValue(i)\n".format(SWITCH= switch.fullName(), NODE= lgtpass[2].name(), GROUP=lgtGroup.fullName(), KNOB= kName)); lgtGroup.addKnob(k)
                        switchKnobs.append(k)
        
                        # Set Expression to correct Multiply Node
                        lgtpass[2]['value'].setExpression('{GROUPNAME}.{KNOBNAME}'.format(GROUPNAME= lgtGroup.fullName(), KNOBNAME= lgtpass[1]))

                    i += 1

                # Secondary Lights Tab
                lgtGroup.addKnob(nuke.Tab_Knob('SECONDARY LIGHTS PASSES \t\t\t\t\t'))
                i = 1
                firstK=True; firstF=True; firstA=True; firstO=False

                dividerKeys=False; dividerFills=False; dividerAny=False;
                for lgtpass in multList:
                    if lgtpass in testList:

                        if 'other' in lgtpass[1]:
                            dividerKeys=True
                            lgtGroup.addKnob(nuke.Text_Knob('\t', '<font color=#408bff>GI</font>', ''))
                        if 'key' in lgtpass[1]:
                            dividerFills=True
                            if firstK==True:
                                if dividerKeys==True:
                                    lgtGroup.addKnob(nuke.Text_Knob('\n', '\n', '\n'))
                                lgtGroup.addKnob(nuke.Text_Knob('\t', '<font color=#ffc400>Keys</font>', ''))
                                firstK=False
                        if 'fill' in lgtpass[1]:
                            dividerAny=True
                            if firstF==True:
                                if dividerFills==True:
                                    lgtGroup.addKnob(nuke.Text_Knob('\n', '\n', '\n'))
                                lgtGroup.addKnob(nuke.Text_Knob('\t', '<font color=#ffc400>Fills</font>', ''))
                                firstF=False
                        if 'any' in lgtpass[1]:
                            if firstA==True:
                                if dividerAny==True:
                                    lgtGroup.addKnob(nuke.Text_Knob('\n', '\n', '\n'))
                                lgtGroup.addKnob(nuke.Text_Knob('\t', '<font color=#ffc400>Others</font>', ''))
                                firstA=False

                        lgtGroup.addKnob(lgtpass[0])
                        lgtGroup[lgtpass[1]].setValue(1)
        
                        # Isolation Button
                        kName = 'display_'+str(lgtpass[1].split('Beauty_')[1].split('mult')[0])
                        k = nuke.PyScript_Knob(kName, '👁️', "k = '{KNOB}'\nlgtGroup = nuke.toNode('{GROUP}')\nfor knob in lgtGroup.knobs():\n if knob == k:\n  lgtGroup[knob].setEnabled(False)\n if not knob == k:\n  lgtGroup[knob].setEnabled(True)\nswitchNode = nuke.toNode('{SWITCH}')\nfor i in range(switchNode.inputs()):\n if '{NODE}' == switchNode.input(i)['name'].value():\n  switchNode['which'].setValue(i)\n".format(SWITCH= switch.fullName(), NODE= lgtpass[2].name(), GROUP=lgtGroup.fullName(), KNOB= kName)); lgtGroup.addKnob(k)
                        switchKnobs.append(k)
        
                        # Set Expression to correct Multiply Node
                        lgtpass[2]['value'].setExpression('{GROUPNAME}.{KNOBNAME}'.format(GROUPNAME= lgtGroup.fullName(), KNOBNAME= lgtpass[1]))

                    i += 1

                lgtGroup.addKnob(nuke.EndTabGroup_Knob())

                # Current Display Dynamic Value
                switchKnobs = [knob.name() for knob in switchKnobs]

                lgtGroup.knob('knobChanged').setValue("n = nuke.thisNode()\nk = nuke.thisKnob()\nswitchKnobs = {KNOBS}\nif not k.name() == 'Displaying' and k.name() in switchKnobs:\n if k.name() == 'AllLights':\n  n['Displaying'].setValue('<b>ALL LIGHTS</b>')\n if not k.name() == 'AllLights':\n  n['Displaying'].setValue('<b>Beauty_'+k.name().split('_')[1]+'</b>')".format(KNOBS=switchKnobs))


            else:
                print 'Selected node is not a Read node'

            return lgtGroup



    ##### SCRIPT  _______________________________________________________________________
    # Get Read Node and Create Lights Group GIZMO

    selectedNode = nuke.selectedNode()

    if selectedNode.inputs() == 1:
        parent = selectedNode.dependencies()[0]
        while parent.Class() != 'Read':
            selectedNode = nuke.toNode(parent.name())
            parent = selectedNode.dependencies()[0]
        selectedNode = nuke.toNode(parent.name())
        selectedNode['selected'].setValue(True)
        
        if parent.Class() != 'Read':
            p1 = ObjectNode(selectedNode['name'].value())
            shuffleLgts = p1.shuffleLgts()   
            grp = nuke.toNode(shuffleLgts.name())
            for each in selectedNode.dependent():
                each.setInput(0, grp)

    if not selectedNode.inputs() and selectedNode.Class() == 'Read':
        p1 = ObjectNode(selectedNode['name'].value())
        shuffleLgts = p1.shuffleLgts()
        grp = nuke.toNode(shuffleLgts.name())
        for each in selectedNode.dependent():
            each.setInput(0, grp)

    else :
        print 'This is not a Read Node : '+selectedNode.name()


shuffleAOV()