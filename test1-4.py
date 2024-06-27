from neuron import h
from neuron.units import ms, mV, µm
h.load_file("stdrun.hoc")

class BallAndStick:
    def __init__(self, gid):
        self._gid = gid
        self._setup_morphology()
        self._setup_biophysics()

    def _setup_morphology(self):
        self.soma = h.Section(name="soma", cell=self)
        self.dend = h.Section(name="dend", cell=self)
        self.all = [self.soma, self.dend]
        self.dend.connect(self.soma)
        self.soma.L = self.soma.diam = 12.6157 * µm
        self.dend.L = 200 * µm
        self.dend.diam = 1 * µm

    def _setup_biophysics(self):
        for sec in self.all:
            sec.Ra = 100
            sec.cm = 1
        self.soma.insert("hh")
        for seg in self.soma:
            seg.hh.gnabar = 0.12
            seg.hh.gkbar = 0.036
            seg.hh.gl = 0.0003
            seg.hh.el = -54.3 * mV
        self.dend.insert("pas")
        for seg in self.dend:
            seg.pas.g = 0.001
            seg.pas.e = -65 * mV

    def __repr__(self):
        return "BallAndStick[{}]".format(self._gid)

my_cell = BallAndStick(0)

import matplotlib.pyplot as plt
from neuron import gui

stim = h.IClamp(my_cell.dend(1))
stim.delay = 5
stim.dur = 1
stim.amp = 0.1

soma_v = h.Vector().record(my_cell.soma(0.5)._ref_v)
dend_v = h.Vector().record(my_cell.dend(0.5)._ref_v)
t = h.Vector().record(h._ref_t)

amps = [0.075 * i for i in range(1, 5)]
colors = ["green", "blue", "red", "black"]

plt.figure()
for amp, color in zip(amps, colors):
    stim.amp = amp
    for my_cell.dend.nseg, width in [(1, 2), (101, 1)]:
        h.finitialize(-65 * mV)
        h.continuerun(25 * ms)
        linewidth = 1 if my_cell.dend.nseg == 101 else 2
        label = f"amp={amp:.3g}" if my_cell.dend.nseg == 1 else ""
        plt.plot(t, soma_v, label=label, color=color, linewidth=linewidth)
        plt.plot(t, dend_v, color=color, linewidth=linewidth, linestyle=':')

plt.xlabel('t (ms)')
plt.ylabel('v (mV)')
plt.legend()
plt.show()