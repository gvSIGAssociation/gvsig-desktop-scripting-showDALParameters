# encoding: utf-8

import gvsig

from gvsig import getResource
from gvsig.libs.formpanel import FormPanel, load_icon
from gvsig.commonsdialog import msgbox

from StringIO import StringIO

from org.gvsig.tools import ToolsLocator
from org.gvsig.tools.dataTypes import DataTypes
from org.gvsig.tools.swing.api import ToolsSwingLocator
from org.gvsig.fmap.dal import DALLocator
from org.gvsig.tools.swing.api.windowmanager import WindowManager_v2

from java.awt.event import ActionListener
from javax.swing import DefaultComboBoxModel
from javax.swing.table import DefaultTableModel
from javax.swing import ListSelectionModel


class ParametersTableMode(DefaultTableModel):
  def __init__(self,parameters):
    DefaultTableModel.__init__(self)
    self.parameters = parameters
    self.parametersType = list()
    self.parametersType.extend(parameters.getDynClass().getDynFields())
    self.parametersType.sort(lambda x,y: cmp(x.getName().lower(),y.getName().lower()))
    self.columns = ("Name", "Type", "Default", "Description")
    self.dataTypesManager = ToolsLocator.getDataTypesManager()

  def getParametersType(self):
    return self.parametersType
    
  def getRowCount(self):
    try:
      return len(self.parametersType)
    except:
      return 0 #Se llama en el constructor antes de que se haya recogido.
    
  def getColumnCount(self):
    return len(self.columns)

  def getColumnName(self,index):
    return self.columns[index]

  def getValueAt(self, row, column):
    field = self.parametersType[row]
    if column == 0:
      return field.getName()
    if column == 1:
      return  self.dataTypesManager.getTypeName(field.getType())
    if column == 2:
      return field.getDefaultValue()
    if column == 3:
      return field.getDescription()
    
class ShowDALParameters(FormPanel):
  def __init__(self):
    FormPanel.__init__(self,getResource(__file__,"showDALParameters.xml"))
    self.initComponents()

  def initComponents(self):
    self.setPreferredSize(500,300)

    self.tableStoreParameters.setRowSelectionAllowed(True)
    self.tableStoreParameters.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION)
    
    self.tableExplorerParameters.setRowSelectionAllowed(True)
    self.tableExplorerParameters.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION)
    
    model = DefaultComboBoxModel()
    manager = DALLocator.getDataManager()
    for providerName in manager.getStoreProviders():
        model.addElement(providerName)
    self.cboStoreProviderNames.setModel(model)
    self.cboStoreProviderNames.setSelectedIndex(0)
    self.cboStoreProviderNames_change(None)
    
    model = DefaultComboBoxModel()
    manager = DALLocator.getDataManager()
    for providerName in manager.getExplorerProviders():
        model.addElement(providerName)
    self.cboExplorerProviderNames.setModel(model)
    self.cboExplorerProviderNames.setSelectedIndex(0)
    self.cboExplorerProviderNames_change(None)
    
  def cboStoreProviderNames_change(self,*args):
    providerName = self.cboStoreProviderNames.getSelectedItem()
    if providerName in ("",None):
      return
    manager = DALLocator.getDataManager()
    parameters = manager.createStoreParameters(providerName)
    model = ParametersTableMode(parameters)
    self.tableStoreParameters.setModel(model)
    
  def cboExplorerProviderNames_change(self,*args):
    providerName = self.cboExplorerProviderNames.getSelectedItem()
    if providerName in ("",None):
      return
    manager = DALLocator.getDataManager()
    parameters = manager.createServerExplorerParameters(providerName)
    model = ParametersTableMode(parameters)
    self.tableExplorerParameters.setModel(model)

  def btnStoreShowExampleCode_click(self,*args):
    rows = self.tableStoreParameters.getSelectedRows()
    if len(rows)==0:
      msgbox("Select any rows to use this utility")
      return
    providerName = self.cboStoreProviderNames.getSelectedItem()
    if providerName in ("",None):
      msgbox("Select a data proviver to use this utility")
      return
    parametersType = self.tableStoreParameters.getModel().getParametersType()
    code = StringIO()
    code.write('DataManager manager = DALLocator.getDataManager();\n')
    code.write('DataParameters storeParameters = manager.createStoreParameters("%s");\n' % providerName)
    for n in rows:
      field = parametersType[n]
      datatype = field.getDataType()
      value = field.getDefaultValue()
      if value == None:
          code.write('storeParameters.setDynValue("%s",null);\n' % (field.getName()))
      else:
        if datatype.isNumeric():
          code.write('storeParameters.setDynValue("%s",%s);\n' % (field.getName(), value))
        elif datatype.isContainer() or datatype.isObject() or datatype.isDynObject():
          code.write('storeParameters.setDynValue("%s",null);\n' % (field.getName()))
        elif datatype.getType() == DataTypes.STRING:
          code.write('storeParameters.setDynValue("%s","%s");\n' % (field.getName(), value))
        elif datatype.getType() == DataTypes.BOOLEAN:
          code.write('storeParameters.setDynValue("%s",%s);\n' % (field.getName(), str(value).lower()))
        else:
          print "???"
    code.write('DataStore store = manager.openStore("%s",storeParameters);\n' % providerName)
    self.txtStoreExampleCode.setText(code.getvalue())
    code.close()


  def btnExplorerShowExampleCode_click(self,*args):
    rows = self.tableExplorerParameters.getSelectedRows()
    if len(rows)==0:
      msgbox("Select any rows to use this utility")
      return
    providerName = self.cboExplorerProviderNames.getSelectedItem()
    if providerName in ("",None):
      msgbox("Select a data proviver to use this utility")
      return
    parametersType = self.tableExplorerParameters.getModel().getParametersType()
    code = StringIO()
    code.write('DataManager manager = DALLocator.getDataManager();\n')
    code.write('DataServerExplorerParameters serverParameters = manager.createServerExplorerParameters("%s");\n' % providerName)
    for n in rows:
      field = parametersType[n]
      datatype = field.getDataType()
      value = field.getDefaultValue()
      if value == None:
          code.write('serverParameters.setDynValue("%s",null);\n' % (field.getName()))
      else:
        if datatype.isNumeric():
          code.write('serverParameters.setDynValue("%s",%s);\n' % (field.getName(), value))
        elif datatype.isContainer() or datatype.isObject() or datatype.isDynObject():
          code.write('serverParameters.setDynValue("%s",null);\n' % (field.getName()))
        elif datatype.getType() == DataTypes.STRING:
          code.write('serverParameters.setDynValue("%s","%s");\n' % (field.getName(), value))
        elif datatype.getType() == DataTypes.BOOLEAN:
          code.write('serverParameters.setDynValue("%s",%s);\n' % (field.getName(), str(value).lower()))
        else:
          print "???"
    code.write('DataServerExplorer serverExplorer = manager.openServerExplorer("%s",serverParameters);\n' % providerName)
    self.txtExplorerExampleCode.setText(code.getvalue())
    code.close()
        
  def showWindow(self,title=None, mode=WindowManager_v2.MODE.WINDOW):
    if title == None:
      title = "Show DAL parameters"
    dialog = ToolsSwingLocator.getWindowManager().createDialog(
        self.asJComponent(),
        title,
        "Show DAL parameters for the selected provider",
        WindowManager_v2.BUTTON_OK
    )
    dialog.show(mode)
    
def main(*args):
  dlg = ShowDALParameters()
  dlg.showWindow()
