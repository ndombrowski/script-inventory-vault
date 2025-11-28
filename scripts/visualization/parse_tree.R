#!/usr/bin/env Rscript

suppressPackageStartupMessages({
    library(ggtree)
    #library(treeio)
    library(phangorn)
    library(tidyverse)
    library(optparse)
})

# ----------------------------------------------------------------------
# Command-line arguments
# ----------------------------------------------------------------------
option_list <- list(
    make_option(
        c("-t", "--tree"),
        type = "character",
        help = "Input tree file (Newick)"
    ),
    make_option(
        c("-c", "--colors"),
        type = "character",
        help = "Color mapping file (tab-delimited incl header: label color)"
    ),
    make_option(
        c("-o", "--output"),
        type = "character",
        help = "Output PDF file"
    ),
    make_option(
        c("-m", "--midpoint"),
        action = "store_true",
        default = FALSE,
        help = "Use midpoint rooting and circular layout"
    )
)

opt <- parse_args(OptionParser(option_list = option_list))
treefile <- opt$tree
colorfile <- opt$colors
use_midpoint <- opt$midpoint

# # For testing
#treefile <- "trimmed.faa.treefile"
#colorfile <- "colors"
#use_midpoint <- TRUE

# ----------------------------------------------------------------------
# Load tree
# ----------------------------------------------------------------------
#tree <- read.newick(treefile, node.label = 'support')
tree <- read.tree(treefile)

if (use_midpoint) {
    tree <- midpoint(tree)
}


# ----------------------------------------------------------------------
# Load color map
# ----------------------------------------------------------------------
color_map <- read_table(colorfile) |>
    mutate(label_lower = tolower(label))


# ----------------------------------------------------------------------
# Assign colors to tips
# ----------------------------------------------------------------------
tip_labels <- tree$tip.label

tip_data <- tibble(tip_labels = tip_labels) |>
    mutate(
        color = unname(sapply(tip_labels, function(label) {
            match_idx <- which(str_detect(
                tolower(label),
                tolower(color_map$label)
            ))
            if (length(match_idx) > 0) {
                color_map$colors[match_idx[1]]
            } else {
                "#000000"
            }
        }))
    )

# ----------------------------------------------------------------------
# Plot tree
# ----------------------------------------------------------------------
layout_type <- ifelse(use_midpoint, "circular", "equal_angle")
other <- "rectangular"

p <- ggtree(tree, layout = layout_type) %<+%
    tip_data +
    geom_tiplab(aes(label = label, color = color), size = 2, align = FALSE) +
    scale_color_identity() +
    geom_nodelab(aes(label = label), hjust = 2, size = 2) +
    geom_treescale(x = 1, y = 0, fontsize = 3, linesize = 1, offset = 0.1) +
    geom_point2(
        # NAs are introduced by as.numeric but that is expected due to an empty bootstrap value at the root
        aes(
            subset = !isTip & suppressWarnings(as.numeric(label)) > 80,
            fill = cut(suppressWarnings(as.numeric(label)), c(0, 90))
        ),
        shape = 16,
        size = 2
    ) +
    hexpand(.1) +
    vexpand(.1) +
    #coord_cartesian(clip = "off") +
    theme(plot.margin = margin(.5, .5, .5, .5, "in")) +
    guides(fill = "none", color = "none", shape = "none")

p

# ----------------------------------------------------------------------
# Save PDF
# ----------------------------------------------------------------------
ggsave(opt$output, plot = p, width = 8.27, height = 11.69, units = "in")
