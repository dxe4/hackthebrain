from liblo import *
import sys
import os
import time
import copy
import serial
import requests


try:
    ser = serial.Serial(sys.argv[1], 9600)
except IndexError:
    ser = serial.Serial('/dev/ttyACM1', 9600)


SLEEP_TIME = 3
ARDUINO_MINIMUM_COUNT = 10
USED_ARDUINO = False
ARDUINO_USED_ONE_TIME = False
ARDUINO_DISABLED = False
HACk = False
all_count = 0

alpha_sums = []
beta_sums = []
theta_sums = []


class MuseServer(ServerThread):

    def __init__(self, port=4444):
        self.signal = {}
        self.signal['eeg'] = []
        self.signal['alpha_rel'] = []
        self.signal['alpha_abs'] = []
        self.signal['conc'] = []
        self.signal['mel'] = []
        self.signal['mel'] = []
        self.signal['beta_abs'] = []
        self.signal['theta_abs'] = []

        ServerThread.__init__(self, port)

    # receive accelrometer data
    @make_method('/muse/acc', 'fff')
    def acc_callback(self, path, args):
        acc_x, acc_y, acc_z = args
        # print "%s %f %f %f" % (path, acc_x, acc_y, acc_z)

    # receive EEG data
    @make_method('/muse/eeg', 'ffff')
    def eeg_callback(self, path, args):
        self.signal['eeg'].append(args)

        # receive alpha relative data
    @make_method('/muse/elements/alpha_relative', 'ffff')
    def alpha_callback(self, path, args):
        self.signal['alpha_rel'].append(args)

    @make_method('/muse/elements/alpha_absolute', 'ffff')
    def alpha_abs_callback(self, path, args):
        self.signal['alpha_abs'].append(args)

    @make_method('/muse/elements/beta_absolute', 'ffff')
    def beta_abs_callback(self, path, args):
        self.signal['beta_abs'].append(args)

    @make_method('/muse/elements/theta_absolute', 'ffff')
    def theta_abs_callback(self, path, args):
        self.signal['theta_abs'].append(args)

    # receive alpha relative data
    @make_method('/muse/elements/experimental/concentration', 'f')
    def concentration_callback(self, path, args):
        self.signal['conc'].append(args[0])

    # receive mellow data - viewer is the same as concentration
    @make_method('/muse/elements/experimental/mellow', 'f')
    def mellow_callback(self, path, args):
        self.signal['mel'].append(args[0])
    # handle unexpected messages

    @make_method(None, None)
    def fallback(self, path, args, types, src):
        test = args
        # print "Unknown message \n\t Source: '%s' \n\t Address: '%s' \n\t Types: '%s ' \n\t Payload: '%s'" %
        # (src.url, path, types, args)


def safe_device(a, b):
    try:
        return a / b
    except Exception as e:
        print(e)
        return 0


def get_signal_data(server, signal):
    data = copy.copy(server.signal[signal])
    server.signal[signal] = []
    _sum = 0
    count = 0
    for i in data:
        _sum += sum(i)
        count += len(i)
    if count == 0:
        return count
    return _sum / count

if __name__ == "__main__":
    current_count = 0
    try:
        server = MuseServer()
    except ServerError, err:
        raise
        print str(err)
        sys.exit()
    server.start()

    while True:
        HACk = False
        time.sleep(SLEEP_TIME)
        all_count += 1

        alpha_sum = get_signal_data(server, 'alpha_abs')
        beta_sum = get_signal_data(server, 'beta_abs')
        theta_sum = get_signal_data(server, 'theta_abs')

        alpha_sums.append(alpha_sum)
        beta_sums.append(beta_sum)
        theta_sums.append(theta_sum)

        # beta / alpha + theta 0.3

        print("alpha", alpha_sums[-1])
        print("beta", beta_sums[-1])
        print("theta", theta_sums[-1])
        # print("theta/beta", theta_sums[-1] / beta_sums[-1])
        # print("ration 2", beta_sums[-1] / (theta_sums[-1] + alpha_sums[-1]))
        current_count += 1

        try:
            data = {
                'alpha': alpha_sums[-1],
                'beta': beta_sums[-1],
                'beta_theta_ratio': safe_device(theta_sums[-1], beta_sums[-1]),
                'beta_alpha_theta_ratio': safe_device(beta_sums[-1], (theta_sums[-1] + alpha_sums[-1])),
            }

            if safe_device(theta_sums[-1], beta_sums[-1]) < 1.5 and not ARDUINO_USED_ONE_TIME and current_count == 20:
                data['beta_theta_ratio'] = 1.6
                HACk = True

            requests.post("http://127.0.0.1:8000/api/brain-data", data=data)
        except Exception as e:
            # dont want this to stop the loop
            print(e)

        if current_count < ARDUINO_MINIMUM_COUNT and USED_ARDUINO and not HACk:
            USED_ARDUINO = False
            continue

        if ARDUINO_DISABLED and not HACk:
            continue

        if safe_device(theta_sums[-1], beta_sums[-1]) > 1.5 or HACk:
            current_count = 0
            ARDUINO_USED_ONE_TIME = True
            ser.write("s")
