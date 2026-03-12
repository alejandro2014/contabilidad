import sys

from PySide2.QtCore import Qt
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import QMainWindow, QApplication
from PySide2.QtCharts import QtCharts


class TestChart(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.set0 = QtCharts.QBarSet("Gastos por mes")

        self.set0.append([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

        self.barSeries = QtCharts.QBarSeries()
        self.barSeries.append(self.set0)
        
        self.chart = QtCharts.QChart()
        self.chart.addSeries(self.barSeries)
        self.chart.setTitle("Gastos por mes")

        self.categories = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        self.axisX = QtCharts.QBarCategoryAxis()
        self.axisX.append(self.categories)
        self.chart.setAxisX(self.axisX, self.barSeries)
        #self.axisX.setRange("Jan", "Jun")

        self.axisY = QtCharts.QValueAxis()
        self.chart.setAxisY(self.axisY, self.barSeries)
        self.axisY.setRange(0, 20)

        self.chart.legend().setVisible(False)
        self.chart.legend().setAlignment(Qt.AlignBottom)

        self.chartView = QtCharts.QChartView(self.chart)
        self.chartView.setRenderHint(QPainter.Antialiasing)

        self.setCentralWidget(self.chartView)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = TestChart()
    window.show()
    window.resize(440, 300)

    sys.exit(app.exec_())
