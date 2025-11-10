import sys
import cv2
from PyQt6 import QtWidgets, QtGui, QtCore


class VideoStepper(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MP4 Frame Stepper (Qt)")
        self.cap = None
        self.total_frames = 0
        self.current_frame_idx = 0
        self.playing = False
        self.user_dragging_slider = False  # to avoid jitter while dragging
        self.last_frame = None  # cache the last frame image

        # main video display
        self.image_label = QtWidgets.QLabel("Open a video to start")
        self.image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(640, 360)
        self.image_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

        # buttons
        open_btn = QtWidgets.QPushButton("Open video")
        open_btn.clicked.connect(self.open_video)

        prev_btn = QtWidgets.QPushButton("← Prev")
        prev_btn.clicked.connect(self.prev_frame)

        next_btn = QtWidgets.QPushButton("Next →")
        next_btn.clicked.connect(self.next_frame)

        self.play_btn = QtWidgets.QPushButton("Play")
        self.play_btn.clicked.connect(self.toggle_play)

        # info label
        self.info_label = QtWidgets.QLabel("No video loaded")

        # slider
        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider.setEnabled(False)
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)
        self.slider.sliderPressed.connect(self.on_slider_pressed)
        self.slider.sliderReleased.connect(self.on_slider_released)
        self.slider.valueChanged.connect(self.on_slider_changed)

        # layout
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(open_btn)
        btn_layout.addWidget(prev_btn)
        btn_layout.addWidget(next_btn)
        btn_layout.addWidget(self.play_btn)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.image_label, stretch=1)
        layout.addLayout(btn_layout)
        layout.addWidget(self.info_label)
        layout.addWidget(self.slider)

        # timer for playback
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.play_step)
        self.timer.start(30)

    def open_video(self):
        dlg = QtWidgets.QFileDialog(
            self, "Select MP4", "", "Video Files (*.mp4 *.mov *.mkv *.avi)"
        )
        if dlg.exec():
            filename = dlg.selectedFiles()[0]
        else:
            return

        cap = cv2.VideoCapture(filename)
        if not cap.isOpened():
            QtWidgets.QMessageBox.critical(self, "Error", "Could not open video")
            return

        self.cap = cap
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.current_frame_idx = 0
        self.playing = False
        self.play_btn.setText("Play")

        # configure slider
        self.slider.setEnabled(True)
        self.slider.setMinimum(0)
        self.slider.setMaximum(max(self.total_frames - 1, 0))
        self.slider.setValue(0)

        self.show_frame(self.current_frame_idx)

    def show_frame(self, idx):
        if self.cap is None:
            return

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = self.cap.read()
        if not ok:
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.last_frame = frame  # store frame for resize events
        self.update_display()

        self.info_label.setText(f"Frame {idx + 1}/{self.total_frames}")
        if not self.user_dragging_slider:
            self.slider.setValue(idx)

    def update_display(self):
        """Render the cached frame scaled to the current label size."""
        if self.last_frame is None:
            return
        frame = self.last_frame
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qimg = QtGui.QImage(
            frame.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888
        )
        pix = QtGui.QPixmap.fromImage(qimg)
        pix = pix.scaled(
            self.image_label.size(),
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )
        self.image_label.setPixmap(pix)

    def resizeEvent(self, event):
        """Redraw the current frame when window is resized."""
        self.update_display()
        super().resizeEvent(event)

    def next_frame(self):
        if self.cap and self.current_frame_idx < self.total_frames - 1:
            self.current_frame_idx += 1
            self.show_frame(self.current_frame_idx)

    def prev_frame(self):
        if self.cap and self.current_frame_idx > 0:
            self.current_frame_idx -= 1
            self.show_frame(self.current_frame_idx)

    def toggle_play(self):
        if not self.cap:
            return
        self.playing = not self.playing
        self.play_btn.setText("Pause" if self.playing else "Play")

    def play_step(self):
        if self.playing and self.cap:
            if self.current_frame_idx < self.total_frames - 1:
                self.current_frame_idx += 1
                self.show_frame(self.current_frame_idx)
            else:
                self.playing = False
                self.play_btn.setText("Play")

    def on_slider_pressed(self):
        self.user_dragging_slider = True

    def on_slider_released(self):
        self.user_dragging_slider = False
        self.current_frame_idx = self.slider.value()
        self.show_frame(self.current_frame_idx)

    def on_slider_changed(self, value):
        pass


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = VideoStepper()
    win.resize(800, 600)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
