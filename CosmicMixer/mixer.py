from __future__ import annotations

import argparse
import os
import shutil
import sys
from importlib.resources import as_file, files

import pulsectl
import sass
from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR, Qt, QTimer
from PyQt6.QtGui import QCursor, QFontMetrics, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

CONFIG_ROOT = os.path.expanduser("~/.config/cosmic-mixer")
THEME_DIR = os.path.join(CONFIG_ROOT, "themes")


def log(msg: str) -> None:
    print(f"[cosmic-mixer] {msg}", file=sys.stderr)


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def get_packaged_palette() -> str:
    resource = files("CosmicMixer.themes.palettes").joinpath("cosmic.scss")
    with as_file(resource) as p:
        return str(p)


def get_packaged_base() -> str:
    resource = files("CosmicMixer.themes").joinpath("base.scss")
    with as_file(resource) as p:
        return str(p)


def get_packaged_theme_dir() -> str:
    resource = files("CosmicMixer.themes")
    with as_file(resource) as p:
        return str(p)


def compile_scss_file(scss_path: str, css_path: str) -> bool:
    try:
        compiled_css = sass.compile(
            filename=scss_path,
            include_paths=[
                THEME_DIR,
                get_packaged_theme_dir(),
            ],
        )
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(compiled_css)
        log(f"compiled theme: {scss_path} -> {css_path}")
        return True
    except Exception as e:
        log(f"failed to compile SCSS '{scss_path}': {e}")
        return False


def seed_default_theme(force: bool = False) -> None:
    ensure_dir(CONFIG_ROOT)

    from importlib.resources import files, as_file

    packaged = files("CosmicMixer.themes")

    with as_file(packaged) as packaged_dir:
        packaged_dir = str(packaged_dir)

        if force:
            if os.path.exists(THEME_DIR):
                shutil.rmtree(THEME_DIR)

        if not os.path.exists(THEME_DIR):
            shutil.copytree(packaged_dir, THEME_DIR)
            log(f"default themes seeded -> {THEME_DIR}")
            return

        # themes dir exists, but structure may be incomplete
        palettes_dir = os.path.join(THEME_DIR, "palettes")

        if not os.path.exists(palettes_dir):
            src_palettes = os.path.join(packaged_dir, "palettes")
            shutil.copytree(src_palettes, palettes_dir)
            log("palettes directory restored")

        base_src = os.path.join(packaged_dir, "base.scss")
        base_dst = os.path.join(THEME_DIR, "base.scss")

        if not os.path.exists(base_dst):
            shutil.copy(base_src, base_dst)
            log("base.scss restored")

def compile_all_user_themes() -> None:
    palette_dir = os.path.join(THEME_DIR, "palettes")

    if not os.path.isdir(palette_dir):
        log("palette directory missing")
        return

    for file_name in os.listdir(palette_dir):
        if not file_name.endswith(".scss"):
            continue

        scss_path = os.path.join(palette_dir, file_name)

        css_name = file_name.replace(".scss", ".css")
        css_path = os.path.join(THEME_DIR, css_name)

        compile_scss_file(scss_path, css_path)


def setup_user_configs(force_theme: bool = False) -> None:
    seed_default_theme(force_theme)
    compile_all_user_themes()


def load_packaged_logo(size: int = 72) -> QPixmap | None:
    try:
        logo_resource = files("CosmicMixer.assets").joinpath("cosmic_logo.png")
        with as_file(logo_resource) as logo_path:
            pixmap = QPixmap(str(logo_path))
            if pixmap.isNull():
                log("logo file was found but QPixmap failed to load it")
                return None

            return pixmap.scaled(
                size,
                size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

    except Exception as e:
        log(f"failed to load packaged logo: {e}")
        return None


def load_packaged_icon() -> QIcon | None:
    try:
        logo_resource = files("CosmicMixer.assets").joinpath("cosmic_logo.png")
        with as_file(logo_resource) as logo_path:
            return QIcon(str(logo_path))

    except Exception as e:
        log(f"failed to load packaged icon: {e}")
        return None


class VolumeMixer(QWidget):
    def __init__(self, theme_path: str):
        super().__init__()

        self.pulse = pulsectl.Pulse("cosmic-mixer")
        self.stream_ids: set[int] = set()
        self.is_armed = False

        self.close_timer = QTimer(self)
        self.close_timer.setSingleShot(True)
        self.close_timer.timeout.connect(self.final_close_check)

        self.setObjectName("MainWin")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setFixedWidth(450)
        self.setFixedHeight(650)

        log(f"Python: {sys.version.split()[0]}")
        log(f"PyQt: {PYQT_VERSION_STR}")
        log(f"Qt: {QT_VERSION_STR}")
        log(f"theme file requested: {theme_path}")

        icon = load_packaged_icon()
        if icon is not None:
            self.setWindowIcon(icon)

        if os.path.exists(theme_path):
            try:
                with open(theme_path, "r", encoding="utf-8") as f:
                    css = f.read()

                if css.strip():
                    self.setStyleSheet(css)
                    log(f"applied theme CSS: {theme_path}")
                else:
                    log(f"theme CSS exists but is empty: {theme_path}")
            except Exception as e:
                log(f"failed to read/apply theme CSS '{theme_path}': {e}")
        else:
            log(f"theme CSS does not exist: {theme_path}")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(14, 10, 14, 14)
        self.main_layout.setSpacing(6)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 2)
        header_row.setSpacing(10)

        header_row.addStretch()

        logo = load_packaged_logo(72)
        if logo is not None:
            logo_label = QLabel()
            logo_label.setObjectName("LogoLabel")
            logo_label.setPixmap(logo)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            header_row.addWidget(logo_label)

        title = QLabel("COSMIC MIXER")
        title.setProperty("class", "MasterTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        header_row.addWidget(title)

        header_row.addStretch()

        self.main_layout.addLayout(header_row)

        sep = QWidget()
        sep.setObjectName("HeaderSeparator")
        sep.setFixedHeight(1)
        self.main_layout.addWidget(sep)

        self.global_out = QComboBox()
        self.global_in = QComboBox()
        self.global_out.setObjectName("GlobalOutput")
        self.global_in.setObjectName("GlobalInput")
        self.global_out.currentIndexChanged.connect(self.set_global_output)
        self.global_in.currentIndexChanged.connect(self.set_global_input)

        out_label = QLabel("GLOBAL OUTPUT")
        out_label.setProperty("class", "SectionLabel")
        in_label = QLabel("GLOBAL INPUT")
        in_label.setProperty("class", "SectionLabel")

        self.main_layout.addWidget(out_label)
        self.main_layout.addWidget(self.global_out)
        self.main_layout.addWidget(in_label)
        self.main_layout.addWidget(self.global_in)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search streams...")
        self.search_bar.setObjectName("SearchBar")
        self.search_bar.textChanged.connect(self.refresh_streams)
        self.main_layout.addWidget(self.search_bar)

        sink = self.get_default_sink()
        if sink is not None:
            self.main_layout.addWidget(
                self.create_slider_row(sink, "System Master", is_master=True)
            )

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("MixerScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("ScrollContent")
        self.scroll_content.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setContentsMargins(5, 0, 0, 0)
        self.scroll_layout.setSpacing(6)

        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

        self.refresh_devices()
        self.refresh_streams()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_logic)
        self.timer.start(1000)

        self.watchdog = QTimer(self)
        self.watchdog.timeout.connect(self.monitor_interaction)
        self.watchdog.start(100)

        self.grace_timer = QTimer(self)
        self.grace_timer.setSingleShot(True)
        self.grace_timer.timeout.connect(
            lambda: self.close() if not self.is_armed else None
        )
        self.grace_timer.start(5000)

    def closeEvent(self, event) -> None:
        self.timer.stop()
        self.watchdog.stop()
        self.close_timer.stop()
        try:
            self.pulse.close()
        except Exception as e:
            log(f"failed to close Pulse connection cleanly: {e}")
        QApplication.quit()
        event.accept()

    def monitor_interaction(self) -> None:
        is_inside = self.rect().contains(self.mapFromGlobal(QCursor.pos()))
        if is_inside or QApplication.activePopupWidget():
            if not self.is_armed:
                self.is_armed = True
                self.grace_timer.stop()
            if self.close_timer.isActive():
                self.close_timer.stop()

    def leaveEvent(self, event) -> None:
        if self.is_armed:
            self.close_timer.start(500)
        super().leaveEvent(event)

    def final_close_check(self) -> None:
        if (
            not QApplication.activePopupWidget()
            and not self.rect().contains(self.mapFromGlobal(QCursor.pos()))
        ):
            self.close()

    def create_slider_row(
        self,
        item,
        name: str,
        is_stream: bool = False,
        is_master: bool = False,
    ) -> QWidget:
        container = QWidget()
        container.setProperty("class", "SliderRow")
        container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        row = QVBoxLayout(container)
        row.setContentsMargins(0, 4, 0, 4)
        row.setSpacing(4)

        head = QHBoxLayout()
        head.setContentsMargins(0, 0, 0, 0)
        head.setSpacing(8)

        lbl = QLabel(self.elide_text(name if is_stream else name.upper(), 240))
        lbl.setProperty("class", "StreamTitle" if is_stream else "AppHeader")

        dev = QComboBox()
        dev.setObjectName("StreamOutputSelector")
        dev.setFixedWidth(120)

        if is_stream:
            try:
                for sink in self.pulse.sink_list():
                    d_name = sink.proplist.get("device.description", sink.name)
                    dev.addItem(self.elide_text(d_name, 100), sink.name)
                    if sink.index == item.sink:
                        dev.setCurrentIndex(dev.count() - 1)
                dev.currentIndexChanged.connect(
                    lambda i: self.move_stream(item, dev.itemData(i))
                )
            except Exception as e:
                log(f"failed to populate stream output selector: {e}")

        mute = QLabel("󰝟" if item.mute else "󰕾")
        mute.setProperty("class", "MuteIcon")
        mute.setCursor(Qt.CursorShape.PointingHandCursor)
        mute.mousePressEvent = lambda e: (
            self.pulse.mute(item, not item.mute),
            self.refresh_streams(),
        )

        head.addWidget(lbl)
        head.addStretch()
        if is_stream:
            head.addWidget(dev)
        head.addWidget(mute)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setObjectName("VolumeSlider")
        slider.setRange(0, 100)
        slider.setValue(int(item.volume.value_flat * 100))
        slider.valueChanged.connect(
            lambda v: (
                setattr(self, "is_armed", True),
                self.pulse.volume_set_all_chans(item, v / 100.0),
            )
        )

        row.addLayout(head)
        row.addWidget(slider)
        return container

    def refresh_streams(self) -> None:
        query = self.search_bar.text().lower()

        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        try:
            streams = self.pulse.sink_input_list()
            grouped: dict[str, list] = {}

            for stream in streams:
                app = stream.proplist.get("application.name", "App")
                media = stream.proplist.get("media.name", "Stream")

                if any(x in app.lower() for x in ["speech", "audioipc", "dummy"]):
                    continue

                if query and query not in app.lower() and query not in media.lower():
                    continue

                grouped.setdefault(app, []).append(stream)

            for app, items in grouped.items():
                hdr = QLabel(app.upper())
                hdr.setProperty("class", "AppHeader")
                self.scroll_layout.addWidget(hdr)

                for stream in items:
                    media_name = stream.proplist.get("media.name", "Stream")
                    self.scroll_layout.addWidget(
                        self.create_slider_row(stream, media_name, is_stream=True)
                    )

        except Exception as e:
            log(f"failed to refresh streams: {e}")

    def set_global_output(self, index: int) -> None:
        try:
            sink_name = self.global_out.itemData(index)
            sink = next(s for s in self.pulse.sink_list() if s.name == sink_name)
            self.pulse.sink_default_set(sink)
            self.refresh_streams()
        except Exception as e:
            log(f"failed to set global output: {e}")

    def set_global_input(self, index: int) -> None:
        try:
            source_name = self.global_in.itemData(index)
            source = next(s for s in self.pulse.source_list() if s.name == source_name)
            self.pulse.source_default_set(source)
        except Exception as e:
            log(f"failed to set global input: {e}")

    def move_stream(self, stream, sink_name: str) -> None:
        try:
            target = next(s for s in self.pulse.sink_list() if s.name == sink_name)
            self.pulse.sink_input_move(stream.index, target.index)
        except Exception as e:
            log(f"failed to move stream {stream.index} to '{sink_name}': {e}")

    def refresh_devices(self) -> None:
        self.global_out.blockSignals(True)
        self.global_in.blockSignals(True)

        self.global_out.clear()
        self.global_in.clear()

        try:
            info = self.pulse.server_info()

            for sink in self.pulse.sink_list():
                self.global_out.addItem(
                    sink.proplist.get("device.description", sink.name),
                    sink.name,
                )
                if sink.name == info.default_sink_name:
                    self.global_out.setCurrentIndex(self.global_out.count() - 1)

            for source in self.pulse.source_list():
                self.global_in.addItem(
                    source.proplist.get("device.description", source.name),
                    source.name,
                )
                if source.name == info.default_source_name:
                    self.global_in.setCurrentIndex(self.global_in.count() - 1)

        except Exception as e:
            log(f"failed to refresh devices: {e}")

        self.global_out.blockSignals(False)
        self.global_in.blockSignals(False)

    def elide_text(self, text: str, width: int) -> str:
        return QFontMetrics(self.font()).elidedText(
            text,
            Qt.TextElideMode.ElideRight,
            width,
        )

    def update_logic(self) -> None:
        try:
            if QApplication.activePopupWidget():
                return

            ids = {s.index for s in self.pulse.sink_input_list()}
            if ids != self.stream_ids:
                self.stream_ids = ids
                self.refresh_streams()

        except Exception as e:
            log(f"failed in update_logic: {e}")

    def get_default_sink(self):
        try:
            info = self.pulse.server_info()
            return next(
                s for s in self.pulse.sink_list() if s.name == info.default_sink_name
            )
        except Exception as e:
            log(f"failed to get default sink: {e}")
            return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--theme", default="cosmic")
    parser.add_argument("--reset-theme", action="store_true")
    args, _ = parser.parse_known_args()
    setup_user_configs(args.reset_theme)



    app = QApplication(sys.argv)
    app.setDesktopFileName("cosmic-mixer") 

    theme_file = os.path.join(THEME_DIR, f"{args.theme}.css")
    log(f"final theme CSS path: {theme_file}")

    mixer = VolumeMixer(theme_file)
    mixer.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()