#-----------------------------------------------------------
# Copyright (C) 2021 Ben Wirf
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox

from qgis.core import QgsProject, QgsVectorLayer, Qgis

def classFactory(iface):
    return StylePolice(iface)


class StylePolice:
    def __init__(self, iface):
        self.iface = iface
        self.msg = QMessageBox()
#        self.count = 0
        self.project = QgsProject.instance()
        self.existing_project_layers = [l for l in self.project.mapLayers()]
        self.signal_1_connected = False
#        self.signal_2_connected = False
#        self.iface.messageBar().pushMessage('init called')
        self.existing_layers = None
        self.mb_text = 'One or more added layers were automatically styled by\
        the "Style Police" plugin!'

    def initGui(self):
#        self.iface.messageBar().pushMessage('initGui called')
        self.existing_layers = []
        if not self.signal_1_connected:
            self.project.layersAdded.connect(self.layers_added)
            self.project.readMapLayer.connect(self.layer_read)
            self.signal_1_connected = True
        self.iface.newProjectCreated.connect(self.new_project)
        self.iface.projectRead.connect(self.new_project)

    def unload(self):
        pass

    def new_project(self):
        # clearing list in this this method is occurring after the layer_read
        # slot is called!!
        project_layers = [l for l in self.project.mapLayers().values()]
        # only clear list if stored layers don't belong to current project!
        if self.existing_layers != project_layers:
            self.existing_layers.clear()
        if self.signal_1_connected:
            self.project.layersAdded.disconnect(self.layers_added)
            self.project.readMapLayer.disconnect(self.layer_read)
            self.signal_1_connected = False

        self.project = QgsProject.instance()

        if not self.signal_1_connected:
            self.project.layersAdded.connect(self.layers_added)
            self.project.readMapLayer.connect(self.layer_read)
            self.signal_1_connected = True
    
            
    def layer_read(self, layer):
        '''Creates a list of existing project layers read from the project
        file. This allows existing layers to be handled and ignored by the
        slot function which is connected to the layersAdded() signal'''
        self.existing_layers.append(layer)
###########################################################################
    def layer_removed(self, layer_list):
        '''If one of the original layers is removed from the project, we
        should also remove it from the existing_layers list'''
        for l in layer_list:
            if l in self.existing_layers:
                self.existing_layers.remove(l)
###########################################################################

    def layers_added(self, layer_list):
        # Make sure layer is not an existing layer in the project. We only want
        # newly added layers (after project has been opened) to be affected.
        new_layers = [l for l in layer_list if l not in self.existing_layers]
        if new_layers:
            for lyr in new_layers:
                if isinstance(lyr, QgsVectorLayer):
                    if lyr.geometryType() == 2:
                        renderer = lyr.renderer().clone()
                        sym = renderer.symbol().symbolLayer(0)
                        sym.setFillColor(QColor(0,0,0,0))
                        sym.setStrokeWidth(0.5)
                        lyr.setRenderer(renderer)
                        lyr.triggerRepaint()
                        self.iface.layerTreeView().refreshLayerSymbology(lyr.id())
            mb_items = self.iface.messageBar().items()
            if not mb_items or False not in [i.text()!=self.mb_text for i in mb_items if mb_items]:
                self.iface.messageBar().pushMessage(self.mb_text, Qgis.Info, 5)
#        self.msg.setText(str(new_layers))
#        self.msg.show()
