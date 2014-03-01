from PyQt4.QtCore import (
    Qt, SIGNAL, QSize, QSettings
)
from PyQt4.QtGui import (
    QWidget, QGridLayout, QSplitter, QTreeView, QTableView,
    QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QCheckBox, QLineEdit,
    QSizePolicy, QComboBox, QLabel, QTextEdit, QStackedWidget, QMessageBox
)

########################################################################
class ConfigDBViewWidget(QWidget):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parentLayoutWidget, parentGridLayout):
        """Constructor"""

        QWidget.__init__(self, parentLayoutWidget)

        self._initUI(parentGridLayout)

        self.comboBox_view.setEditable(False)
        self.group_based_view_index = \
            self.comboBox_view.findText('Group-based View')
        self.channel_based_view_index = \
            self.comboBox_view.findText('Channel-based View')
        self.comboBox_view.setCurrentIndex(self.channel_based_view_index)
        self.on_view_base_change(self.channel_based_view_index)

        self.connect(self.comboBox_view, SIGNAL('currentIndexChanged(int)'),
                     self.on_view_base_change)
        self.connect(self.checkBox_sortable, SIGNAL('stateChanged(int)'),
                     self.on_sortable_state_changed)

    #----------------------------------------------------------------------
    def _initUI(self, parentGridLayout):
        """"""

        self.gridLayout_5 = QGridLayout(self)
        self.gridLayout_5.setMargin(0)
        self.verticalLayout_2 = QVBoxLayout()
        self.stackedWidget = QStackedWidget(self)
        self.page_tree = QWidget()
        self.gridLayout_2 = QGridLayout(self.page_tree)
        self.treeView = QTreeView(self.page_tree)
        self.gridLayout_2.addWidget(self.treeView, 0, 0, 1, 1)
        self.stackedWidget.addWidget(self.page_tree)
        self.page_table = QWidget()
        self.gridLayout = QGridLayout(self.page_table)
        self.tableView = QTableView(self.page_table)
        self.gridLayout.addWidget(self.tableView, 0, 0, 1, 1)
        self.stackedWidget.addWidget(self.page_table)
        self.verticalLayout_2.addWidget(self.stackedWidget)
        self.horizontalLayout = QHBoxLayout()
        spacerItem = QSpacerItem(40, 20,
                                 QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.comboBox_view = QComboBox(self)
        self.comboBox_view.addItem('Group-based View')
        self.comboBox_view.addItem('Channel-based View')
        self.horizontalLayout.addWidget(self.comboBox_view)
        self.pushButton_columns = QPushButton(self)
        self.pushButton_columns.setText('Columns')
        self.horizontalLayout.addWidget(self.pushButton_columns)
        self.checkBox_sortable = QCheckBox(self)
        self.checkBox_sortable.setText('Sortable')
        self.checkBox_sortable.setChecked(False)
        self.horizontalLayout.addWidget(self.checkBox_sortable)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.gridLayout_5.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        parentGridLayout.addWidget(self, 0, 0, 2, 1)

    #----------------------------------------------------------------------
    def on_view_base_change(self, current_comboBox_index):
        """"""

        if current_comboBox_index == self.group_based_view_index:
            page_obj = self.page_tree
        elif current_comboBox_index == self.channel_based_view_index:
            page_obj = self.page_table
        else:
            raise ValueError('Unexpected current ComboBox index: {0:d}'.
                             format(current_comboBox_index))

        self.stackedWidget.setCurrentWidget(page_obj)

    #----------------------------------------------------------------------
    def on_sortable_state_changed(self, state):
        """"""

        if state == Qt.Checked:
            checked = True
        else:
            checked = False

        self.tableView.setSortingEnabled(checked)
