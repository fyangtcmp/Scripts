import matplotlib.pyplot as plt
from pymatgen.io.vasp.outputs import Vasprun
from pymatgen.electronic_structure.plotter import BSDOSPlotter,BSPlotter

try:
    Emin, Emax = map(float, input('Emin Emax:').split())
except:
    print('Input error, use default Erange [-3 3]')
    Emin = -3
    Emax =  3

vasprun  = Vasprun("./vasprun.xml",parse_projected_eigen=True,parse_potcar_file=False)
bs_data  = vasprun.get_band_structure(line_mode=1)
dos_data = vasprun.complete_dos

for i in range(len(bs_data.branches)):
    kpath_name = bs_data.branches[i]['name']
    kp_name = kpath_name.split("-")
    for j in [0, 1]:
        if len(kp_name[j]) > 1:
            kp_name[j] = "$\\"+kp_name[j].capitalize()+"$"
    bs_data.branches[i]['name'] = kp_name[0] + "-" + kp_name[1]


plt_1=BSDOSPlotter(fig_size=(10,10),
        bs_projection   = "elements",
        vb_energy_range =-Emin,
        cb_energy_range = Emax)
plt_1.get_plot(bs=bs_data, dos=dos_data)
ax = plt.gca()
ax.set_xlabel("")
ax.set_ylabel("E(eV)")
plt.rcParams["font.family"] = "Times New Roman"
plt.savefig('band_proj.png', dpi=300)

plt_2 = BSPlotter(bs=bs_data)
plt_2.get_plot(ylim = [Emin,Emax])
ax = plt.gca()
ax.set_xlabel("")
ax.set_ylabel("E(eV)")
ax.get_legend().remove()
plt.gcf().set_size_inches(10,10)
plt.rcParams["font.family"] = "Times New Roman"
plt.savefig('band.png', dpi=300, bbox_inches = 'tight')

