import sys
from PySide import QtCore, QtGui
import gameUi
from time import sleep as zzz


class Board(QtGui.QMainWindow):
    def __init__(self, numrows=30, numclmns=30):
        super(Board, self).__init__()
        self.ui = gameUi.Ui_MainWindow()
        self.running = 0

        self.prevStatesStack = []
        #
        # l = []
        # for _ in range(numrows):
        #     row = []
        #     for _ in range(numclmns):
        #         row.append(0)
        #     l.append(row)
        #
        # self.lastState = l

        self.ui.setupUi(self)
        self.ui.tickTimeInput.valueChanged.connect(self.setTick)
        self.ui.startButton.clicked.connect(self.start)
        self.ui.stopButton.clicked.connect(self.stop)
        self.ui.resetButton.clicked.connect(self.clearBoard)
        self.ui.fwdButton.clicked.connect(self.manualMove)
        self.ui.bkButton.clicked.connect(self.mvBack)
        self.ui.randFillBtn.clicked.connect(self.randFill)
        self.ui.randFillInput.setValue(88)
        self.setTick()
        self.setupGrid()

    def setupGrid(self, numrows=30, numclmns=30):
        self.gridCellList = []
        for rnum in range(numrows):
            rowList = []
            for cnum in range(numclmns):
                cell = Cell((rnum, cnum))
                self.ui.boardGrid.addWidget(cell, rnum, cnum)
                rowList.append(cell)
            self.gridCellList.append(rowList)

    @QtCore.Slot()
    def setTick(self):
        self.tickTime = self.ui.tickTimeInput.value()
        # print(self.tickTime)

    def start(self):
        self.running = 1
        self.ui.statusBar.showMessage("Running")
        self.processMoves()

    def processMoves(self):
        while self.running:
            self.oneMove()
            for _ in range(20):
                QtCore.QCoreApplication.processEvents()
                zzz(self.tickTime / 20.0)

    def oneMove(self):
        li = []
        lastState = []
        for rnum, row in enumerate(self.gridCellList):
            lii = []
            lsr = []
            for cnum, cell in enumerate(row):
                lsr.append(cell.isLive)
                nlive = self.numLiveNeighbors(rnum, cnum)
                if (nlive < 2) or (nlive > 3):
                    lii.append(0)
                elif nlive == 2:
                    lii.append(cell.isLive)
                elif nlive == 3:
                    lii.append(1)
                    # print(rnum, cnum, nlive)
            li.append(lii)
            lastState.append(lsr)

        for rnum, row in enumerate(li):
            for cnum, val in enumerate(row):
                self.gridCellList[rnum][cnum].setLiveVal(val)

        if len(self.prevStatesStack) > 1000:
            self.prevStatesStack = self.prevStatesStack[1:]
        self.prevStatesStack.append(lastState)

    def returnNeighbors(self, rnum, cnum):
        nbs = []
        # print('rnum, cnum = ', rnum, cnum)
        rstart, rend = -1, 2
        if rnum == 0:
            rstart = 0
        # if rnum == len(self.gridCellList):
        #     rend = 0
        if rnum == len(self.gridCellList) - 1:
            rend = 1

        cstart, cend = -1, 2
        if cnum == 0:
            cstart = 0

        if cnum == len(self.gridCellList[rnum]) - 1:
            cend = 1

        for ri in range(rstart, rend):
            for ci in range(cstart, cend):
                if not (ri == 0 and ci == 0):
                    nbs.append((rnum + ri, cnum + ci))
        # print(nbs)
        return nbs

    def numLiveNeighbors(self, cnum, rnum):
        nbs = self.returnNeighbors(cnum, rnum)
        n = 0
        for t in nbs:
            if self.gridCellList[t[0]][t[1]].isLive:
                n += 1
        return n

    def stop(self):
        self.running = 0
        self.ui.statusBar.showMessage("Paused", 900)

    def manualMove(self):
        self.ui.statusBar.showMessage("Manual mode engaged. Press start to resume auto", 2200)
        self.stop()
        self.oneMove()

    def mvBack(self):
        if self.running == 1:
            self.ui.statusBar.showMessage("Manual mode engaged. Press start to resume auto", 2200)
        self.running = 0
        try:
            grid = self.prevStatesStack.pop()
            for rnum, row in enumerate(grid):
                for cnum, val in enumerate(row):
                    self.gridCellList[rnum][cnum].setLiveVal(val)
        except IndexError:
            self.ui.statusBar.showMessage("No previous moves left!", 2200)


    def clearBoard(self):
        self.running = 0
        self.prevStatesStack = []
        for row in self.gridCellList:
            for cell in row:
                self.ui.boardGrid.removeWidget(cell)
        zzz(.05)
        del self.gridCellList
        self.setupGrid()

    def randFill(self):
        l = []
        from random import randrange

        n = self.ui.randFillInput.value()
        while len(l) < n:
            rnum, cnum = randrange(len(self.gridCellList)), randrange(len(self.gridCellList[0]))
            if tuple((rnum, cnum)) in l:
                continue
            l.append((rnum, cnum))

        self.clearBoard()
        zzz(.05)
        for rnum, cnum in l:
            self.gridCellList[rnum][cnum].setLiveVal(1)


class Cell(QtGui.QWidget):

    csig = QtCore.Signal(int)

    def __init__(self, coords, parent=None):
        super(Cell, self).__init__(parent)
        font = QtGui.QFont()
        font.setFamily("Saab")
        font.setPixelSize(8)
        self.setMinimumHeight(30)
        self.setMaximumHeight(32)
        self.setMinimumWidth(30)
        self.setMaximumWidth(32)
        self.btn = QtGui.QPushButton('..')
        self.btn.setContentsMargins(0, 0, 0, 0)
        self.btn.setMaximumWidth(32)
        self.btn.setMinimumWidth(28)
        self.btn.setMinimumHeight(28)
        self.btn.setMaximumHeight(32)
        self.btn.setStyleSheet('QPushButton {background-color: grey}')
        self.btn.clicked.connect(self.onClickedToggler)
        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.btn)
        self.setContentsMargins(0, 0, 0, 0)
        self.isLive = 0
        self.setLayout(self.layout)

    @QtCore.Slot()
    def onClickedToggler(self):
        self.isLive = (self.isLive + 1) % 2
        self.syncBtnState()

    def setLiveVal(self, val):
        if val in [0, 1]:
            self.isLive = val
            self.syncBtnState()

    def syncBtnState(self):
        if self.isLive:
            self.btn.setText('||')
            self.btn.setStyleSheet('QPushButton {background-color: green}')

        else:
            self.btn.setText('..')
            self.btn.setStyleSheet('QPushButton {background-color: grey}')


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    b = Board()
    b.show()
    sys.exit(app.exec_())
