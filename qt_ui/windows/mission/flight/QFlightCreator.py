from typing import Optional

from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import (
    QDialog,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)
from dcs.planes import PlaneType

from game import Game
from gen.ato import Package
from gen.flights.flight import Flight
from qt_ui.uiconstants import EVENT_ICONS
from qt_ui.widgets.QFlightSizeSpinner import QFlightSizeSpinner
from qt_ui.widgets.QLabeledWidget import QLabeledWidget
from qt_ui.widgets.combos.QAircraftTypeSelector import QAircraftTypeSelector
from qt_ui.widgets.combos.QFlightTypeComboBox import QFlightTypeComboBox
from qt_ui.widgets.combos.QOriginAirfieldSelector import QOriginAirfieldSelector
from theater import ControlPoint


class QFlightCreator(QDialog):
    created = Signal(Flight)

    def __init__(self, game: Game, package: Package, parent=None) -> None:
        super().__init__(parent=parent)

        self.game = game
        self.package = package

        self.setWindowTitle("Create flight")
        self.setWindowIcon(EVENT_ICONS["strike"])

        layout = QVBoxLayout()

        self.task_selector = QFlightTypeComboBox(
            self.game.theater, package.target
        )
        self.task_selector.setCurrentIndex(0)
        layout.addLayout(QLabeledWidget("Task:", self.task_selector))

        self.aircraft_selector = QAircraftTypeSelector(
            self.game.aircraft_inventory.available_types_for_player
        )
        self.aircraft_selector.setCurrentIndex(0)
        self.aircraft_selector.currentIndexChanged.connect(
            self.on_aircraft_changed)
        layout.addLayout(QLabeledWidget("Aircraft:", self.aircraft_selector))

        self.airfield_selector = QOriginAirfieldSelector(
            self.game.aircraft_inventory,
            [cp for cp in game.theater.controlpoints if cp.captured],
            self.aircraft_selector.currentData()
        )
        self.airfield_selector.availability_changed.connect(self.update_max_size)
        layout.addLayout(QLabeledWidget("Airfield:", self.airfield_selector))

        self.flight_size_spinner = QFlightSizeSpinner()
        self.update_max_size(self.airfield_selector.available)
        layout.addLayout(QLabeledWidget("Size:", self.flight_size_spinner))

        self.client_slots_spinner = QFlightSizeSpinner(
            min_size=0,
            max_size=self.flight_size_spinner.value(),
            default_size=0
        )
        self.flight_size_spinner.valueChanged.connect(
            lambda v: self.client_slots_spinner.setMaximum(v)
        )
        layout.addLayout(
            QLabeledWidget("Client Slots:", self.client_slots_spinner))

        layout.addStretch()

        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.create_flight)
        layout.addWidget(self.create_button, alignment=Qt.AlignRight)

        self.setLayout(layout)

    def verify_form(self) -> Optional[str]:
        aircraft: PlaneType = self.aircraft_selector.currentData()
        origin: ControlPoint = self.airfield_selector.currentData()
        size: int = self.flight_size_spinner.value()
        if not origin.captured:
            return f"{origin.name} is not owned by your coalition."
        available = origin.base.aircraft.get(aircraft, 0)
        if not available:
            return f"{origin.name} has no {aircraft.id} available."
        if size > available:
            return f"{origin.name} has only {available} {aircraft.id} available."
        if size <= 0:
            return f"Flight must have at least one aircraft."
        return None

    def create_flight(self) -> None:
        error = self.verify_form()
        if error is not None:
            QMessageBox.critical(self, "Could not create flight", error,
                                 QMessageBox.Ok)
            return

        task = self.task_selector.currentData()
        aircraft = self.aircraft_selector.currentData()
        origin = self.airfield_selector.currentData()
        size = self.flight_size_spinner.value()

        if self.game.settings.perf_ai_parking_start:
            start_type = "Cold"
        else:
            start_type = "Warm"
        flight = Flight(self.package, aircraft, size, origin, task, start_type)
        flight.client_count = self.client_slots_spinner.value()

        # noinspection PyUnresolvedReferences
        self.created.emit(flight)
        self.close()

    def on_aircraft_changed(self, index: int) -> None:
        new_aircraft = self.aircraft_selector.itemData(index)
        self.airfield_selector.change_aircraft(new_aircraft)

    def update_max_size(self, available: int) -> None:
        self.flight_size_spinner.setMaximum(min(available, 4))
        if self.flight_size_spinner.maximum() >= 2:
            if self.flight_size_spinner.value() < 2:
                self.flight_size_spinner.setValue(2)
