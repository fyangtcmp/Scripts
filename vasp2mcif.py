from pymatgen.io.vasp import Outcar
from pymatgen.io.cif import CifWriter
from pymatgen.core.structure import Structure

# 
struc = Structure.from_file('POSCAR')
outcar = Outcar('OUTCAR')
magmom_fullout = outcar.magnetization

for i in range(struc.num_sites):
    struc.sites[i].properties['magmom'] = magmom_fullout[i]['tot']

cifname = struc.formula.replace(" ", "_")
CifWriter(struc, write_magmoms=True).write_file(cifname + '.mcif')



