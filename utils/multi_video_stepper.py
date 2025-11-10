import sys
import cv2
from PyQt6 import QtWidgets, QtGui, QtCore


class VideoStepper(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MP4 Frame Comparator (Qt)")

        # video handles
        self.cap1 = None
        self.cap2 = None

        self.total_frames_1 = 0
        self.total_frames_2 = 0
        self.effective_total_frames = 0  # min of the two (when both loaded)

        self.current_frame_idx = 0
        self.playing = False
        self.user_dragging_slider = False

        # cache last frames so we can resize
        self.last_frame_1 = None
        self.last_frame_2 = None

        # --- UI SETUP ---

        # two video labels side by side
        self.image_label_1 = QtWidgets.QLabel("Open video 1 to start")
        self.image_label_1.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.image_label_1.setMinimumSize(320, 240)
        self.image_label_1.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

        self.image_label_2 = QtWidgets.QLabel("Open video 2 to start")
        self.image_label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.image_label_2.setMinimumSize(320, 240)
        self.image_label_2.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

        videos_layout = QtWidgets.QHBoxLayout()
        videos_layout.addWidget(self.image_label_1, stretch=1)
        videos_layout.addWidget(self.image_label_2, stretch=1)

        # buttons
        open1_btn = QtWidgets.QPushButton("Open video 1")
        open1_btn.clicked.connect(lambda: self.open_video(which=1))

        open2_btn = QtWidgets.QPushButton("Open video 2")
        open2_btn.clicked.connect(lambda: self.open_video(which=2))

        prev_btn = QtWidgets.QPushButton("← Prev")
        prev_btn.clicked.connect(self.prev_frame)

        next_btn = QtWidgets.QPushButton("Next →")
        next_btn.clicked.connect(self.next_frame)

        self.play_btn = QtWidgets.QPushButton("Play")
        self.play_btn.clicked.connect(self.toggle_play)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(open1_btn)
        btn_layout.addWidget(open2_btn)
        btn_layout.addWidget(prev_btn)
        btn_layout.addWidget(next_btn)
        btn_layout.addWidget(self.play_btn)

        # info + slider
        self.info_label = QtWidgets.QLabel("Load two videos to compare")

        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider.setEnabled(False)
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)
        self.slider.sliderPressed.connect(self.on_slider_pressed)
        self.slider.sliderReleased.connect(self.on_slider_released)
        self.slider.valueChanged.connect(self.on_slider_changed)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(videos_layout, stretch=1)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.info_label)
        main_layout.addWidget(self.slider)

        # timer for playback
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.play_step)
        self.timer.start(30)

    # ---------- VIDEO LOADING ----------

    def open_video(self, which: int):
        dlg = QtWidgets.QFileDialog(
            self, "Select video", "", "Video Files (*.mp4 *.mov *.mkv *.avi)"
        )
        if not dlg.exec():
            return
        filename = dlg.selectedFiles()[0]

        cap = cv2.VideoCapture(filename)
        if not cap.isOpened():
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Could not open video {which}"
            )
            return

        if which == 1:
            self.cap1 = cap
            self.total_frames_1 = int(self.cap1.get(cv2.CAP_PROP_FRAME_COUNT))
            # reset frame cache 1
            self.last_frame_1 = None
        else:
            self.cap2 = cap
            self.total_frames_2 = int(self.cap2.get(cv2.CAP_PROP_FRAME_COUNT))
            # reset frame cache 2
            self.last_frame_2 = None

        # recompute effective frames (min of the two that exist)
        self.recompute_effective_total_frames()

        # if first time / reloaded, show current frame
        self.current_frame_idx = 0
        self.playing = False
        self.play_btn.setText("Play")
        self.show_current_frame()

    def recompute_effective_total_frames(self):
        frames = []
        if self.cap1 is not None:
            frames.append(self.total_frames_1)
        if self.cap2 is not None:
            frames.append(self.total_frames_2)

        if frames:
            self.effective_total_frames = min(frames)
            # enable slider
            self.slider.setEnabled(True)
            self.slider.setMinimum(0)
            self.slider.setMaximum(max(self.effective_total_frames - 1, 0))
            self.slider.setValue(
                min(self.current_frame_idx, self.effective_total_frames - 1)
            )
        else:
            self.effective_total_frames = 0
            self.slider.setEnabled(False)
            self.slider.setMaximum(0)

    # ---------- SHOWING FRAMES ----------

    def show_current_frame(self):
        """Show current frame index in both videos (if present)."""
        idx = self.current_frame_idx

        if self.cap1 is not None and idx < self.total_frames_1:
            self.last_frame_1 = self.read_frame(self.cap1, idx)
            self.update_display(1)

        if self.cap2 is not None and idx < self.total_frames_2:
            self.last_frame_2 = self.read_frame(self.cap2, idx)
            self.update_display(2)

        # update info
        if self.effective_total_frames > 0:
            self.info_label.setText(f"Frame {idx + 1}/{self.effective_total_frames}")
        else:
            self.info_label.setText("No frames to show")

        # slider pos (if user not dragging)
        if not self.user_dragging_slider and self.effective_total_frames > 0:
            self.slider.setValue(idx)

    def read_frame(self, cap, idx):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        if not ok:
            return None
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

    def update_display(self, which: int):
        """Scale cached frame to label size for given video."""
        if which == 1:
            frame = self.last_frame_1
            label = self.image_label_1
        else:
            frame = self.last_frame_2
            label = self.image_label_2

        if frame is None:
            return

        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qimg = QtGui.QImage(
            frame.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888
        )
        pix = QtGui.QPixmap.fromImage(qimg)
        pix = pix.scaled(
            label.size(),
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )
        label.setPixmap(pix)

    # ---------- RESIZE ----------

    def resizeEvent(self, event):
        # just re-render cached frames to new sizes
        if self.last_frame_1 is not None:
            self.update_display(1)
        if self.last_frame_2 is not None:
            self.update_display(2)
        super().resizeEvent(event)

    # ---------- CONTROLS ----------

    def next_frame(self):
        if self.effective_total_frames == 0:
            return
        if self.current_frame_idx < self.effective_total_frames - 1:
            self.current_frame_idx += 1
            self.show_current_frame()

    def prev_frame(self):
        if self.effective_total_frames == 0:
            return
        if self.current_frame_idx > 0:
            self.current_frame_idx -= 1
            self.show_current_frame()

    def toggle_play(self):
        if self.effective_total_frames == 0:
            return
        self.playing = not self.playing
        self.play_btn.setText("Pause" if self.playing else "Play")

    def play_step(self):
        if self.playing and self.effective_total_frames > 0:
            if self.current_frame_idx < self.effective_total_frames - 1:
                self.current_frame_idx += 1
                self.show_current_frame()
            else:
                # stop at end
                self.playing = False
                self.play_btn.setText("Play")

    # ---------- SLIDER ----------

    def on_slider_pressed(self):
        self.user_dragging_slider = True

    def on_slider_released(self):
        self.user_dragging_slider = False
        val = self.slider.value()
        self.current_frame_idx = val
        self.show_current_frame()

    def on_slider_changed(self, value):
        # optional live scrub — uncomment to preview while dragging:
        # if self.user_dragging_slider:
        #     self.current_frame_idx = value
        #     self.show_current_frame()
        pass


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = VideoStepper()
    win.resize(1100, 600)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
