import sys
import xml.dom.minidom


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtSql import *


class EntryEdit(QAbstractItemView):
    STATE_INIT = "INIT"
    STATE_VIEW = "VIEW"
    STATE_EDIT = "EDIT"
    STATE_NEW = "NEW"

    def __init__(self):
        super(EntryEdit, self).__init__()

        nameLabel = QLabel("Name:")
        self.nameLine = QLineEdit()

        addressLabel = QLabel("Address:")
        self.addressText = QTextEdit()

        mainLayout = QGridLayout()
        mainLayout.addWidget(nameLabel, 0, 0)
        mainLayout.addWidget(self.nameLine, 0, 1)
        mainLayout.addWidget(addressLabel, 1, 0, Qt.AlignTop)
        mainLayout.addWidget(self.addressText, 1, 1)

        self.addButton = QPushButton("&Add")
        self.addButton.show()
        self.editButton = QPushButton("&Edit")
        self.editButton.show()
        self.saveButton = QPushButton("&Save")
        self.saveButton.show()
        self.cancelButton = QPushButton("&Cancel")
        self.cancelButton.show()
        self.deleteButton = QPushButton("&Delete")
        self.deleteButton.show()


        self.addButton.clicked.connect(self.addContact)
        self.editButton.clicked.connect(self.editContact)
        self.saveButton.clicked.connect(self.saveContact)
        self.cancelButton.clicked.connect(self.cancelContact)
        self.deleteButton.clicked.connect(self.deleteContact)

        buttonLayout1 = QVBoxLayout()
        buttonLayout1.addWidget(self.addButton, Qt.AlignTop)
        buttonLayout1.addWidget(self.editButton)
        buttonLayout1.addWidget(self.saveButton)
        buttonLayout1.addWidget(self.cancelButton)
        buttonLayout1.addWidget(self.deleteButton)
        buttonLayout1.addStretch()

        mainLayout = QGridLayout()
        mainLayout.addWidget(nameLabel, 0, 0)
        mainLayout.addWidget(self.nameLine, 0, 1)
        mainLayout.addWidget(addressLabel, 1, 0, Qt.AlignTop)
        mainLayout.addWidget(self.addressText, 1, 1)
        mainLayout.addLayout(buttonLayout1, 1, 2)

        self.setLayout(mainLayout)
        self.setWindowTitle("Simple Address Book")

        self.setInitState()

    def setInitState(self):
        #set buttons state
        self.addButton.setEnabled(True)
        self.editButton.setDisabled(True)
        self.saveButton.setDisabled(True)
        self.cancelButton.setDisabled(True)
        self.deleteButton.setDisabled(True)

        #clear fields and disable
        self.nameLine.clear()
        self.nameLine.setDisabled(True)
        self.addressText.clear()
        self.addressText.setDisabled(True)

        self.state = self.STATE_INIT

    def setNewState(self):
        #set buttons state
        self.addButton.setDisabled(True)
        self.editButton.setDisabled(True)
        self.saveButton.setEnabled(True)
        self.cancelButton.setEnabled(True)
        self.deleteButton.setDisabled(True)

        #clear fields and disable
        self.nameLine.clear()
        self.nameLine.setEnabled(True)
        self.addressText.clear()
        self.addressText.setEnabled(True)

        #TODO: create a new record, ready to save?

        self.state = self.STATE_NEW


    def setEditState(self):

        #set buttons state
        self.addButton.setDisabled(True)
        self.editButton.setDisabled(True)
        self.saveButton.setEnabled(True)
        self.cancelButton.setEnabled(True)
        self.deleteButton.setDisabled(True)

        #enable fields
        self.nameLine.setEnabled(True)
        self.addressText.setEnabled(True)

        self.state = self.STATE_EDIT


    def setViewState(self):

        #set buttons state
        self.addButton.setEnabled(True)
        self.editButton.setEnabled(True)
        self.saveButton.setDisabled(True)
        self.cancelButton.setDisabled(True)
        self.deleteButton.setEnabled(True)

        #populate fields, but disabled
        text = self.model().data(self.index)
        self.nameLine.setText(text)
        self.nameLine.setDisabled(True)
        self.addressText.setDisabled(True)

        self.state = self.STATE_VIEW


    def handleGridClicked(self, selected, deselected):

        #TODO: check to see if there is a pending change.  If so, then prompt before changing, and if "no"
        #then return to deselected in grid (somehow)

        indexes = selected.indexes()
        #assuming single row selection
        self.index = indexes[0]
        # 0 is first column.  maybe I can create constants?

        self.setViewState()


    def addContact(self):
        self.setNewState()


    def editContact(self):
        self.setEditState()


    def saveContact(self):

        #grab values
        name = self.nameLine.text()
        address = self.addressText.toPlainText()

        #validate not empty
        if name == "" or address == "":
            QMessageBox.information(self, "Empty Field",
                    "Please enter a name and address.")
            return

        #validate for duplicate names
#        if name in self.contacts:
#            QMessageBox.information(self, "Add Unsuccessful",
#                    "Sorry, \"%s\" is already in your address book." % name)
#            return


        #in STATE_NEW?  then insert new record
        if self.state == self.STATE_NEW:
            rec = self.model().record()
            rec.setValue("first_name", name);
            #rec.setValue("address", address);
            self.model().insertRecord(-1, rec);

            self.tableRef.scrollToBottom()
            self.setInitState()

        #else, assume it's editing existing and save
        else:
            self.model().setData(self.index,name)
            self.model().submit()

            self.setViewState()


    def cancelContact(self):

        #prompt for verification if changes before canceling
        msgBox = QMessageBox()
        msgBox.setText("Sure you want to cancel?")
        msgBox.setModal(True)
        msgBox.setWindowFlags(Qt.WindowStaysOnTopHint)
        msgBox.setInformativeText("Any unsaved modifications will be lost.")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        ret = msgBox.exec_()
        if ret == QMessageBox.No:
            # return to previous state
            return True

        #in STATE_NEW?  return to INIT state
        if self.state == self.STATE_NEW:
            self.setInitState()

        #else, assume it's editing and return to VIEW state
        else:
            self.setViewState()



    def deleteContact(self):

        #prompt for verification before deleting
        msgBox = QMessageBox()
        msgBox.setText("Sure you want to delete?")
        msgBox.setModal(True)
        msgBox.setWindowFlags(Qt.WindowStaysOnTopHint)
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        ret = msgBox.exec_()
        if ret == QMessageBox.No:
            # return to previous state
            return True

        self.model().removeRows(self.index.row(),1)
        self.model().submit()

        self.tableRef.hideRow(self.index.row())

        self.setInitState()


    def createKML(self):

        #TODO: need to get fileName via file browser
        fileName = "/Users/bkrouse/PycharmProjects/directorymap/sample.KML"

        #TODO: maybe need a pending processing indicator?

        # This constructs the KML document from the CSV file.
        kmlDoc = xml.dom.minidom.Document()

        kmlElement = kmlDoc.createElementNS('http://earth.google.com/kml/2.2', 'kml')
        kmlElement.setAttribute('xmlns', 'http://www.opengis.net/kml/2.2')
        kmlElement.setAttribute('xmlns:gx', 'http://www.google.com/kml/ext/2.2')
        kmlElement.setAttribute('xmlns:kml', 'http://www.opengis.net/kml/2.2')
        kmlElement.setAttribute('xmlns:atom', 'http://www.w3.org/2005/Atom')
        kmlElement = kmlDoc.appendChild(kmlElement)

        kmlFolder = kmlDoc.createElement("Folder")
        kmlFolder = kmlElement.appendChild(kmlFolder)
        nameElement = kmlDoc.createElement('name')
        nameElement.appendChild(kmlDoc.createTextNode('My Places'))
        kmlFolder.appendChild(nameElement)
        openElement = kmlDoc.createElement('open')
        openElement.appendChild(kmlDoc.createTextNode('1'))
        kmlFolder.appendChild(openElement)


        for i in range(0, self.model().rowCount()):
            self.createKMLEntry(kmlDoc, kmlFolder, self.model().record(i))


        kmlFile = open(fileName, 'wb')
        kmlFile.write(kmlDoc.toprettyxml(encoding="UTF-8"))



        msgBox = QMessageBox()
        msgBox.setText("Created KML successfully.")
        msgBox.exec()


    def createKMLEntry(self, kmlDoc, kmlFolder, record):

        personName = record.field("first_name").value() + " " + record.field("last_name").value()

        kmlFileName = personName + '.kml'
        nameAndPosition = personName + ' - Fellow, Researcher'
        descriptionText = "Bunch of <b>description text</b>"
        coordsStr = '-122.1226561806599,47.67504299735445,0'
        longitude = '-122.1222145437816'
        latitude = '47.67511545561167'
        altitude = '0'
        heading = '0.0005234466212885948'
        tilt = '0'
        xrange = '247.266752558574'


        documentElement = kmlDoc.createElement('Document')
        documentElement = kmlFolder.appendChild(documentElement)

        nameElement = kmlDoc.createElement('name')
        nameElement.appendChild(kmlDoc.createTextNode(kmlFileName))
        documentElement.appendChild(nameElement)

        styleElement = kmlDoc.createElement('Style')
        styleElement.setAttribute('id', 'sn_woman')
        documentElement.appendChild(styleElement)
        iconStyleElement = kmlDoc.createElement('IconStyle')
        styleElement.appendChild(iconStyleElement)
        colorElement = kmlDoc.createElement('color')
        colorElement.appendChild(kmlDoc.createTextNode('ffffaa00'))
        iconStyleElement.appendChild(colorElement)
        scaleElement = kmlDoc.createElement('scale')
        scaleElement.appendChild(kmlDoc.createTextNode('1.2'))
        iconStyleElement.appendChild(scaleElement)
        iconElement = kmlDoc.createElement('Icon')
        iconStyleElement.appendChild(iconElement)
        hrefElement = kmlDoc.createElement('href')
        hrefElement.appendChild(kmlDoc.createTextNode('http://maps.google.com/mapfiles/kml/shapes/woman.png'))
        iconElement.appendChild(hrefElement)
        listStyleElement = kmlDoc.createElement('ListStyle')
        styleElement.appendChild(listStyleElement)

        styleElement = kmlDoc.createElement('Style')
        styleElement.setAttribute('id', 'sh_woman')
        documentElement.appendChild(styleElement)
        iconStyleElement = kmlDoc.createElement('IconStyle')
        styleElement.appendChild(iconStyleElement)
        colorElement = kmlDoc.createElement('color')
        colorElement.appendChild(kmlDoc.createTextNode('ffffaa00'))
        iconStyleElement.appendChild(colorElement)
        scaleElement = kmlDoc.createElement('scale')
        scaleElement.appendChild(kmlDoc.createTextNode('1.4'))
        iconStyleElement.appendChild(scaleElement)
        iconElement = kmlDoc.createElement('Icon')
        iconStyleElement.appendChild(iconElement)
        hrefElement = kmlDoc.createElement('href')
        hrefElement.appendChild(kmlDoc.createTextNode('http://maps.google.com/mapfiles/kml/shapes/woman.png'))
        iconElement.appendChild(hrefElement)
        listStyleElement = kmlDoc.createElement('ListStyle')
        styleElement.appendChild(listStyleElement)

        styleMapElement = kmlDoc.createElement('StyleMap')
        styleMapElement.setAttribute('id', 'msn_woman')
        documentElement.appendChild(styleMapElement)
        pairElement = kmlDoc.createElement('Pair')
        styleMapElement.appendChild(pairElement)
        keyElement = kmlDoc.createElement('key')
        keyElement.appendChild(kmlDoc.createTextNode('normal'))
        pairElement.appendChild(keyElement)
        styleUrlElement = kmlDoc.createElement('styleUrl')
        styleUrlElement.appendChild(kmlDoc.createTextNode('#sn_woman'))
        pairElement.appendChild(styleUrlElement)
        pairElement = kmlDoc.createElement('Pair')
        styleMapElement.appendChild(pairElement)
        keyElement = kmlDoc.createElement('key')
        keyElement.appendChild(kmlDoc.createTextNode('highlight'))
        pairElement.appendChild(keyElement)
        styleUrlElement = kmlDoc.createElement('styleUrl')
        styleUrlElement.appendChild(kmlDoc.createTextNode('#sh_woman'))
        pairElement.appendChild(styleUrlElement)

        placemarkElement = kmlDoc.createElement('Placemark')
        documentElement.appendChild(placemarkElement)
        nameElement = kmlDoc.createElement('name')
        nameElement.appendChild(kmlDoc.createTextNode(nameAndPosition))
        placemarkElement.appendChild(nameElement)
        descriptionElement = kmlDoc.createElement('description')
        descriptionElement.appendChild(kmlDoc.createCDATASection(str(descriptionText)))
        placemarkElement.appendChild(descriptionElement)

        lookAtElement = kmlDoc.createElement('LookAt')
        placemarkElement.appendChild(lookAtElement)
        longitudeElement = kmlDoc.createElement('longitude')
        longitudeElement.appendChild(kmlDoc.createTextNode(longitude))
        lookAtElement.appendChild(longitudeElement)
        latitudeElement = kmlDoc.createElement('latitude')
        latitudeElement.appendChild(kmlDoc.createTextNode(latitude))
        lookAtElement.appendChild(latitudeElement)
        altitudeElement = kmlDoc.createElement('altitude')
        altitudeElement.appendChild(kmlDoc.createTextNode(altitude))
        lookAtElement.appendChild(altitudeElement)
        headingElement = kmlDoc.createElement('heading')
        headingElement.appendChild(kmlDoc.createTextNode(heading))
        lookAtElement.appendChild(headingElement)
        tiltElement = kmlDoc.createElement('tilt')
        tiltElement.appendChild(kmlDoc.createTextNode(tilt))
        lookAtElement.appendChild(tiltElement)
        rangeElement = kmlDoc.createElement('range')
        rangeElement.appendChild(kmlDoc.createTextNode(xrange))
        lookAtElement.appendChild(rangeElement)
        altitudeModeElement = kmlDoc.createElement('altitudeMode')
        altitudeModeElement.appendChild(kmlDoc.createTextNode('relativeToGround'))
        lookAtElement.appendChild(altitudeModeElement)
        gxaltitudeModeElement = kmlDoc.createElement('gx:altitudeMode')
        gxaltitudeModeElement.appendChild(kmlDoc.createTextNode('relativeToSeaFloor'))
        lookAtElement.appendChild(gxaltitudeModeElement)

        styleUrlElement = kmlDoc.createElement('styleUrl')
        styleUrlElement.appendChild(kmlDoc.createTextNode('#msn_woman'))
        placemarkElement.appendChild(styleUrlElement)

        pointElement = kmlDoc.createElement('Point')
        placemarkElement.appendChild(pointElement)
        altitudeModeElement = kmlDoc.createElement('altitudeMode')
        altitudeModeElement.appendChild(kmlDoc.createTextNode('clampToGround'))
        pointElement.appendChild(altitudeModeElement)
        gxaltitudeModeElement = kmlDoc.createElement('gx:altitudeMode')
        gxaltitudeModeElement.appendChild(kmlDoc.createTextNode('clampToSeaFloor'))
        pointElement.appendChild(gxaltitudeModeElement)
        coordinatesElement = kmlDoc.createElement('coordinates')
        coordinatesElement.appendChild(kmlDoc.createTextNode(coordsStr))
        pointElement.appendChild(coordinatesElement)





class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        #add some menus here later maybe

        self.setupModel()
        self.setupViews()

        self.setWindowTitle("Directory Map")
        self.resize(800, 600)


    def setupModel(self):
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("people.db")
        db.open()

        self.model = QSqlTableModel(self, db)

        # My TransQry function takes parameters and returns a SQL query using the parameters as criteria for filtering my 'transactions' table.

        self.model.setTable("people")
        self.model.setEditStrategy(QSqlTableModel.OnRowChange)
        self.model.select()

        # Remember the indexes of the columns
        #authorIdx = model->fieldIndex("author");
        #genreIdx = model->fieldIndex("genre");



    def setupViews(self):
        splitter = QSplitter(Qt.Vertical)

        table = QTableView()
        table.setModel(self.model)
        #table.hideColumn(0)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()

        editor = EntryEdit()
        editor.setModel(self.model)

        selectionModel = QItemSelectionModel(self.model)
        table.setSelectionModel(selectionModel)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        editor.setSelectionModel(selectionModel)
        selectionModel.selectionChanged.connect(editor.handleGridClicked)

        #temp: this would be better done with signaling...but this will do
        editor.tableRef = table

        splitter.addWidget(table)
        splitter.addWidget(editor)
        splitter.setStretchFactor(0,0)
        splitter.setStretchFactor(1,1)

        self.setCentralWidget(splitter)

        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(QAction("&Create KML", self,
                statusTip="Create KML", triggered=editor.createKML))
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(QAction("E&xit", self, shortcut="Ctrl+Q",
                statusTip="Exit the application", triggered=self.close))




def main():
    app = QApplication(sys.argv)
#    window = DqTableForm()
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

