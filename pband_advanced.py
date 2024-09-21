import warnings
import numpy as np
from typing import Literal

import matplotlib.lines as mlines
import matplotlib.pyplot as plt
from matplotlib import rcParams

from pymatgen.electronic_structure.plotter import BSPlotterProjected
from pymatgen.electronic_structure.core import Spin

class BSPlotterProjected_dev(BSPlotterProjected):
    def __init__(self, bs, font_size=24, font_name='Arial') -> None:
        """
        Args:
            bs: A BandStructureSymmLine object with projections.
        """

        self._bs = bs
        self._nb_bands = bs.nb_bands

        self.fig_size = (10,8)
        self.font_size = font_size
        self.font_name = font_name
        self.egrid_interval = 2
        self.ribbon_factor  = 0.05
        self.bubble_factor  = 50
        self.color_list = ['#FD6D5A', '#6DC354', '#518CD8', '#FEB40B', '#994487',  '#443295'] # 红 绿 蓝 黄 紫 靛

    def _make_ticks(self, ax: plt.Axes, emin, emax) -> plt.Axes:
        # initialize all the k-point labels and k-point x-distances for bs plot
        xlabels = []  # all symmetry point labels on x-axis
        xlabel_distances = []  # positions of symmetry point x-labels

        x_distances_list = []
        prev_right_klabel = None  # used to determine which branches require a midline separator

        for branch in self._bs.branches:
            x_distances = []

            # get left and right kpoint labels of this branch
            left_k, right_k = branch["name"].split("-")

            # add $ notation for LaTeX kpoint labels
            if len(left_k) > 1:
                left_k  = "$\\"+left_k.capitalize() +"$"
            if len(right_k) > 1:
                right_k = "$\\"+right_k.capitalize()+"$"

            # add left k label to list of labels
            if prev_right_klabel is None:
                xlabels.append(left_k)
                xlabel_distances.append(0)
            elif prev_right_klabel != left_k:  # used for pipe separator
                xlabels[-1] = f"{xlabels[-1]}$\\mid$ {left_k}"

            # add right k label to list of labels
            xlabels.append(right_k)
            prev_right_klabel = right_k

            # add x-coordinates for labels
            left_kpoint = self._bs.kpoints[branch["start_index"]].cart_coords
            right_kpoint = self._bs.kpoints[branch["end_index"]].cart_coords
            distance = np.linalg.norm(right_kpoint - left_kpoint)
            xlabel_distances.append(xlabel_distances[-1] + distance)

            # add x-coordinates for kpoint data
            npts = branch["end_index"] - branch["start_index"]
            distance_interval = distance / npts
            x_distances.append(xlabel_distances[-2])
            for _ in range(npts):
                x_distances.append(x_distances[-1] + distance_interval)
            x_distances_list.append(x_distances)

        rcParams['font.size'] = self.font_size
        rcParams['font.sans-serif'] = self.font_name
        rcParams["legend.loc"] = 'center right'

        ax.set_xlim(0, x_distances_list[-1][-1])
        ax.set_xticks(xlabel_distances)
        ax.set_xticklabels(xlabels)

        ax.set_ylabel("E(eV)")
        ax.set_ylim(emin + emin/10, emax + emax/10)
        ax.set_yticks(np.arange(emin , emax + 1e-5 , self.egrid_interval))
        ax.set_yticklabels(np.arange(emin , emax + 1e-5, self.egrid_interval))
        # ax.set_axisbelow(b=True)
        ax.grid(color='gray', linestyle="dotted", linewidth=1)
        return ax
    
    def _rgbline(ax, k, e, red, green, blue, alpha=1, linestyles="solid") -> None:
        """An RGB colored line for plotting.
        creation of segments based on:
        http://nbviewer.ipython.org/urls/raw.github.com/dpsanders/matplotlib-examples/master/colorline.ipynb.

        Args:
            ax: matplotlib axis
            k: x-axis data (k-points)
            e: y-axis data (energies)
            red: red data
            green: green data
            blue: blue data
            alpha: alpha values data
            linestyles: linestyle for plot (e.g., "solid" or "dotted").
        """
        pts = np.array([k, e]).T.reshape(-1, 1, 2)
        seg = np.concatenate([pts[:-1], pts[1:]], axis=1)

        nseg = len(k) - 1
        r = [0.5 * (red[i] + red[i + 1]) for i in range(nseg)]
        g = [0.5 * (green[i] + green[i + 1]) for i in range(nseg)]
        b = [0.5 * (blue[i] + blue[i + 1]) for i in range(nseg)]
        a = np.ones(nseg, float) * alpha
        lc = LineCollection(seg, colors=list(zip(r, g, b, a)), linewidth=2, linestyles=linestyles)
        ax.add_collection(lc)

    def _get_colordata(bs, elements, bs_projection):
        """Get color data, including projected band structures.

        Args:
            bs: Bandstructure object
            elements: elements (in desired order) for setting to blue, red, green
            bs_projection: None for no projection, "elements" for element projection

        Returns:
            Dictionary representation of color data.
        """
        contribs = {}
        if bs_projection and bs_projection.lower() == "elements":
            projections = bs.get_projection_on_elements()

        for spin in (Spin.up, Spin.down):
            if spin in bs.bands:
                contribs[spin] = []
                for band_idx in range(bs.nb_bands):
                    colors = []
                    for k_idx in range(len(bs.kpoints)):
                        if bs_projection and bs_projection.lower() == "elements":
                            c = [0, 0, 0, 0]
                            projs = projections[spin][band_idx][k_idx]
                            # note: squared color interpolations are smoother
                            # see: https://youtu.be/LKnqECcg6Gw
                            projs = {k: v**2 for k, v in projs.items()}
                            total = sum(projs.values())
                            if total > 0:
                                for idx, e in enumerate(elements):
                                    c[idx] = math.sqrt(projs[e] / total)  # min is to handle round errors

                            c = [
                                c[1],
                                c[2],
                                c[0],
                                c[3],
                            ]  # prefer blue, then red, then green or magenta, then yellow, then cyan, then black
                            if len(elements) == 4:
                                # convert cmyk to rgb
                                c = [(1 - c[0]) * (1 - c[3]), ((1 - c[1]) * (1 - c[3])), ((1 - c[2]) * (1 - c[3]))]
                            else:
                                c = [c[0], c[1], c[2]]

                        else:
                            c = [0, 0, 0] if spin == Spin.up else [0, 0, 1]  # black for spin up, blue for spin down

                        colors.append(c)

                    contribs[spin].append(colors)
                contribs[spin] = np.array(contribs[spin])

        return contribs

    def get_plot(
        self,
        zero_to_efermi: bool = True,
        emin: float = -4,
        emax: float =  4,
    ):
        
        fig = plt.figure(figsize=self.fig_size)
        ax  = plt.subplot()
        
        self._make_ticks(ax, emin, emax)   
        data = self.bs_plot_data(zero_to_efermi)

        # Walk through high symmetry points of the band structure
        # (Gamma->X, X->M, ...)
        for k_path_idx in range(len(data["distances"])):
            for band_idx in range(self._nb_bands):
                ax.plot(
                    data["distances"][k_path_idx],
                    data["energy"][str(Spin.up)][k_path_idx][band_idx],
                    "k-",
                    linewidth=1,
                )

        return ax

    def get_projected_plot(
        self,
        dictio: dict[str, list],
        zero_to_efermi: bool = True,
        emin: float = -4,
        emax: float =  4,
        style: Literal['ribbon', 'bubble', 'line'] = 'line'
    ):
        """Generate a plot with subplots for each element-orbital pair.

        The orbitals are named as in the FATBAND file, e.g. "2p" or "2p_x".

        he blue and red colors are for spin up and spin down
        The size of the dot in the plot corresponds to the value
        for the specific point.

        Args:
            dictio: The element and orbitals you want a projection on. The
                format is {Element: [*Orbitals]} for instance
                {"Cu":["d", "s"], "O":["p"]} will yield projections for
                Cu on d and s orbitals and oxygen on p.
            zero_to_efermi: Set the Fermi level as the plot's origin
                (i.e. subtract E_f). Defaults to True.

        Returns:
            ax
        """
        
        fig = plt.figure(figsize=self.fig_size)
        ax  = plt.subplot()
        
        self._make_ticks(ax, emin, emax)
        data = self.bs_plot_data(zero_to_efermi)

        if style == 'line':
            self.ribbon_factor = 0.02
        else:
            # Walk through high symmetry points of the band structure
            # (Gamma->X, X->M, ...)
            for k_path_idx in range(len(data["distances"])):
                for band_idx in range(self._nb_bands):
                    ax.plot(
                        data["distances"][k_path_idx],
                        data["energy"][str(Spin.up)][k_path_idx][band_idx],
                        "k-",
                        linewidth=1,
                    )
        
        proj = self._get_projections_by_branches(dictio)
        handles = []
        for ie, element in enumerate(dictio):
            handles.append(mlines.Line2D([], [], lw=2, ls='-', color=self.color_list[ie], label=element)) 

        leg = ax.legend(handles=handles)
        [line.set_linewidth(6) for line in leg.get_lines()]

        # Walk through high symmetry points of the band structure
        # (Gamma->X, X->M, ...)
        for k_path_idx in range(len(data["distances"])):
            for band_idx in range(self._nb_bands):
                proj_branch = proj[k_path_idx][str(Spin.up)][band_idx]
                for ie, element in enumerate(dictio):
                    weight = []
                    orbitals = dictio[element]
                    for proj_ik in proj_branch:
                        weight_sum = 0
                        for iorb in orbitals:
                            weight_sum += proj_ik[element][iorb]
                        weight.append(weight_sum)

                    weight = np.array(weight)

                    if style == 'ribbon' or style == 'line':
                        ax.fill_between(
                            data["distances"][k_path_idx],
                            data["energy"][str(Spin.up)][k_path_idx][band_idx]-weight*self.ribbon_factor,
                            data["energy"][str(Spin.up)][k_path_idx][band_idx]+weight*self.ribbon_factor,
                            color=self.color_list[ie],
                            alpha=1
                        )
                        
                    elif style == 'bubble':
                        ax.scatter(
                            data["distances"][k_path_idx],
                            data["energy"][str(Spin.up)][k_path_idx][band_idx],
                            s=weight*self.bubble_factor,
                            marker='o',
                            color=self.color_list[ie],
                        )
                    else:
                        continue

        return ax

if __name__ == '__main__':
    import argparse
    from pymatgen.io.vasp.outputs import Vasprun

    parser = argparse.ArgumentParser()
    parser.add_argument("-e", nargs=2, type=float, default=[-4,4], help="set the energy range")
    parser.add_argument("-p", "--proj",help="specify the projections, like 'Fe:s,d;Se:p'")
    parser.add_argument("-s", "--style", choices=['ribbon', 'bubble', 'line'], default='line', help="the style to plot the projections")

    args = parser.parse_args()

    if args.e:
        Emin = args.e[0]
        Emax = args.e[1]

    # target_proj = {'Fe':['s','d'],'Se':['p']}
    target_proj = {}
    if args.proj:
        elts = args.proj.split(';')
        for ie in elts:
            elt_name = ie.split(':')[0]
            orbs = ie.split(':')[1]
            target_proj[elt_name] = orbs.split(',')
    else:
        from pymatgen.core.structure import Structure
        struc = Structure.from_file('POSCAR')
        for ie in struc.elements:
            target_proj[ie.symbol] = ['s','p','d','f']

    vasprun  = Vasprun("./vasprun.xml",parse_projected_eigen=True,parse_potcar_file=False)
    bs_data  = vasprun.get_band_structure(line_mode=1)    

    BSobj = BSPlotterProjected_dev(bs=bs_data)
    axes = BSobj.get_projected_plot(target_proj, emin=Emin, emax=Emax, style=args.style)
    plt.savefig('pband.png', dpi=300, bbox_inches = 'tight')
