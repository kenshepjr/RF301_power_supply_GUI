# Seren R301 RF Power Supply Controller

A Python-based GUI application for interfacing with the Seren R301 Radio Frequency Power Supply over RS232/Ethernet (via Moxa serial device server). Supports single-material depositions with a timed countdown and automated alternating-target RF sputtering sequences with shutter control.

## Features

- **Single Growth Mode**: Set RF power and deposition time; automatically opens shutter, fires the RF gun, counts down, then shuts off and closes the shutter
- **Alternating Growth Mode**: Automated multi-period switching between two RF sputtering targets with configurable power, growth time, and recovery time per target
- **Shutter Control**: Independent manual and automatic control of two relay-driven shutters via an 8-channel RS232 relay board
- **Real-time Countdown**: MM:SS countdown display for both single and alternating growth modes, with per-stage time display in alternating mode
- **Safe Shutdown**: Quit button disables the RF gun and closes all shutters before closing serial ports

## Requirements

### Hardware

- Seren R301 Radio Frequency Power Supply
- Moxa serial device server (NPort or equivalent) — tested with IDs `10.66.26.75` (BNL) and `132.198.10.14` (UVM)
- 8-Channel RS232 Control Relay Board (PMDWay SKU 16583004, 12V DC)
    - Handles up to 8 relays; 250V AC / 10A or 30V DC / 10A per relay
    - [Product page](https://pmdway.com/products/eight-channel-rs232-control-relay-board-12v-dc)
    - Board communicates via 8-byte hex commands over RS232 at 9600 baud
- Two RF sputtering guns with shutters wired to relay channels 3 and 4 of the relay board

### Software Dependencies

```
numpy
matplotlib
tkinter  (included with standard Python)
pyserial
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/kenshepjr/r301_rf_power_supply
cd r301_rf_power_supply
```

2. Install required dependencies:
```bash
pip install numpy matplotlib pyserial
```

3. Place both files in the same directory:
```
cont_R301_RF_Power_Supply_V3.py
mod_R301_RF_power_supply.py
```

4. Update the Moxa IP address and port assignments in the main script:
```python
bnl_moxa_ID = '10.66.26.75'      # Update with your Moxa server IP

moxa_ports = {
    'Power_Supply_01': 4006,      # Update with your Moxa port for the R301
    'Shutter': 4005,              # Update with your Moxa port for the relay board
}
```

## Usage

### Basic Operation

1. Connect the R301 and relay board to the Moxa serial device server
2. Update the Moxa IP and port assignments as shown above
3. Run the main application:
```bash
python cont_R301_RF_Power_Supply_V3.py
```
4. `mod_R301_RF_power_supply.py` must be in the same directory

### GUI Components

#### Single Growth Panel

| Control | Description |
|---|---|
| Power (W) | RF power setpoint sent to the R301 |
| Deposition Time (min) | Duration of the deposition in minutes |
| Enable/Disable RF Gun 01 | Manual toggle for the RF gun and shutter 01 |
| Shutter 01 | Manual toggle for shutter 01 independently |
| Start Deposition | Begins the timed deposition sequence |
| Time Left | MM:SS countdown to deposition end |

Clicking **Start Deposition** opens shutter 01, fires the RF gun, and begins a countdown. When the timer reaches zero, the RF gun is disabled and the shutter is closed automatically. A "Deposition Complete!" message is displayed for 10 seconds.

#### Alternating Growth Panel

| Control | Description |
|---|---|
| Power (W) — RF Gun 01 | Power setpoint for target 1 |
| Power (W) — RF Gun 02 | Power setpoint for target 2 |
| Growth Time (s) | Duration of each growth stage per target |
| Recovery Time (s) | Shutter-closed dwell time between targets |
| Periods (int) | Number of complete alternating cycles to run |
| Enable/Disable RF Gun 01/02 | Manual toggle for each gun and its shutter |
| Shutter 01 / Shutter 02 | Manual toggle for each shutter independently |
| Start Deposition | Begins the automated alternating sequence |
| Time Left | MM:SS overall countdown plus current stage and stage time remaining |

One period consists of four stages in order:

```
Growth 01 → Recovery 01 → Growth 02 → Recovery 02
```

At each stage transition the appropriate shutter is opened or closed and the RF gun power setpoint is updated. The RF gun is disabled during recovery stages.

#### Widget Panel

- **Clock (min)**: Elapsed time since application start
- **Data Point**: Count of update loop iterations
- **Quit**: Disables RF gun, closes both shutters, closes all serial ports, then exits

### Relay Board Shutter Commands

The `Shutter` class in `mod_R301_RF_power_supply.py` sends fixed 8-byte hex commands to the PMDWay relay board at 9600 baud. The commands are wired for relay channels 3 (Shutter 01) and 4 (Shutter 02):

| Method | Hex Command | Action |
|---|---|---|
| `open_shutter_01()` | `55 56 00 00 00 04 01 b0` | Opens relay channel 4 |
| `close_shutter_01()` | `55 56 00 00 00 04 02 b1` | Closes relay channel 4 |
| `open_shutter_02()` | `55 56 00 00 00 03 01 af` | Opens relay channel 3 |
| `close_shutter_02()` | `55 56 00 00 00 03 02 b0` | Closes relay channel 3 |

If your shutters are wired to different relay channels you will need to update these hex values. Refer to the PMDWay relay board manual for the command format.

## File Structure

### `cont_R301_RF_Power_Supply_V3.py`

Main application file containing:

- `R301_RFPS_GUI`: GUI class managing all user interface elements, button callbacks, countdown logic, and the alternating growth state machine
- `Data_Structure_RFPS`: Data storage class holding `tk.DoubleVar` dictionaries for single growth and alternating growth setpoints and read-only values
- `initialize_controllers()`: Opens serial connections to the power supply and relay board; disables the RF gun and closes both shutters on startup
- Main program block: Configures the Moxa connection, builds the Tkinter window, wires setpoint traces to `PS.set_power()`, and runs the update loop at 100ms

### `mod_R301_RF_power_supply.py`

Hardware interface module containing:

- `R301_Radio_Frequency_Power_Supply`: Serial communication class for the Seren R301
    - Asserts serial control (`***\r`) on instantiation
    - Methods: `enable_RF_gun()`, `disable_RF_gun()`, `set_power()`, `enable_pulse_mode()`, `disable_pulse_mode()`, `set_high_power()`, `set_low_power()`, `set_high_time()`, `set_duty_cycle()`, `query_instrument()`, `close_port()`
- `Shutter`: Serial communication class for the 8-channel relay board
    - Methods: `open_shutter_01()`, `close_shutter_01()`, `open_shutter_02()`, `close_shutter_02()`, `close_port()`
- Module-level byte constants for all R301 commands

## Communication Protocol — Seren R301

The R301 uses a plain ASCII serial protocol at 19200 baud, 8N1. Commands are terminated with CR (`\r`). Serial control must be asserted first by sending `***\r`.

### Serial Settings

| Parameter | Value |
|---|---|
| Baud rate | 19200 |
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |
| Timeout | 1 second |

### Supported Commands

| Command | Bytes Sent | Description |
|---|---|---|
| Assert serial | `***\r` | Enables serial control; required on connect |
| RF on | `G\r` | Enables the RF output |
| RF off | `S\r` | Disables the RF output |
| Set power | `<W> W\r` | Sets forward power setpoint in watts (integer) |
| Set voltage | `<V> V\r` | Sets voltage setpoint |
| Query | `Q\r` | Returns status string (fwd power, ref power, max power) |
| Pulse on | `+P\r` | Enables pulse mode |
| Pulse off | `-P\r` | Disables pulse mode |
| Set duty cycle | `<D> D\r` | Sets pulse duty cycle |
| Set high time | `<HT> HT\r` | Sets pulse high time |
| Set high power | `<HP> HP\r` | Sets pulse high power level |
| Set low power | `<LP> LP\r` | Sets pulse low power level |
| Echo on | `ECHO\r` | Enables command echo |
| Echo off | `NOECHO\r` | Disables command echo |

## Known Issues in Current Code

The following bugs exist in `mod_R301_RF_power_supply.py` and have not yet caused runtime failures only because the affected methods are not called in the current GUI workflows:

- `disable_echo()`: Method body is empty — sends nothing
- `set_voltage()`: Typo `comannd` on assignment but `command` used in `self.ser.write(command)` — will raise `NameError` if called
- `set_duty_cycle()`: Typo `duty_cyle` — will raise `NameError` if called

## Multi-Controller Synchronization

A file-based synchronization scaffold is present but fully commented out in all versions. It was intended to coordinate startup across multiple instrument controllers by writing to a shared `controller_ready.txt` file. It is not active and does not need to be enabled for standalone use.

Expected controllers when the sync system is active:
- `Substrate_Heater_Controller`
- `TPG261_Controller`
- `MKS_Pressure_Controller`
- `BKP_Arb_Waveform_Controller`
- `Ircon_Modline_Plus_Controller`

## Version History

### V2 — `cont_R301_RF_Power_Supply_V2.py`

Initial working GUI. Key characteristics and limitations:

- Single growth panel and a partial alternating growth panel layout
- `PS` and `shutter` objects were global variables; the `R301_RFPS_GUI` class accessed them directly rather than receiving them as arguments — tight coupling that made the class non-portable
- Alternating growth panel used `self.keys` (the single growth keys) for its entry widgets instead of a separate `alt_keys` list — entries were bound to the wrong variables
- `Data_Structure_RFPS` had no `alt_input_var` dictionary; alternating growth parameters were not stored separately
- Countdown for single growth worked; alternating growth sequence was not yet functional
- `GUI[PS]` key used the `PS` object as a dict key (instead of the string `'PS'`), which caused a silent bug in the window dictionary
- Multi-controller sync code present but commented out

### V3 — `cont_R301_RF_Power_Supply_V3.py` *(latest working version)*

Major rewrite of the GUI architecture and alternating growth logic:

- `PS` and `shutter` are now passed as constructor arguments to `R301_RFPS_GUI` and stored as `self.PS` and `self.shutter` — however, the internal methods still reference the outer-scope `PS` and `shutter` globals; full encapsulation is not yet complete
- `Data_Structure_RFPS` now has a separate `alt_input_var` and `alt_read_only` dictionary using `alt_keys`: `['setpoint_power_01', 'growth_period_01', 'setpoint_power_02', 'growth_period_02', 'recovery_time', 'num_periods']`
- Alternating growth panel correctly uses `alt_keys` and `alt_entry` for its entry widgets
- Alternating growth state machine implemented in `update_countdown_alt_growth()` with four named stages (`Growth 01`, `Recovery 01`, `Growth 02`, `Recovery 02`) and a period counter `self.N`
- `growth_recipe()` helper handles per-stage hardware actuation: power setpoint updates, RF enable/disable, shutter open/close
- Per-stage countdown display: `Time Left: MM:SS | Stage: <name> (<N>s left)`
- `deposition_complete()` separated into its own method
- GUI dict key corrected to string `'PS'`
- `initialize_controllers()` now explicitly calls `PS.disable_RF_gun()` on startup
- Two Moxa IP addresses defined (`uvm_moxa_ID`, `bnl_moxa_ID`) for portability between sites
- Power setpoint traces added for both `setpoint_power_01` and `setpoint_power_02` in the alternating growth panel
- Multi-controller sync code present but commented out

### V4 — `cont_R301_RF_Power_Supply_V4_WIP.py` *(work in progress — untested)*

The V4 file is structurally identical to V3 at the time of writing. It is the working branch for testing updates to the automated RF gun switching logic in the alternating growth sequence. No functional differences from V3 have been committed to this file yet. Do not use V4 in production until testing is complete.

## Configuration Options

### Serial Settings — Shutter Relay Board

| Parameter | Value |
|---|---|
| Baud rate | 9600 |
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |
| Timeout | 1 second |

### Update Loop

- Interval: 100ms (10 Hz), configured via `dt = 1000 // 10`
- Updates the elapsed clock display and data point counter only; instrument readback is not yet implemented in the loop

## License

This project is licensed under the MIT License — see the LICENSE file for details.

## Author

Kenneth Shepherd Jr

## Support

For issues, questions, or contributions, open an issue on the GitHub repository or contact the author. Manuals for the R301 power supply and the relay board should be placed in the `manuals/` directory.
