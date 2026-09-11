import sys
from pylsl import resolve_byprop, StreamInlet
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                               QWidget, QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import QThread, Signal, Slot, Qt
import numpy as np

class LSLWorker(QThread):
    # Emit both the timestamp (float) and the marker (string)
    data_received = Signal(float, object)

    def run(self):
        print("Looking for a 'Markers' stream...")
        streams = resolve_byprop('type', 'Markers')
        
        if not streams:
            print("No streams found.")
            return

        inlet = StreamInlet(streams[0])
        print("Connected to stream!")

        while not self.isInterruptionRequested():
            # timeout ensures the thread checks for interruption requests smoothly
            sample, timestamp = inlet.pull_sample(timeout=1.0)
            if sample is not None:
                # sample is a list with marker data
                self.data_received.emit(timestamp, sample)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LSL Event Log")
        self.resize(500, 400)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Set up a 0-row, 2-column table
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Timestamp", "LSL Output"])
        
        # Adjust column widths: Timestamp fits to content, LSL Output stretches to fill remaining space
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        layout.addWidget(self.table)
        self.setCentralWidget(central_widget)

        # Initialize and start the LSL worker
        self.lsl_thread = LSLWorker()
        self.lsl_thread.data_received.connect(self.append_row)
        self.lsl_thread.start()

    @Slot(float, object)
    def append_row(self, timestamp, marker):
        # Get the current number of rows to append to the very end
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        
        # Format the timestamp for clean readability
        ts_item = QTableWidgetItem(f"{timestamp:.4f}")
        
        # Handle marker as list or single value
        if isinstance(marker, list):
            marker_text = ', '.join(str(m) for m in marker)
        else:
            marker_text = str(marker)
        marker_item = QTableWidgetItem(marker_text)
        
        # Optional: Center the timestamp, left-align the string
        ts_item.setTextAlignment(Qt.AlignCenter)
        marker_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Add items to the new row
        self.table.setItem(row_position, 0, ts_item)
        self.table.setItem(row_position, 1, marker_item)
        
        # Auto-scroll to the bottom as new rows are added
        self.table.scrollToBottom()

    def closeEvent(self, event):
        # Clean up the thread
        self.lsl_thread.requestInterruption()
        self.lsl_thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())