# IMPORTS --------------------------------------------------------------------
import os
import time
import traceback
from pathlib import Path

import numpy as np
import imageio.v3 as iio
import matplotlib.pyplot as plt

from scipy.interpolate import CubicSpline
from scipy.signal import butter, filtfilt
from pylablib.devices import Andor

import communication
from drivers.arduino_giga_serial.aurora import aurora
import general_functions.pretty_printing.verbose_printing as vp

try:
    import utils
except ImportError:
    import sys
    import pathlib

    util_path = str(pathlib.Path(__file__).parent.parent.resolve())
    sys.path.append(util_path)
    import utils

# ---------------------------------------------------------------------------
# General / plotting constants
# ---------------------------------------------------------------------------

x_pixel = 1024
y_pixel = 1024
px_scale = 5.596  # um/px for 2.5x objective

x_axis_um = np.arange(0, x_pixel * px_scale, px_scale)
y_axis_um = np.arange(0, y_pixel * px_scale, px_scale)
extent_raw = np.array([0, x_pixel * px_scale, 0, y_pixel * px_scale])
colors = ['blue', 'aqua', 'red', 'lightcoral', 'green', 'lightgreen']

# ---------------------------------------------------------------------------
# Alignment figure
# ---------------------------------------------------------------------------


class alignment_figure:
    def __init__(self, integrate_over_um: float):
        self.integrate_over_pixel = int(integrate_over_um / px_scale)

        fig = plt.figure(figsize=(10, 7), num=0, clear=True)
        ax0 = fig.add_subplot(221)
        ax1 = fig.add_subplot(222)
        ax2 = fig.add_subplot(223)
        self.ax_array = [ax0, ax1, ax2]

        plt.suptitle('SPR alignment')

        ax0.set_title('Raw image')
        ax0.set_xlabel('x [µm]')
        ax0.set_ylabel('y [µm]')

        ax1.set_title('y-integrated spectrum')
        ax1.set_xlabel('Intensity [counts]')
        ax1.set_ylabel('y [µm]')

        ax2.set_title('Reflected spectrum from alignment')
        ax2.set_xlabel('x [µm]')
        ax2.set_ylabel('Intensity [counts]')

        plt.tight_layout()
        self.fig = fig

    def update_alignment_image(self, image: np.ndarray):
        # Plot full image
        self.ax_array[0].imshow(image, extent=extent_raw, origin='lower', cmap='magma')

        # Sum along y-axis and find maximum
        y_cross = np.sum(image, axis=1)
        y_max_index = np.argmax(y_cross)

        # Plot y-integrated spectrum
        self.ax_array[1].plot(y_cross, y_axis_um)
        self.ax_array[1].plot(
            y_cross[y_max_index],
            y_axis_um[y_max_index],
            'x',
            color='black'
        )

        # Mark integration region in the raw image
        y_center = y_axis_um[y_max_index]
        y_top = y_axis_um[min(y_max_index + self.integrate_over_pixel, y_pixel - 1)]
        y_bottom = y_axis_um[max(y_max_index - self.integrate_over_pixel, 0)]

        self.ax_array[0].plot(
            [0, np.max(x_axis_um)],
            [y_center, y_center],
            color='red',
            linewidth=0.5
        )
        self.ax_array[0].plot(
            [0, np.max(x_axis_um)],
            [y_top, y_top],
            color='red',
            linewidth=0.3
        )
        self.ax_array[0].plot(
            [0, np.max(x_axis_um)],
            [y_bottom, y_bottom],
            '--',
            color='red',
            linewidth=0.3
        )

        min_idx = y_max_index - self.integrate_over_pixel
        max_idx = y_max_index + self.integrate_over_pixel
        if min_idx < 0 or max_idx > y_pixel:
            vp.headline(
                'You, Cassandra, are finding a laser beam too close to the edge '
                'of the image. Move stage or integrate less wide.'
            )

        # Integrated spectrum around laser
        spr_spectrum = np.sum(
            image[max(min_idx, 0):min(max_idx, y_pixel), :],
            axis=0
        )
        self.ax_array[2].plot(x_axis_um, spr_spectrum / np.max(spr_spectrum))

        # Update canvas
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

        return y_max_index, spr_spectrum


# ---------------------------------------------------------------------------
# Spectrum processing helpers
# ---------------------------------------------------------------------------


def create_peak_spectrum(values: np.ndarray,
                         start_cropped_image_from_pixel: int,
                         stopp_cropped_image_from_pixel: int,
                         spacing: float = 15,
                         px_avg: int = 3):
    """Create filtered peak spectrum from a 1D intensity profile."""
    zeroed_values = values[start_cropped_image_from_pixel:stopp_cropped_image_from_pixel]
    zeroed_coords = np.arange(zeroed_values.size) * px_scale

    peak_coords = np.arange(0, np.max(zeroed_coords), spacing)

    peaks = []
    for peak_x in peak_coords:
        mask = np.abs(zeroed_coords - peak_x) < px_scale * px_avg
        peaks.append(np.max(zeroed_values[mask]))

    # Butterworth lowpass filter
    sampling_freq = 1 / spacing
    cutoff_freq = 1 / 200
    nyquist_freq = 0.5 * sampling_freq
    normalized_cutoff_freq = cutoff_freq / nyquist_freq

    b, a = butter(2, normalized_cutoff_freq, btype='low')
    peaks = filtfilt(b, a, peaks)

    return peak_coords, np.array(peaks)


def isolate_SPR(peak_coords: np.ndarray,
                peak_values: np.ndarray,
                width_around_SPR_dip: float = 150):
    """Isolate spectrum around the SPR dip from a coarse peak spectrum."""
    start_from = 3
    stopp_at = 10

    peak_coords = np.asarray(peak_coords)
    peak_values = np.asarray(peak_values)

    # Not enough points to safely look for a dip
    if peak_values.size <= start_from + stopp_at:
        return np.array([]), np.array([]), None

    # Find minimum in the inner region
    spr_dip_rel_index = np.argmin(peak_values[start_from:-stopp_at])
    spr_dip_index = spr_dip_rel_index + start_from

    if spr_dip_index < 0 or spr_dip_index >= peak_coords.size:
        return np.array([]), np.array([]), None

    SPR_x = np.arange(
        peak_coords[spr_dip_index] - width_around_SPR_dip / 2,
        peak_coords[spr_dip_index] + width_around_SPR_dip / 2,
        15
    )

    if SPR_x.size == 0:
        return np.array([]), np.array([]), None

    half_len = SPR_x.size // 2
    # Slice around the dip
    start_idx = max(spr_dip_index - half_len, 0)
    stop_idx = min(spr_dip_index + half_len, peak_values.size)
    SPR_y = peak_values[start_idx:stop_idx]

    # If lengths mismatch, trim the longer one
    min_len = min(SPR_x.size, SPR_y.size)
    SPR_x = SPR_x[:min_len]
    SPR_y = SPR_y[:min_len]

    if min_len == 0:
        return np.array([]), np.array([]), None

    return SPR_x, SPR_y, peak_coords[spr_dip_index]


def find_SPR_dip(x: np.ndarray, y: np.ndarray) -> float:
    """Find the position of the SPR dip using cubic spline interpolation."""
    if x is None or y is None:
        return np.nan

    x = np.asarray(x)
    y = np.asarray(y)

    if x.size == 0 or y.size == 0:
        return np.nan

    try:
        x_fit = np.linspace(np.min(x), np.max(x), 10000)
        spline = CubicSpline(x, y)
        x_centroid = x_fit[np.argmax(spline(x_fit))]
    except Exception:
        print('Failed to find SPR Dip!')
        x_centroid = np.nan

    return x_centroid


# ---------------------------------------------------------------------------
# SPR figure
# ---------------------------------------------------------------------------


class SPR_figure:
    def __init__(self, integrate_over_um: float):
        self.integrate_over_pixel = int(integrate_over_um / px_scale)

        plt.ion()
        fig = plt.figure(figsize=(10, 7), num=1, clear=True)
        ax0 = fig.add_subplot(231)
        ax1 = fig.add_subplot(232)
        ax2 = fig.add_subplot(234)
        ax3 = fig.add_subplot(235)
        ax4 = fig.add_subplot(133)
        self.ax_array = [ax0, ax1, ax2, ax3, ax4]

        plt.suptitle('SPR measurements')

        for i, ax in enumerate(fig.axes):
            if i not in (0, 4):
                ax.grid(True)
                ax.set_xlabel('x [µm]')

        ax0.set_title('Raw image')
        ax0.set_xlabel('x [px]')
        ax0.set_ylabel('y [px]')

        ax1.set_title('Integrated spectrum')
        ax1.set_ylabel('Intensity [Counts]')

        ax2.set_title('Filtered peaks')
        ax2.set_ylabel('Intensity [Counts]')

        ax3.set_title('SPR dip')
        ax3.set_ylabel('Intensity [Counts]')

        ax4.set_title('SPR trace')
        ax4.set_xlabel('Time [s]')
        ax4.set_ylabel('x [µm]')
        ax4.grid(True)

        plt.tight_layout()
        self.fig = fig

        self.im_raw_data = None
        self.line_integrated_spectrum = None
        self.filtered_spectrum = None
        self.dip_spectrum = None

        # NEW: vertical lines for SPR window in peak spectrum
        self.left_line_peak_spectrum = None
        self.right_line_peak_spectrum = None

    def analyze_image(self,
                      image: np.ndarray,
                      y_max_index: int,
                      frame_counter: int,
                      config: dict,
                      start_cropped_image_from: float,
                      stopp_cropped_image_from: float,
                      start_look_for_dip_from: float,
                      stopp_look_for_dip_from: float,
                      width_around_SPR_dip_um: float):
        # Crop image around laser
        min_row = max(int(y_max_index - self.integrate_over_pixel), 0)
        max_row = min(int(y_max_index + self.integrate_over_pixel), image.shape[0])
        cropped_image = image[min_row:max_row, :]

        x = np.arange(cropped_image.shape[1]) * px_scale
        y = np.mean(cropped_image, axis=0)

        start_idx = np.argmin(np.abs(x - start_cropped_image_from))
        stop_idx = np.argmin(np.abs(x - stopp_cropped_image_from))

        peak_x, peak_y = create_peak_spectrum(
            y,
            start_idx,
            stop_idx
        )

        # use configured width around SPR dip
        sprx, spry, SPR_x = isolate_SPR(peak_x, peak_y, width_around_SPR_dip_um)

        # SAFETY: handle possible empty SPR window
        if spry.size == 0:
            x_SPR = np.nan
        else:
            x_SPR = find_SPR_dip(sprx, np.max(spry) - spry)

        x_offset_um = x[start_idx]

        if frame_counter == 0:
            # Raw image
            self.im_raw_data = self.ax_array[0].imshow(image)

            # Integrated detected spectrum
            (self.line_integrated_spectrum,) = self.ax_array[1].plot(
                x, y, linewidth=0.5
            )
            self.ax_array[1].set_xlim(start_cropped_image_from, stopp_cropped_image_from)
            self.ax_array[1].set_ylim(np.min(y), np.max(y))

            # Vertical guide lines in integrated spectrum: region where we look for dip
            self.ax_array[1].plot(
                [start_look_for_dip_from, start_look_for_dip_from],
                [np.min(y), np.max(y)],
                '--',
                color='black',
                linewidth=1
            )
            self.ax_array[1].plot(
                [stopp_look_for_dip_from, stopp_look_for_dip_from],
                [np.min(y), np.max(y)],
                '--',
                color='black',
                linewidth=1
            )

            # Filtered spectrum
            (self.filtered_spectrum,) = self.ax_array[2].plot(
                peak_x + x_offset_um,
                peak_y,
                color='black',
                marker='o',
                markersize=3
            )
            self.ax_array[2].set_ylim(np.min(peak_y), np.max(peak_y))

            # SPR window lines in filtered peaks
            if sprx.size > 0:
                left = np.min(sprx) + x_offset_um
                right = np.max(sprx) + x_offset_um
                self.left_line_peak_spectrum, = self.ax_array[2].plot(
                    [left, left],
                    [np.min(peak_y), np.max(peak_y)],
                    '--',
                    color='black',
                    linewidth=1
                )
                self.right_line_peak_spectrum, = self.ax_array[2].plot(
                    [right, right],
                    [np.min(peak_y), np.max(peak_y)],
                    '--',
                    color='black',
                    linewidth=1
                )

            # Isolated SPR dip
            (self.dip_spectrum,) = self.ax_array[3].plot(
                sprx,
                spry,
                'r',
                marker='o',
                markersize=3
            )
        else:
            # Raw image
            self.ax_array[0].imshow(image)

            # Integrated spectrum
            self.line_integrated_spectrum.set_data(x, y)
            self.ax_array[1].set_ylim(np.min(y), np.max(y))

            # Filtered peaks
            self.filtered_spectrum.set_data(peak_x + x_offset_um, peak_y)
            self.ax_array[2].set_ylim(np.min(peak_y), np.max(peak_y))

            # Update SPR window lines in peak spectrum
            if sprx.size > 0 and self.left_line_peak_spectrum is not None:
                left = np.min(sprx) + x_offset_um
                right = np.max(sprx) + x_offset_um
                self.left_line_peak_spectrum.set_data(
                    [left, left],
                    [np.min(peak_y), np.max(peak_y)]
                )
                self.right_line_peak_spectrum.set_data(
                    [right, right],
                    [np.min(peak_y), np.max(peak_y)]
                )

            # SPR dip spectrum
            self.dip_spectrum.set_data(sprx, spry)
            if sprx.size > 0 and spry.size > 0:
                self.ax_array[3].set_xlim(np.min(sprx), np.max(sprx))
                self.ax_array[3].set_ylim(np.min(spry), np.max(spry))

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

        return x_SPR

    def update_spr_trace(self,
                         lasers_on_chip: np.ndarray,
                         results: dict,
                         color,
                         frame_counter: int,
                         start_trace: int,
                         clear_trace: bool):
        ax = self.fig.axes[4]

        if clear_trace:
            ax.clear()
            ax.set_title('SPR trace')
            ax.set_xlabel('Time [s]')
            ax.set_ylabel('x [µm]')
            ax.grid(True)

        for ch in lasers_on_chip:
            frame_time = results['frame_time'][ch][start_trace:]
            spr_trace = results['spr_data'][ch][start_trace:]
            ax.plot(
                frame_time,
                spr_trace,
                marker='o',
                linewidth=0.2,
                markersize=3,
                color=color[ch],
                label=f'Laser {ch}'
            )

        if frame_counter == 0:
            ax.legend(loc='lower left')

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


# ---------------------------------------------------------------------------
# Dummy DC class (for running code without DC unit)
# ---------------------------------------------------------------------------


class DummyDC:
    def __init__(self, config):
        self.verbose = config.get('verbose_printing', 0)

    def __enter__(self):
        print("DummyDC: entering context (no hardware connected).")
        return self

    def __exit__(self, exc_type, exc_value, tb):
        print("DummyDC: exiting context.")
        return False

    def set_current(self, value):
        pass

    def set_voltage_limit(self, value):
        pass

    def set_output(self, value):
        pass

    def get_voltage_and_current(self):
        return 0.0, 0.0


# ---------------------------------------------------------------------------
# DC selection
# ---------------------------------------------------------------------------


def get_DC_unit(config):
    dc_cfg = config.get('dc_unit', {})
    dc_type = dc_cfg.get('type', '').lower()

    if dc_type in ('dummy', 'none', 'simulated'):
        if dc_cfg.get('verbose_printing', 0):
            print("Using DummyDC (simulation mode).")
        return DummyDC

    if dc_cfg.get('verbose_printing', 0):
        print(f"Connecting to real DC unit: {dc_type}")

    instrument_com = communication.Communication()
    return instrument_com.get_DCsupply(dc_cfg)


# ---------------------------------------------------------------------------
# Public init
# ---------------------------------------------------------------------------


def init(config: dict, meas_output_dir_path: str):
    """Entry point called by framework."""
    DC_unit_obj = get_DC_unit(config)

    spr_config = config['measurement']
    DC_config = config['dc_unit']
    measurement_type = spr_config['type']
    DC_name = DC_config['type']

    results = SPR_main(spr_config, DC_config, DC_unit_obj, meas_output_dir_path)
    return_dict = {measurement_type: spr_config, DC_name: DC_config}
    return results, return_dict


# ---------------------------------------------------------------------------
# Main SPR measurement
# ---------------------------------------------------------------------------


def SPR_main(IPV_config: dict,
             DC_config: dict,
             DC_unit_obj,
             meas_output_dir_path: str):
    V_max = IPV_config['v_max']
    verbose = IPV_config['verbose_printing']
    measurement_time = IPV_config['measurement_time']
    measurement_interval = IPV_config['measurement_interval']

    vcsel_chip = IPV_config['vcsel_chip']
    vcsel_biases = IPV_config['vcsel_biases']

    run_measurement = IPV_config['run_measurement']
    start_cropped_image_from = IPV_config['start_cropped_image_from']
    stopp_cropped_image_from = IPV_config['stopp_cropped_image_from']

    # NEW: also use these again, as in original code
    start_look_for_dip_from = IPV_config['start_look_for_dip_from']
    stopp_look_for_dip_from = IPV_config['stopp_look_for_dip_from']
    width_around_SPR_dip_um = IPV_config['width_around_spr_dip_um']

    exposure_time = IPV_config['exposure_time']
    integrate_over_um = IPV_config['integrate_over_um']

    laser_control = aurora(vcsel_chip)
    lasers_on_chip = np.fromiter(laser_control.chip.keys(), dtype=int)

    for instru_dict in [DC_config]:
        instru_dict.setdefault('verbose_printing', verbose)

    # Preallocate result containers
    results = {'frame_list': {}, 'frame_time': {}, 'spr_data': {}}
    for i in range(len(vcsel_biases)):
        results['frame_list'][i] = []
        results['frame_time'][i] = []
        results['spr_data'][i] = []

    measurement_time_start = time.time()
    measurement_timestamp = time.strftime('%Y%m%d_%H.%M.%S')

    if len(vcsel_biases) != len(lasers_on_chip):
        print('Not all VCSELs have a bias! Please check your config.toml')
        return results

    with DC_unit_obj(DC_config) as DC_unit, Andor.AndorSDK3Camera(idx=0) as cam:
        try:
            cam.set_exposure(exposure_time)
            cam.set_roi(0, 2048, 0, 2048, hbin=2, vbin=2)

            DC_unit.set_current(0.0)
            DC_unit.set_voltage_limit(V_max)
            DC_unit.set_output(True)

            vp.message('Finding new alignment')

            alignment_voltage = np.zeros_like(lasers_on_chip, dtype=float)
            alignment_current = np.zeros_like(lasers_on_chip, dtype=float)

            alignment_figure_obj = alignment_figure(integrate_over_um)
            laser_locations = []

            # Alignment loop
            for i, laser in enumerate(lasers_on_chip):
                laser_control.switch_to_laser(laser)
                utils.ramp_current(DC_unit, 0, vcsel_biases[laser])

                image_array = cam.grab(1)
                image = image_array[0]

                y_max_index, _ = alignment_figure_obj.update_alignment_image(image)
                laser_locations.append(y_max_index)

                voltage, current = DC_unit.get_voltage_and_current()
                alignment_voltage[laser] = voltage
                alignment_current[laser] = current

                utils.ramp_current(DC_unit, vcsel_biases[laser], 0)
                laser_control.turn_off_all_lasers()

                save_alignment(
                    alignment_figure_obj,
                    alignment_voltage,
                    alignment_current,
                    vcsel_chip,
                    measurement_timestamp,
                    meas_output_dir_path
                )

            if run_measurement:
                vp.message('Running measurement')

                spr_figure = SPR_figure(integrate_over_um)
                results['fig_object'] = spr_figure.fig

                frame_counter = 0

                # MAIN MEASUREMENT LOOP
                while (time.time() - measurement_time_start) < measurement_time:
                    loop_start = time.time()

                    for laser in lasers_on_chip:
                        laser_control.switch_to_laser(laser)
                        utils.ramp_current(DC_unit, 0, vcsel_biases[laser])

                        image_array = cam.grab(1)
                        image = image_array[0]

                        utils.ramp_current(DC_unit, vcsel_biases[laser], 0)

                        frame_time = time.time() - measurement_time_start

                        results['frame_time'][laser].append(frame_time)
                        x_spr = spr_figure.analyze_image(
                            image,
                            laser_locations[laser],
                            frame_counter,
                            IPV_config,
                            start_cropped_image_from,
                            stopp_cropped_image_from,
                            start_look_for_dip_from,
                            stopp_look_for_dip_from,
                            width_around_SPR_dip_um
                        )
                        results['spr_data'][laser].append(x_spr)

                    spr_figure.update_spr_trace(
                        lasers_on_chip,
                        results,
                        colors,
                        frame_counter,
                        start_trace=0,
                        clear_trace=False
                    )

                    elapsed = time.time() - loop_start
                    # NEW: print timing similar to old "grabbing image took"
                    print(f"Frame {frame_counter}: loop took {elapsed:.2f} s")

                    if elapsed < measurement_interval:
                        time.sleep(measurement_interval - elapsed)

                    frame_counter += 1

        except KeyboardInterrupt:
            print('Keyboard interrupt detected, stopping.')
        except Exception:
            traceback.print_exc()
        if (time.time() - measurement_time_start) >= measurement_time:
            print(f"Measurement time reached ({measurement_time} s)")

    laser_control.turn_off_all_lasers()
    # save_results(IPV_config, results, measurement_timestamp, meas_output_dir_path)
    return results


# ---------------------------------------------------------------------------
# Saving helpers
# ---------------------------------------------------------------------------


def save_results(IPV_config, results, measurement_timestamp, meas_output_dir_path):
    print(f'Saving Data to {meas_output_dir_path}')

    for laser_idx, _ in results['frame_list'].items():
        frame_list = results['frame_list'][laser_idx]
        frame_time = results['frame_time'][laser_idx]
        spr_data = results['spr_data'][laser_idx]

        if IPV_config['save_raw_images']:
            for i, im in enumerate(frame_list):
                iio.imwrite(
                    os.path.join(meas_output_dir_path, f'image{i}.png'),
                    im
                )

        if len(frame_time) > len(spr_data):
            frame_time = frame_time[:-1]
        elif len(frame_time) < len(spr_data):
            spr_data = spr_data[:-1]

        print("DEBUG shapes:", np.shape(frame_time), np.shape(spr_data))

        xy = np.vstack((frame_time, spr_data)).T
        np.savetxt(
            os.path.join(meas_output_dir_path, f'VCSEL_{laser_idx}.txt'),
            xy,
            delimiter=','
        )


def save_alignment(alignment_figure_obj,
                   alignment_voltage,
                   alignment_current,
                   vcsel_chip,
                   measurement_timestamp,
                   meas_output_dir_path):
    vp.headline(f'Saving alignment data to {meas_output_dir_path}')

    save_folder_alignment = Path(meas_output_dir_path, 'alignment_vcsel_chip')
    save_folder_alignment.mkdir(parents=True, exist_ok=True)

    alignment_png = Path(save_folder_alignment, 'alignment_image.png')
    alignment_csv = Path(save_folder_alignment, 'alignment_bias.csv')

    alignment_figure_obj.fig.savefig(alignment_png, format='png', dpi=300)

    alignment_bias = np.vstack((alignment_voltage, alignment_current)).T
    np.savetxt(
        alignment_csv,
        alignment_bias,
        delimiter=',',
        header='Voltage,Current',
        comments=''
    )

