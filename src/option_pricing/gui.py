"""Simple French desktop interface for the option-pricing project."""

import sys
from io import BytesIO

# Support both `python -m option_pricing.gui` and direct file execution.
if __package__ in (None, ""):
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "option_pricing"

from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtGui import QFont
from matplotlib.font_manager import FontProperties
from matplotlib.mathtext import math_to_image
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QLineEdit,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .black_scholes import black_scholes_price
from .greeks import black_scholes_greeks
from .monte_carlo import monte_carlo_price


class NumericField(QLineEdit):
    """Validated numeric input without native spin buttons."""

    def __init__(self, minimum, maximum, value, decimals=2):
        super().__init__()
        self._integer = decimals == 0
        locale = QLocale(QLocale.French, QLocale.France)
        self.setLocale(locale)
        validator = (
            QIntValidator(int(minimum), int(maximum), self)
            if self._integer
            else QDoubleValidator(float(minimum), float(maximum), decimals, self)
        )
        validator.setLocale(locale)
        self.setValidator(validator)
        self.setText(str(int(value)) if self._integer else locale.toString(float(value), 'f', decimals))
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def value(self):
        value, valid = self.locale().toDouble(self.text())
        if not valid:
            raise ValueError("Saisis une valeur numérique valide.")
        return int(value) if self._integer else value


class MathTextLabel(QWidget):
    """Inline label with a Matplotlib MathText-rendered symbol."""

    def __init__(self, prefix, expression, suffix=""):
        super().__init__()
        line = QHBoxLayout(self)
        line.setContentsMargins(0, 0, 0, 0)
        line.setSpacing(2)
        line.addStretch(1)
        if prefix:
            before = QLabel(prefix)
            before.setObjectName("fieldLabel")
            line.addWidget(before)
        image = BytesIO()
        math_to_image(
            expression,
            image,
            prop=FontProperties(family="sans-serif", size=8),
            dpi=96,
            format="png",
            color="#34495a",
        )
        symbol = QLabel()
        pixmap = QPixmap()
        pixmap.loadFromData(image.getvalue())
        symbol.setPixmap(pixmap)
        symbol.setAlignment(Qt.AlignCenter)
        line.addWidget(symbol)
        if suffix:
            after = QLabel(suffix)
            after.setObjectName("fieldLabel")
            line.addWidget(after)
        self.setMinimumWidth(190)
        self.setMaximumWidth(205)
        spoken_symbol = "S zéro" if expression == r"$S_0$" else "sigma"
        self.setAccessibleName(f"{prefix}{spoken_symbol}{suffix}")


class OptionPricerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Option Pricing | Projet finance")
        QApplication.setStyle("Fusion")
        self.setFont(QFont("Helvetica Neue", 13))
        self.resize(1040, 740)
        self.setMinimumSize(940, 700)
        self._build_ui()

    @staticmethod
    def _number(minimum, maximum, value, decimals=2, suffix=""):
        return NumericField(minimum, maximum, value, decimals)

    def _build_ui(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        title = QLabel("Pricing d’options européennes")
        title.setObjectName("title")
        subtitle = QLabel("Black–Scholes · Monte Carlo · Grecques")
        subtitle.setObjectName("subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        row = QHBoxLayout()
        row.setSpacing(24)
        inputs = QGroupBox("Paramètres du contrat")
        inputs.setMinimumHeight(450)
        form = QVBoxLayout(inputs)
        form.setContentsMargins(22, 28, 22, 22)
        form.setSpacing(10)
        self.spot = self._number(0.01, 1_000_000, 100, suffix=" €")
        self.strike = self._number(0.01, 1_000_000, 100, suffix=" €")
        self.volatility = self._number(0, 500, 20, suffix=" %")
        self.rate = self._number(-100, 100, 5, suffix=" %")
        self.maturity = self._number(0, 100, 1, decimals=3, suffix=" an(s)")
        self.option_type = QComboBox()
        self.option_type.addItems(["Call", "Put"])
        self.method = QComboBox()
        self.method.addItems(["Black–Scholes", "Monte Carlo"])
        self.paths = self._number(2, 10_000_000, 1_000_000, decimals=0)
        for label, widget in [
            (MathTextLabel("Spot ", r"$S_0$", " (€)"), self.spot),
            ("Strike K (€)", self.strike),
            (MathTextLabel("Volatilité ", r"$\sigma$", " (%)"), self.volatility),
            ("Taux sans risque r (%)", self.rate),
            ("Maturité T (ans)", self.maturity),
            ("Type", self.option_type),
            ("Méthode de pricing", self.method),
            ("Simulations N", self.paths),
        ]:
            field_row = QHBoxLayout()
            field_row.setSpacing(14)
            if isinstance(label, str):
                label_widget = QLabel(label)
                label_widget.setObjectName("fieldLabel")
                label_widget.setMinimumWidth(190)
                label_widget.setMaximumWidth(205)
                label_widget.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            else:
                label_widget = label
                label_widget.setFixedHeight(38)
            widget.setFixedHeight(38)
            field_row.addWidget(label_widget)
            field_row.addWidget(widget, 1)
            form.addLayout(field_row)
        row.addWidget(inputs, 1)

        results = QGroupBox("Résultats")
        results.setMinimumHeight(450)
        result_layout = QVBoxLayout(results)
        result_layout.setContentsMargins(24, 30, 24, 24)
        result_layout.setSpacing(14)
        self.price_label = QLabel("—")
        self.price_label.setObjectName("price")
        self.price_caption = QLabel("Premium estimé")
        self.price_caption.setObjectName("subtitle")
        result_layout.addWidget(self.price_caption)
        result_layout.addWidget(self.price_label)
        self.error_label = QLabel("Erreur standard : —\nIC 95 % : —")
        self.error_label.setObjectName("details")
        result_layout.addWidget(self.error_label)
        result_layout.addSpacing(18)
        greek_title = QLabel("Grecques Black–Scholes")
        greek_title.setObjectName("section")
        result_layout.addWidget(greek_title)
        self.greeks_label = QLabel("Delta : —\nGamma : —\nVega : —")
        self.greeks_label.setObjectName("details")
        result_layout.addWidget(self.greeks_label)
        result_layout.addStretch(1)
        row.addWidget(results, 1)
        layout.addLayout(row)

        self.message = QLabel("")
        self.message.setObjectName("message")
        layout.addWidget(self.message)
        self.calculate_button = QPushButton("Calculer le premium")
        self.calculate_button.setObjectName("primary")
        self.calculate_button.clicked.connect(self.calculate)
        layout.addWidget(self.calculate_button)

        note = QLabel("Modèle sans dividendes · Les taux et la volatilité sont saisis en %.")
        note.setObjectName("footnote")
        layout.addWidget(note)
        self.setCentralWidget(page)
        self.setStyleSheet("""
            QWidget {
                background: #f3f6f8;
                color: #172b3a;
                font-family: "Avenir Next", "Helvetica Neue", Arial;
                font-size: 13px;
            }
            QLabel { background: transparent; }
            QLabel#title {
                color: #123b50;
                font-size: 24px;
                font-weight: 600;
            }
            QLabel#subtitle, QLabel#footnote { color: #687887; font-size: 13px; }
            QGroupBox {
                background: #ffffff;
                border: 1px solid #dce5ea;
                border-radius: 16px;
                margin-top: 14px;
                padding: 20px;
                font-weight: 600;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 18px;
                padding: 0 8px;
                color: #176b87;
                font-size: 14px;
                font-weight: 700;
            }
            QLabel#fieldLabel { color: #34495a; font-size: 13px; font-weight: 500; }
            QLineEdit, QComboBox {
                background: #ffffff;
                color: #1d2939;
                border: 1px solid #d5dfe6;
                border-radius: 3px;
                padding: 5px 10px;
                min-width: 150px;
                font-size: 14px;
                selection-background-color: #176b87;
            }
            QLineEdit:focus, QComboBox:focus { border: 2px solid #3a91a7; }
            QComboBox::drop-down { border: 0; width: 32px; }
            QComboBox::down-arrow { width: 9px; height: 9px; }
            QLabel#price_caption { color: #687887; font-size: 14px; font-weight: 600; }
            QLabel#price {
                color: #087b91;
                background: #e8f5f7;
                border-radius: 12px;
                font-size: 36px;
                font-weight: 700;
                padding: 16px 18px;
            }
            QLabel#section { color: #123b50; font-size: 15px; font-weight: 700; }
            QLabel#details {
                color: #263746;
                background: #f7f9fa;
                border-radius: 10px;
                padding: 14px;
                font-size: 14px;
            }
            QLabel#message { color: #b42318; }
            QPushButton#primary {
                background: #087b91;
                color: white;
                border: 0;
                border-radius: 10px;
                padding: 14px;
                font-size: 15px;
                font-weight: 700;
            }
            QPushButton#primary:hover { background: #06687b; }
            QPushButton#primary:pressed { background: #055869; }
        """)
        self.method.currentTextChanged.connect(self._update_method)
        self._update_method(self.method.currentText())

    def _update_method(self, method):
        self.paths.setEnabled(method == "Monte Carlo")

    def calculate(self):
        self.message.setText("")
        spot = self.spot.value()
        strike = self.strike.value()
        volatility = self.volatility.value() / 100.0
        rate = self.rate.value() / 100.0
        maturity = self.maturity.value()
        kind = self.option_type.currentText().lower()

        try:
            if self.method.currentText() == "Monte Carlo":
                result = monte_carlo_price(
                    spot, strike, maturity, rate, volatility,
                    option_type=kind, n_paths=int(self.paths.value()), seed=2026,
                )
                price = result.price
                self.error_label.setText(
                    f"Erreur standard : {result.standard_error:.5f} €\n"
                    f"IC 95 % : [{result.ci_lower:.5f} ; {result.ci_upper:.5f}] €"
                )
            else:
                price = black_scholes_price(
                    spot, strike, maturity, rate, volatility, kind
                )
                self.error_label.setText("Erreur standard : sans objet\nIC 95 % : sans objet")

            self.price_label.setText(f"{price:.4f} €")
            if maturity == 0 or volatility == 0:
                self.greeks_label.setText("Delta : non défini à cette limite\nGamma : non défini\nVega : non défini")
            else:
                greeks = black_scholes_greeks(
                    spot, strike, maturity, rate, volatility, kind
                )
                self.greeks_label.setText(
                    f"Delta : {greeks.delta:.6f}\n"
                    f"Gamma : {greeks.gamma:.6f}\n"
                    f"Vega : {greeks.vega:.6f} € par 1,00 de volatilité"
                )
        except (ValueError, OverflowError) as error:
            self.message.setText(str(error))


def main():
    app = QApplication(sys.argv)
    window = OptionPricerWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
