from liblo import *
import sys
import os
import time
import copy
import serial


try:
    ser = serial.Serial(sys.argv[1], 9600)
except IndexError:
    ser = serial.Serial('/dev/ttyACM1', 9600)


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


try:
    server = MuseServer()
except ServerError, err:
    raise
    print str(err)
    sys.exit()
server.start()

if __name__ == "__main__":
   # io_udp = MuseIOOSC()
   # io_udp.starit()
    while True:
        last_alpha_index = 0
        last_beta_index = 0
        time.sleep(10)
        # print server.signal['conc']
        alpha = copy.copy(server.signal['alpha_abs'])
        beta = copy.copy(server.signal['beta_abs'])
        theta = copy.copy(server.signal['theta_abs'])

        server.signal['beta_abs'] = []
        server.signal['alpha_abs'] = []
        server.signal['theta_abs'] = []

        alpha_sum = 0
        beta_sum = 0
        theta_sum = 0

        for alhpa_result in alpha:
            alpha_sum += sum(alhpa_result)

        for beta_result in beta:
            beta_sum += sum(beta_result)

        for theta_result in theta:
            theta_sum += sum(theta_result)

        alpha_sums.append(alpha_sum)
        beta_sums.append(beta_sum)
        theta_sums.append(theta_sum)

        # beta / alpha + theta 0.3

        print("alpha", alpha_sums[-1])
        print("beta", beta_sums[-1])
        print("theta", theta_sums[-1])
        print("theta/beta", theta_sums[-1] / beta_sums[-1])
        print("ration 2", beta_sums[-1] / (theta_sums[-1] + alpha_sums[-1]))
        if theta_sums[-1] / beta_sums[-1] > 1.5:
            ser.write("s")
