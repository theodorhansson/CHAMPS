# IMPORTS --------------------------------------------------------------------
import time
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.widgets import Button
from pylablib.devices import Andor
import communication
from drivers.arduino_giga_serial.aurora import aurora
import general_functions.pretty_printing.verbose_printing as vp

try:
    import utils
except ImportError:
    import sys, pathlib
    util_path = str(pathlib.Path(__file__).parent.parent.resolve())
    sys.path.append(util_path)
    import utils


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
x_pixel = 1024
y_pixel = 1024
px_scale = 5.596  # µm/px
window_size = 50  # smoothing window for X spectrum

x_axis_um = np.arange(0, x_pixel * px_scale, px_scale)
y_axis_um = np.arange(0, y_pixel * px_scale, px_scale)
extent_raw = np.array([0, x_pixel * px_scale, 0, y_pixel * px_scale])


# ---------------------------------------------------------------------------
# Moving-average helper (used on the X spectrum)
# ---------------------------------------------------------------------------
def moving_average_two_sided(data, window_size):
    """Centered moving average using data points on both sides."""
    data = np.asarray(data)
    if window_size < 2 or window_size > data.size:
        return data
    if window_size % 2 == 0:
        window_size += 1
    window = np.ones(window_size) / window_size
    return np.convolve(data, window, mode="same")


# ---------------------------------------------------------------------------
# Dummy DC (for simulation mode)
# ---------------------------------------------------------------------------
class DummyDC:
    def __init__(self, config):
        self.verbose = config.get("verbose_printing", 0)

    def __enter__(self):
        print("DummyDC: entering context (no hardware connected).")
        return self

    def __exit__(self, exc_type, exc_value, tb):
        print("DummyDC: exiting context.")
        return False

    def set_current(self, value): pass
    def set_voltage_limit(self, value): pass
    def set_output(self, value): pass
    def get_voltage_and_current(self): return 0.0, 0.0


# ---------------------------------------------------------------------------
# DC selector (same logic as before)
# ---------------------------------------------------------------------------
def get_DC_unit(config):
    dc_cfg = config.get("dc_unit", {})
    dc_type = dc_cfg.get("type", "").lower()
    if dc_type in ("dummy", "none", "simulated"):
        if dc_cfg.get("verbose_printing", 0):
            print("Using DummyDC (simulation mode).")
        return DummyDC
    else:
        Instrument_COM = communication.Communication()
        if dc_cfg.get("verbose_printing", 0):
            print(f"Connecting to real DC unit: {dc_type}")
        return Instrument_COM.get_DCsupply(dc_cfg)


# ---------------------------------------------------------------------------
# Alignment figure (live, with "Set reference" button and normalization plot)
# ---------------------------------------------------------------------------
class alignment_figure:
    def __init__(self, integrate_over_um, window_size):
        self.integrate_over_pixel = int(integrate_over_um / px_scale)
        self.window_size = window_size

        plt.ion()
        fig = plt.figure(figsize=(10, 8), num=0, clear=True)
        gs = fig.add_gridspec(2, 2)
        ax0 = fig.add_subplot(gs[0, 0])
        ax1 = fig.add_subplot(gs[0, 1])
        ax2 = fig.add_subplot(gs[1, 0])
        ax3 = fig.add_subplot(gs[1, 1])
        self.ax_array = [ax0, ax1, ax2, ax3]

        plt.suptitle("SPR alignment (live)")

        # Button for setting reference
        btn_ax = fig.add_axes([0.8, 0.92, 0.15, 0.05])
        self.btn_set_ref = Button(btn_ax, "Set reference")
        self.btn_set_ref.on_clicked(self.on_set_reference)

        # Storage for spectra
        self.current_filtered = None   # current filtered X spectrum (normalized)
        self.reference = None          # stored reference (normalized)

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        self.fig = fig
        plt.show(block=False)

    def on_set_reference(self, event):
        """Store current filtered X spectrum as reference."""
        if self.current_filtered is not None:
            self.reference = self.current_filtered.copy()
            vp.message("Reference spectrum updated.")

    def update_alignment_image(self, image):
        ax0, ax1, ax2, ax3 = self.ax_array

        # Clear axes each frame
        for ax in self.ax_array:
            ax.cla()

        # -------- Raw image --------
        ax0.imshow(image, extent=extent_raw, origin="lower", cmap="magma")
        ax0.set_title("Raw image")
        ax0.set_xlabel("x [µm]")
        ax0.set_ylabel("y [µm]")

        # -------- y-integrated spectrum (sum over x) --------
        y_cross = np.sum(image, axis=1)
        y_max_index = np.argmax(y_cross)

        ax1.plot(y_cross, y_axis_um)
        ax1.plot(y_cross[y_max_index], y_axis_um[y_max_index], "x", color="black")
        ax1.set_title("y-integrated spectrum")
        ax1.set_xlabel("Intensity [counts]")
        ax1.set_ylabel("y [µm]")

        # Integration band on raw image
        integrate = self.integrate_over_pixel
        y_center = y_axis_um[y_max_index]
        y_top = y_axis_um[min(y_max_index + integrate, y_pixel - 1)]
        y_bottom = y_axis_um[max(y_max_index - integrate, 0)]

        ax0.plot([0, np.max(x_axis_um)], [y_center, y_center], color="red", linewidth=0.5)
        ax0.plot([0, np.max(x_axis_um)], [y_top, y_top], color="red", linewidth=0.3)
        ax0.plot([0, np.max(x_axis_um)], [y_bottom, y_bottom], "--", color="red", linewidth=0.3)

        # -------- X spectrum (Y-integrated) + filtering --------
        spr_spectrum = np.sum(
            image[y_max_index - integrate:y_max_index + integrate, :],
            axis=0,
        )

        spr_spectrum_smooth = moving_average_two_sided(
            spr_spectrum, window_size=self.window_size
        )

        # Trim edges to avoid filter artefacts
        edge = self.window_size // 2
        if len(spr_spectrum_smooth) > 2 * edge:
            x_trimmed = x_axis_um[edge:-edge]
            smooth_trimmed = spr_spectrum_smooth[edge:-edge]
        else:
            x_trimmed = x_axis_um
            smooth_trimmed = spr_spectrum_smooth

        norm = np.max(spr_spectrum) if np.max(spr_spectrum) != 0 else 1.0

        ax2.plot(x_axis_um, spr_spectrum / norm, label="Original")
        ax2.plot(x_trimmed, smooth_trimmed / norm,
                 label=f"Filtered (w={self.window_size})")
        ax2.set_title("Reflected spectrum")
        ax2.set_xlabel("x [µm]")
        ax2.set_ylabel("Intensity [norm.]")
        ax2.legend()

        # Store current filtered spectrum in full length array (with NaNs at edges)
        filtered_full = np.empty_like(spr_spectrum_smooth, dtype=float)
        if len(spr_spectrum_smooth) > 2 * edge:
            filtered_full[edge:-edge] = smooth_trimmed / norm
            # Extend edges to remove NaNs
            filtered_full[:edge] = filtered_full[edge]
            filtered_full[-edge:] = filtered_full[-edge - 1]
        else:
            filtered_full[:] = spr_spectrum_smooth / norm

        self.current_filtered = filtered_full

        # -------- Reference & normalized plot --------
        if self.reference is not None:
            # Ref in ax2
            ax2.plot(x_axis_um, self.reference, "--", label="Reference")
            ax2.legend()

            # Normalized I / I_ref in ax3
            valid = ~np.isnan(self.reference) & (self.reference != 0)
            ratio = np.full_like(filtered_full, np.nan)
            ratio[valid] = (smooth_trimmed / norm)[valid] / self.reference[valid]


            ax3.plot(x_axis_um, ratio, label="I / I_ref")
            ax3.axhline(1.0, color="gray", linestyle="--", linewidth=0.8)
            ax3.set_title("Normalized by reference")
            ax3.set_xlabel("x [µm]")
            ax3.set_ylabel("I / I_ref")
            ax3.legend()

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

        return y_max_index, spr_spectrum


    def on_set_reference(self, event):
        """Callback for button: store current filtered X spectrum as reference."""
        if self.current_filtered is not None:
            self.reference = self.current_filtered.copy()
            vp.message("Reference spectrum updated.")

    def update_alignment_image(self, image):
        ax0, ax1, ax2, ax3 = self.ax_array

        # Clear axes
        for ax in self.ax_array:
            ax.cla()

        # -------- Raw image --------
        ax0.imshow(image, extent=extent_raw, origin="lower", cmap="magma")

        # -------- y-integrated spectrum (sum over x) --------
        y_cross = np.sum(image, axis=1)
        y_max_index = np.argmax(y_cross)
        ax1.plot(y_cross, y_axis_um)
        ax1.plot(y_cross[y_max_index], y_axis_um[y_max_index], "x", color="black")

        integrate = self.integrate_over_pixel
        y_center = y_axis_um[y_max_index]
        y_top = y_axis_um[min(y_max_index + integrate, y_pixel - 1)]
        y_bottom = y_axis_um[max(y_max_index - integrate, 0)]

        ax0.plot([0, np.max(x_axis_um)], [y_center, y_center], color="red", linewidth=0.5)
        ax0.plot([0, np.max(x_axis_um)], [y_top, y_top], color="red", linewidth=0.3)
        ax0.plot([0, np.max(x_axis_um)], [y_bottom, y_bottom], "--", color="red", linewidth=0.3)

        # -------- X spectrum (Y-integrated) --------
        spr_spectrum = np.sum(
            image[y_max_index - integrate:y_max_index + integrate, :],
            axis=0,
        )

        spr_spectrum_smooth = moving_average_two_sided(
            spr_spectrum, window_size=self.window_size
        )

        # Trim edges
        edge = self.window_size // 2
        x_trimmed = x_axis_um[edge:-edge]
        smooth_trimmed = spr_spectrum_smooth[edge:-edge]

        norm = np.max(spr_spectrum) if np.max(spr_spectrum) != 0 else 1.0
        ax2.plot(x_axis_um, spr_spectrum / norm, label="Original")
        ax2.plot(x_trimmed, smooth_trimmed / norm,
                 label=f"Filtered (w={self.window_size})")

        # Save current filtered
        filtered_full = np.full_like(spr_spectrum_smooth, np.nan, dtype=float)
        filtered_full[edge:-edge] = smooth_trimmed / norm
        self.current_filtered = filtered_full

        # Plot reference if available
        if self.reference is not None:
            ax2.plot(x_axis_um, self.reference, "--", label="Reference")

            # -------- Normalized by reference (new plot) --------
            valid = ~np.isnan(self.reference) & (self.reference != 0)
            ratio = np.full_like(filtered_full, np.nan)
            ratio[valid] = filtered_full[valid] / self.reference[valid]
            ax3.plot(x_axis_um, ratio, label="I / I_ref")
            ax3.axhline(1.0, color="gray", linestyle="--", linewidth=0.8)
            ax3.set_ylim(0.5, 1.5)  # adjust as needed
            ax3.legend()

        ax2.legend()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

        return y_max_index, spr_spectrum


# ---------------------------------------------------------------------------
# Alignment live: one laser, continuous frames
# ---------------------------------------------------------------------------
def SPR_alignment_live(IPV_config, DC_config, DC_unit_obj):
    V_max = IPV_config["v_max"]
    exposure_time = IPV_config["exposure_time"]
    integrate_over_um = IPV_config["integrate_over_um"]
    vcsel_chip = IPV_config["vcsel_chip"]
    vcsel_biases = IPV_config["vcsel_biases"]

    laser_control = aurora(vcsel_chip)
    lasers_on_chip = np.fromiter(laser_control.chip.keys(), dtype=int)

    if len(vcsel_biases) != len(lasers_on_chip):
        print("Not all VCSELs have a bias! Please check your config.toml")
        return

    laser = lasers_on_chip[0]

    alignment_fig = alignment_figure(integrate_over_um, window_size)
    vp.message(f"Running live alignment on laser {laser} (press Ctrl+C to stop)")

    with DC_unit_obj(DC_config) as DC_unit, Andor.AndorSDK3Camera(idx=0) as cam:
        cam.set_exposure(exposure_time)
        cam.set_roi(0, 2048, 0, 2048, hbin=2, vbin=2)
        DC_unit.set_current(0.0)
        DC_unit.set_voltage_limit(V_max)
        DC_unit.set_output(True)

        laser_control.switch_to_laser(laser)
        utils.ramp_current(DC_unit, 0, vcsel_biases[laser])

        try:
            while True:
                image = cam.grab(1)[0]
                alignment_fig.update_alignment_image(image)
                plt.pause(0.01)
        except KeyboardInterrupt:
            vp.message("Live alignment stopped by user.")
        finally:
            utils.ramp_current(DC_unit, vcsel_biases[laser], 0)
            laser_control.turn_off_all_lasers()

    laser_control.turn_off_all_lasers()
    vp.message("Alignment complete.")


# ---------------------------------------------------------------------------
# CHAMPS entry point
# ---------------------------------------------------------------------------
def init(config: dict, meas_output_dir_path: str):
    DC_unit_obj = get_DC_unit(config)
    spr_config = config["measurement"]
    DC_config = config["dc_unit"]

    SPR_alignment_live(spr_config, DC_config, DC_unit_obj)
    return {}, {}
