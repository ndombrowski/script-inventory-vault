#!/usr/bin/env python3
import argparse
from ete3 import Tree, TreeStyle, NodeStyle, TextFace

# ----------------------------------------------------------------------
# Color matcher function
# ----------------------------------------------------------------------
def get_color(name, color_map):
    name_lower = name.lower()
    for pattern, color in color_map.items():
        if pattern.lower() in name_lower:
            return color
    return "#000000"

# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description=(
            "Color an unrooted tree using patterns from a color file.\n"
            "--------------------------------------------------------\n"
            "\nTakes as input:\n"
            "-    iqtree treefile\n"
            "-    color file: a two column, tab-separated file with the header: label color\n"
            "         the label can be the taxon name or a pattern\n"
            "         the color should be provided as a hexcode.\n"
            "         if colors are not needed provide a empty colors file"
            "\n"
            "Outputs:\n"
            " - output.pdf\n"
            " - output.nex\n "
            "\noutput.nex can be used with `figtree -graphic PDF tree.nex tree.pdf` "
            "to generate a more nicely formatted pdf\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--tree", required=True, help="Input tree file (Newick)")
    parser.add_argument("--colors", required=True, help="Color mapping file")
    parser.add_argument("--output", required=True, help="Output PDF")
    parser.add_argument(
        "--midpoint",
        action="store_true",
        default=False,
        help="Perform midpoint rooting (optional, default: no)"
    )

    args = parser.parse_args()
    
    treefile = args.tree
    colorfile = args.colors
    midpoint = args.midpoint
    
    # ==================================================================
    # Prepare tree (for PDF)
    # ==================================================================
    # Load tree
    t = Tree(treefile)

    # Midpoint root
    if midpoint:
        R = t.get_midpoint_outgroup()
        t.set_outgroup(R)
        
    # Load color map
    color_map = {}
    with open(colorfile) as f:
        next(f)  # skip header
        for line in f:
            try:
                label, color = line.strip().split()
                color_map[label] = color
            except ValueError:
                continue

    # Assign colored text labels for PDF rendering 
    for leaf in t:
        clr = get_color(leaf.name, color_map)
        tf = TextFace(leaf.name, fsize=10)
        tf.fgcolor = clr
        leaf.add_face(tf, column=0, position="branch-right")

    # Remove node circles for all nodes
    for node in t.traverse():
        ns = NodeStyle()
        ns["size"] = 0
        node.set_style(ns)

    # Configure tree style
    ts = TreeStyle()
    ts.mode = "c"                    # circular tree
    ts.show_leaf_name = False        # use custom labels
    ts.show_branch_length = False
    ts.show_branch_support = True

    # Render to PDF
    t.render(args.output, tree_style=ts)

    # ==================================================================
    # Generate Nexus file (nexus file in FigTree format)
    # ==================================================================
    # Prepare the colored species list (TAXLABELS block)
    treenexus = t.write(format=0, format_root_node=True)
    leaves = list(t.get_leaf_names())
    listspsC = []
    
    # Iterate through leaves to get the color tag based on the pattern matcher
    for leaf_name in leaves:
        hex_color = get_color(leaf_name, color_map) 
        
        # FigTree uses a special tag for colors: 
        # '[&!color=#RRGGBB]'.
        color_tag = f"[&!color={hex_color}]"
        
        # Append the formatted label to the leaf label:
        listspsC.append(f"\t{leaf_name}{color_tag}\n")

    # Write the Nexus file
    nexus_file = args.output.rsplit(".", 1)[0] + ".nex" 
    with open(nexus_file, "w") as f:
        # NEXUS Block Start
        f.write("#NEXUS\n")
        
        # TAXA Block
        f.write("begin taxa;\n")
        f.write(f"\tdimensions ntax={len(leaves)};\n")
        f.write("\ttaxlabels\n")
        f.write("".join(listspsC)) # Write all colored labels
        f.write(";\n")
        f.write("end;\n\n")

        # TREES Block
        # The FigTree header '[&R]' indicates the tree is rooted.
        f.write("begin trees;\n")
        f.write(f"\ttree tree_1 = [&R] {treenexus}\n")
        f.write("end;\n\n")

        # FIGTREE Block (settings for FigTree viewer)
        # Note: This block has been adapted from the Perl script to match FigTree defaults
        f.write("begin figtree;\n")
        f.write("\tset appearance.backgroundColorAttribute=\"Default\";\n")
        f.write("\tset appearance.backgroundColour=#ffffff;\n")
        f.write("\tset appearance.branchColorAttribute=\"User selection\";\n")
        f.write("\tset appearance.branchColorGradient=false;\n")
        f.write("\tset appearance.branchLineWidth=1.0;\n")
        f.write("\tset appearance.branchMinLineWidth=0.0;\n")
        f.write("\tset appearance.branchWidthAttribute=\"Fixed\";\n")
        f.write("\tset appearance.foregroundColour=#000000;\n")
        f.write("\tset appearance.hilightingGradient=false;\n")
        f.write("\tset appearance.selectionColour=#2d3680;\n")
        f.write("\tset layout.expansion=0;\n")
        f.write("\tset layout.layoutType=\"RECTILINEAR\";\n") # RECTILINEAR, RADIAL
        f.write("\tset layout.zoom=0;\n")
        f.write("\tset nodeLabels.colorAttribute=\"User selection\";\n")
        f.write("\tset nodeLabels.displayAttribute=\"label\";\n")
        f.write("\tset nodeLabels.fontName=\"Calibri\";\n")
        f.write("\tset nodeLabels.fontSize=8;\n")
        f.write("\tset nodeLabels.fontStyle=0;\n")
        f.write("\tset nodeLabels.isShown=false;\n")
        f.write("\tset nodeLabels.significantDigits=4;\n")
        f.write("\tset nodeShape.colourAttribute=\"User selection\";\n")
        f.write("\tset nodeShape.isShown=false;\n")
        f.write("\tset nodeShape.minSize=10.0;\n")
        f.write("\tset nodeShape.scaleType=Width;\n")
        f.write("\tset nodeShape.shapeType=Circle;\n")
        f.write("\tset nodeShape.size=4.0;\n")
        f.write("\tset nodeShape.sizeAttribute=\"Fixed\";\n")
        f.write("\tset branchLabels.colorAttribute=\"User selection\";\n")
        f.write("\tset branchLabels.displayAttribute=\"label\";\n")
        f.write("\tset branchLabels.fontName=\"Agency FB\";\n")
        f.write("\tset branchLabels.fontSize=8;\n")
        f.write("\tset branchLabels.fontStyle=0;\n")
        f.write("\tset branchLabels.isShown=true;\n")
        f.write("\tset branchLabels.significantDigits=4;\n")
        f.write("\tset tipLabels.colorAttribute=\"User selection\";\n")
        f.write("\tset tipLabels.displayAttribute=\"Names\";\n")
        f.write("\tset tipLabels.fontName=\"Calibri\";\n")
        f.write("\tset tipLabels.fontSize=8;\n") 
        f.write("\tset tipLabels.isShown=true;\n")
        f.write("\tset legend.attribute=\"label\";\n")
        f.write("\tset legend.fontSize=10.0;\n")
        f.write("\tset legend.isShown=false;\n")
        f.write("\tset legend.significantDigits=4;\n")
        f.write("\tset nodeBars.barWidth=4.0;\n")
        f.write("\tset nodeBars.displayAttribute=null;\n")
        f.write("\tset nodeBars.isShown=false;\n")
        f.write("\tset polarLayout.alignTipLabels=false;\n")
        f.write("\tset polarLayout.angularRange=0;\n")
        f.write("\tset polarLayout.rootAngle=0;\n")
        f.write("\tset polarLayout.rootLength=100;\n")
        f.write("\tset polarLayout.showRoot=true;\n")
        f.write("\tset radialLayout.spread=0.0;\n")
        f.write("\tset rectilinearLayout.alignTipLabels=false;\n")
        f.write("\tset rectilinearLayout.curvature=0;\n")
        f.write("\tset rectilinearLayout.rootLength=100;\n")
        f.write("\tset trees.order=true;\n")
        f.write("\tset trees.orderType=\"increasing\";\n")
        f.write("\tset trees.rooting=true;\n")
        f.write("\tset trees.rootingType=Midpoint;\n") # Reflects the midpoint rooting option
        f.write("\tset trees.transform=false;\n")
        f.write("\tset trees.transformType=\"cladogram\";\n") 
        f.write("\tset scale.offsetAge=0.0;\n")
        f.write("\tset scale.rootAge=1.0;\n")
        f.write("\tset scale.scaleFactor=1.0;\n")
        f.write("\tset scale.scaleRoot=false;\n")
        f.write("\tset scaleAxis.automaticScale=true;\n")
        f.write("\tset scaleAxis.fontSize=8.0;\n")
        f.write("\tset scaleAxis.isShown=false;\n")
        f.write("\tset scaleAxis.lineWidth=1.0;\n")
        f.write("\tset scaleAxis.majorTicks=1.0;\n")
        f.write("\tset scaleAxis.origin=0.0;\n")
        f.write("\tset scaleAxis.reverseAxis=false;\n")
        f.write("\tset scaleAxis.showGrid=true;\n")
        f.write("\tset scaleBar.automaticScale=true;\n")
        f.write("\tset scaleBar.fontSize=10.0;\n")
        f.write("\tset scaleBar.isShown=true;\n")
        f.write("\tset scaleBar.lineWidth=1.0;\n")
        f.write("\tset scaleBar.scaleRange=0.0;\n")
        f.write("end;\n")

    # If interactive view desired:
    # t.show(tree_style=ts)


if __name__ == "__main__":
    main()
