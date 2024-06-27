from neuron import h
from neuron.units import ms, mV, µm
from bokeh.plotting import figure, output_file, show

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

stim = h.IClamp(my_cell.dend(1))
stim.delay = 5 * ms
stim.dur = 1 * ms
stim.amp = 0.1

soma_v = h.Vector().record(my_cell.soma(0.5)._ref_v)
dend_v = h.Vector().record(my_cell.dend(0.5)._ref_v)
t = h.Vector().record(h._ref_t)

output_file("plot.html")
f = figure(x_axis_label="t (ms)", y_axis_label="v (mV)")
amps = [0.075 * i for i in range(1, 5)]
colors = ["green", "blue", "red", "black"]

for amp, color in zip(amps, colors):
    stim.amp = amp
    for nseg, width in [(1, 2), (101, 1)]:
        my_cell.dend.nseg = nseg
        h.finitialize(-65 * mV)
        h.continuerun(25 * ms)

        # 데이터를 리스트로 변환
        t_list = list(t)
        soma_v_list = list(soma_v)
        dend_v_list = list(dend_v)

        # 데이터를 Bokeh 플롯에 전달
        f.line(
            t_list, soma_v_list,
            line_width=width,
            legend_label="amp={:.3g}".format(amp) if nseg == 1 else "",
            color=color,
        )
        f.line(
            t_list, dend_v_list,
            line_width=width,
            line_dash="dashed",
            color=color
        )

show(f)
