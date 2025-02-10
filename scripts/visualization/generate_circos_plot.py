"""
Title: Generate circos plots
Description: This script generates circos plots from GenBank files. If desired also mark genes of interest.
Author: Nina Dombrowski
Date: 2024-11-20
Tags: visualization, genomics
Usage: python python generate_circos_plot.py -i genome.gbk  -o circos_plot.pdf  -g genes_of_interest.txt
"""

import argparse
from pycirclize import Circos
from pycirclize.parser import Genbank
import numpy as np
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib import pyplot as plt

def read_genes_of_interest(file_path):
    """Read genes of interest from a file."""
    with open(file_path, "r") as f:
        return [line.strip() for line in f.readlines()]

def main():
    # Set up argparse
    parser = argparse.ArgumentParser(description="Generate a Circos plot from a GenBank file.")
    parser.add_argument("-i", "--input", required=True, help="Input GenBank file (.gbk)")
    parser.add_argument("-o", "--output", required=True, help="Output PDF file (.pdf)")
    parser.add_argument("-g", "--genes", help="Text file containing genes of interest (one gene per line)", default=None)
    args = parser.parse_args()

    # Read genes of interest from the file, if provided
    CDS_list = []
    if args.genes:
        CDS_list = read_genes_of_interest(args.genes)

    # Load Genbank file
    gbk = Genbank(args.input)

    # Set base plot
    circos = Circos(sectors={gbk.name: gbk.range_size})
    sector = circos.get_sector(gbk.name)

    # Forward CDS (blue)
    f_cds_track = sector.add_track((91.3, 97), r_pad_ratio=0.1)
    f_cds_track.genomic_features(gbk.extract_features("CDS", target_strand=1), fc="#145da0")

    # Add line
    circos.line(r=90, deg_lim = (2,358))
    circos.text("5'", r=90, deg=1, size = 5)
    circos.text("3'", r=90, deg=359, size = 5)

    # Reverse CDS (blue)
    r_cds_track = sector.add_track((83, 89), r_pad_ratio=0.1)
    r_cds_track.genomic_features(gbk.extract_features("CDS", target_strand=-1), fc="#145da0")
    
    # rRNA and tRNA
    rrna_track = sector.add_track((78, 83), r_pad_ratio=0.1)
    rrna_track.genomic_features(gbk.extract_features("rRNA"), fc="firebrick")
    rrna_track.genomic_features(gbk.extract_features("tRNA"), fc="orange")

    # GC Content
    gc_content_track = sector.add_track((57, 78))
    pos_list, gc_contents = gbk.calc_gc_content()
    gc_contents = gc_contents - gbk.calc_genome_gc_content()
    positive_gc_contents = np.where(gc_contents > 0, gc_contents, 0)
    negative_gc_contents = np.where(gc_contents < 0, gc_contents, 0)
    abs_max_gc_content = np.max(np.abs(gc_contents))
    vmin, vmax = -abs_max_gc_content, abs_max_gc_content
    gc_content_track.fill_between(
        pos_list, positive_gc_contents, 0, vmin=vmin, vmax=vmax, color="black"
    )
    gc_content_track.fill_between(
        pos_list, negative_gc_contents, 0, vmin=vmin, vmax=vmax, color="black"
    )

    # GC Skew (purple, green)
    gc_skew_track = sector.add_track((40, 57))
    pos_list, gc_skews = gbk.calc_gc_skew()
    positive_gc_skews = np.where(gc_skews > 0, gc_skews, 0)
    negative_gc_skews = np.where(gc_skews < 0, gc_skews, 0)
    abs_max_gc_skew = np.max(np.abs(gc_skews))
    vmin, vmax = -abs_max_gc_skew, abs_max_gc_skew
    gc_skew_track.fill_between(
        pos_list, positive_gc_skews, 0, vmin=vmin, vmax=vmax, color="purple"
    )
    gc_skew_track.fill_between(
        pos_list, negative_gc_skews, 0, vmin=vmin, vmax=vmax, color="#008000"
    )

    # Add inner track for ticks and genome position (after GC skew)
    inner_tick_track = sector.add_track((41, 46))  # Define the track position

    # Add major ticks with labels
    major_ticks_interval = 500000
    minor_ticks_interval = 100000

    inner_tick_track.xticks_by_interval(
        major_ticks_interval,
        outer=False,
        show_bottom_line=False,
        label_orientation="horizontal",
        label_size=6,
        label_formatter=lambda v: f"{v / 10 ** 6:.1f} Mb",
        tick_length=2,  # Length of the major ticks
        line_kws=dict(color="black"),  # Style for the major ticks
    )

    # Add minor ticks without labels
    inner_tick_track.xticks_by_interval(
        minor_ticks_interval,
        outer=False,
        show_bottom_line=False,
        tick_length=0.24,  # Shorter ticks for minor intervals
        show_label=False,  # No labels for minor ticks
        line_kws=dict(color="black"),  # Style for the minor ticks
    )

    # Selected genes of interest (and add as outer labels)
    pos_list, labels = [], []
    for feat in gbk.extract_features("CDS"):
        start, end = int(str(feat.location.end)), int(str(feat.location.start))
        pos = (start + end) / 2

        # Try to get gene label first, then fallback to locus_tag if gene is missing
        label = feat.qualifiers.get("gene", [""])[0]
        locus_tag = feat.qualifiers.get("locus_tag", [""])[0]
        
        # If label is missing, use locus_tag
        if label == "" or label.startswith("hypothetical"):
            label = locus_tag
        
        # Skip if the gene_id is not in the CDS_list
        gene_id = feat.qualifiers.get("locus_tag", [""])[0]
        if gene_id not in CDS_list:
            continue
        
        # Truncate label if it's too long
        if len(label) > 20:
            label = label[:20] + "..."
        
        # Add position and label to lists
        pos_list.append(pos)
        labels.append(label)

    # Plot labels
    f_cds_track.xticks(
        pos_list,
        labels,
        label_orientation="vertical",
        show_bottom_line=False,  # Remove bottom lines for cleaner look
        label_size=6,
        tick_length=4,
        line_kws=dict(ec="red", lw=1.5),
    )

    # Plot
    fig = circos.plotfig()

    # Legend
    
    # Create the list of legend handles
    handles = []

    # Conditionally add "Genes of interest" to the legend if -g was provided
    if args.genes:
        handles.append(Patch(color="red", label="Genes of interest"))

    # Add other legend entries
    handles.extend([
        Patch(color="#145da0", label="CDS"),
        Patch(color="firebrick", label="rRNA"),
        Patch(color="orange", label="tRNA"),
        Patch(color="black", label="GC Content"),
        Patch(color="purple", label="Positive GC Skew"),
        Patch(color="#008000", label="Negative GC Skew"),
    ])
    
    # Add the legend to the plot
    _ = circos.ax.legend(handles=handles, bbox_to_anchor=(0.9, 1), loc="upper left", fontsize=8)

    # Save to PDF
    fig.savefig(args.output)
    plt.close(fig)

if __name__ == "__main__":
    main()
