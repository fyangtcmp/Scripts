from pymatgen.io.vasp import Vasprun
from pymatgen.electronic_structure.plotter import DosPlotter
import matplotlib.pyplot as plt

try:
    Emin, Emax = map(int, input('Emin Emax:').split())
except:
    print('Input error, use default Erange [-3 3]')
    Emin = -3
    Emax =  3

v = Vasprun('./vasprun.xml',parse_potcar_file=False)
cdos = v.complete_dos
dos = cdos.get_element_dos()
plotter = DosPlotter()
plotter.add_dos_dict(dos)
plotter.get_plot(xlim=[Emin, Emax])
plt.savefig('pdos_element.png')
