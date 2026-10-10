

import logging
import moku
import requests
import csv
from pprint import pprint
from datetime import datetime
from moku.instruments import Oscilloscope



FORMAT = '%(asctime)-15s %(name)s: %(message)s'
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.INFO)


HIGH_RANGE_LSB_VOLT = (2**11 - 1) / 25.0
LOW_RANGE_LSB_VOLT = (2**11 - 1) / 5.0
DAC_LSB_VOLT = (2**11 - 1) / 5.0
OFFSET_FRAC = 16.0
UNITY_GAIN = 0x400
INPUT_VOLTS = 1.0

colours = [
    ('Unknown', '999999'),
    ('White', 'ffffff'),
    ('Black', '000000'),
    ('Storm (dark blue)', '5f7a9d'),
    ('Sage (light green)', 'c1d2c7'),
    ('Fire (orange)', 'f46c63'),
    ('Blush (pink)', 'ecb3cb')
]

def export_cal_data(m, hg0, ho0, lg0, lo0, hg1, ho1, lg1, lo1):
    # Export calibration data and SN to CSV file
    with open('calibration_data.csv', 'a') as f:
        writer = csv.writer(f, lineterminator = '\n')
        writer.writerow([m.serial_number(), hg0, ho0, lg0, lo0, hg1, ho1, lg1, lo1])


def get_calibration(ip):
    # Uses Tweaks (experimental) API
    cal = requests.get(f"http://{ip}/tweaks/calibration").json()
    return cal

def set_calibration(ip, cal):
    requests.post(f"http://{ip}/tweaks/calibration", json={"write_eeprom": True, "data": cal})

def redeploy(uid, out_volts=1.0, high_range=True):
    # Deploy scope
    i = Oscilloscope(uid, force_connect=True)
    i.set_acquisition_mode(mode="Precision")
    i.set_frontend(1, "1MOhm", "DC", "50Vpp" if high_range else "10Vpp")
    i.set_frontend(2, "1MOhm", "DC", "50Vpp" if high_range else "10Vpp")
    i.set_timebase(-1e-2, 1e-2)

    # Generate DC signal on output
    i.generate_waveform(1, "DC", dc_level=out_volts)
    i.generate_waveform(2, "DC", dc_level=out_volts)
    return i

def dc_volts(osc):
    data = osc.get_data()
    c1, c2 = data['ch1'], data['ch2']
    Vch0 = sum(c1) / len(c1)
    Vch1 = sum(c2) / len(c2)
    return Vch0, Vch1


def _calc_coeffs(a, b, lsbs_per_volt):
    # in volts
    g = (2.0 * INPUT_VOLTS) / (a - b)  # gain relative to nominal 1.0
    o = -(a + b) / 2.0

    # in regs
    g = int(round(UNITY_GAIN * g))
    o = int(round(o * lsbs_per_volt * OFFSET_FRAC))

    # clipped
    g = min(2047, max(0, g))
    o = min(4095, max(-4096, o))

    # check gain and offset calibration values
    if (g > 1200 or g < 800):
            log.warning('Gain calibration out of bounds, please check inputs and recalibrate')

    if (o > 200 or o < -250):
            log.warning('Offset calibration out of bounds, please check inputs and recalibrate')

    return g, o


def main(uid):
    input("Apply +{:3.1f}V DC to both inputs... [enter]".format(INPUT_VOLTS))
    osc = redeploy(uid, out_volts=1.0, high_range=True)
    a0, a1 = dc_volts(osc)

    # check input 1 and 2 if +1V is applied
    if a0 < 0.95 or a0 > 1.05:
        log.warning('+1 V not applied to input 1, please check supply and recalibrate')
    if a1 < 0.95 or a1 > 1.05:
        log.warning('+1 V not applied to input 2, please check supply and recalibrate')

    osc = redeploy(uid, out_volts=1.0, high_range=False)
    c0, c1 = dc_volts(osc)

    e0 = float(input("What is Output 1 voltage? "))
    e1 = float(input("What is Output 2 voltage? "))

    input("Apply -{:3.1f}V DC to both inputs... [enter]".format(INPUT_VOLTS))
    osc = redeploy(uid, out_volts=-1.0, high_range=True)
    b0, b1 = dc_volts(osc)

    # check input 1 and 2 if -1V is applied
    if b0 < -1.05 or b0 > -0.95:
        log.warning('-1 V not applied to input 1, please check supply and recalibrate')
    if b1 < -1.05 or b1 > -0.95:
        log.warning('-1 V not applied to input 2, please check supply and recalibrate')

    osc = redeploy(uid, out_volts=-1.0, high_range=False)
    d0, d1 = dc_volts(osc)

    f0 = float(input("What is Output 1 voltage? "))
    f1 = float(input("What is Output 2 voltage? "))

    cal = get_calibration(uid)

    high_g0, high_o0 = _calc_coeffs(a0, b0, HIGH_RANGE_LSB_VOLT)
    low_g0, low_o0 = _calc_coeffs(c0, d0, LOW_RANGE_LSB_VOLT)

    cal['ADC']['0'] = {'AC': {'14': [high_g0, high_o0, 128.0, 0x400, HIGH_RANGE_LSB_VOLT],
                              '0': [low_g0, low_o0, 128.0, 0x400, LOW_RANGE_LSB_VOLT]},
                       'DC': {'14': [high_g0, high_o0, 128.0, 0x400, HIGH_RANGE_LSB_VOLT],
                              '0': [low_g0, low_o0, 128.0, 0x400, LOW_RANGE_LSB_VOLT]}}

    high_g1, high_o1 = _calc_coeffs(a1, b1, HIGH_RANGE_LSB_VOLT)
    low_g1, low_o1 = _calc_coeffs(c1, d1, LOW_RANGE_LSB_VOLT)
    export_cal_data(osc, high_g0, high_o0, low_g0, low_o0, high_g1, high_o1, low_g1, low_o1)

    cal['ADC']['1'] = {'AC': {'14': [high_g1, high_o1, 128.0, 0x400, HIGH_RANGE_LSB_VOLT],
                              '0': [low_g1, low_o1, 128.0, 0x400, LOW_RANGE_LSB_VOLT]},
                       'DC': {'14': [high_g1, high_o1, 128.0, 0x400, HIGH_RANGE_LSB_VOLT],
                              '0': [low_g1, low_o1, 128.0, 0x400, LOW_RANGE_LSB_VOLT]}}

    g, o = _calc_coeffs(e0, f0, DAC_LSB_VOLT)
    cal['DAC']['0'] = [g, o, DAC_LSB_VOLT]

    g, o = _calc_coeffs(e1, f1, DAC_LSB_VOLT)
    cal['DAC']['1'] = [g, o, DAC_LSB_VOLT]

    cal['date'] = str(datetime.now())
    cal['version'] = 0

    # Choose colour
    indices = list(enumerate(colours))

    print("Select device colour:")
    for i, c in indices:
        print(f"  {i}) {c[0]}")

    print("")
    idx = input(f"0-{len(indices)-1}: ")

    try:
        hx = colours[int(idx)][1]
    except (ValueError, KeyError):
        print(f"Entered value {idx} is not valid")
        exit(1)

    cal['color'] = hx

    log.info('New Calibration is:')
    pprint(cal)

    set_calibration(uid, cal)
    osc = redeploy(uid, out_volts=0.0)

    osc.relinquish_ownership()


if __name__ == '__main__':
    import argparse  # noqa
    parser = argparse.ArgumentParser(description='Calibration')
    parser.add_argument('uid', type=str)

    args = parser.parse_args()
    main(args.uid)
