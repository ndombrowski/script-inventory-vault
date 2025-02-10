#!/usr/bin/perl
####!/opt/perl-5.16.2/bin/perl
# Nom du programme: formatFigtree2.pl
# Version 1.0 (juin 2015)
# Auteur: CP
#Format a newick tree to a figtree format, coloring the leaves depending on the taxa (or anything it's giving in the list with color)
# Infiles: List of trees on a newick format, in one line, and one tree per file.
#Document with in column one the list of the pattern we will use to define the color of the leave (could be a taxon, number anything but without space) and separated by a space a second column with the color tag from figtree we want to add for the pattern
#outfile: trees in figtree format, named tree.fgcol
#also change: the order of the nodes (decreasing), the values at nodes (label) and the font for nodes and leaves (Calibri).
#for example files check: https://github.com/Neo-sage/nicescripts/blob/master/colourtrees/arcbactreelist.lis
#usage: perl formatFigtree.pl listoftreepaths.file -C colourtable.file


###################################################################################



$USAGE = "\n formatFigtree.pl CP version 1.0 (june 2015)\n\n [USAGE]  : formatFigtree.pl 0ListTrees -C TableTaxa/color -p police(optional - default Calibri) -sn sizenode(optional - default 8) -sl sizeleaves(optional - default 8) \n\n Ouvrir pour info sur les fichiers\n\n" ;

# Affiche les informations si aucun argument n'est entré
unless( @ARGV )
{
    print $USAGE ;
    exit ;
}




#Initialisation des variables
$police = "Calibri";
$sizenode = "8";
$sizeleaves = "8";

$ListTrees=$ARGV[0]; 
$TableTaxaColor=$ARGV[1];


# initialisation des variables optionelles
for $i (1..10){
	if ($ARGV[$i] eq "-C"){ $TableTaxaColor = $ARGV[$i+1];} 
	if ($ARGV[$i] eq "-p"){ $police = $ARGV[$i+1];}
	if ($ARGV[$i] eq "-sn"){ $sizenode = $ARGV[$i+1];} 
	if ($ARGV[$i] eq "-sl"){ $sizeleaves = $ARGV[$i+1];}
}


#Lecture de la table de taxa/ pattern et stockage dans une hash.
open(tableTC,"<$TableTaxaColor")|| die ("Erreur d'ouverture de fichier d'entree ".$ARGV[1]) ;
%hashcolor = ();
while(<tableTC>){
	@split_line = split(/\t/,$_);
	$taxa = $split_line[0];
	$color = $split_line[1];
	$hashcolor{$taxa} = $color;
}






open(listtrees,"<$ListTrees")|| die ("Erreur d'ouverture de fichier d'entree ".$ARGV[0]) ;

# Lecture de la liste de fichiers a traiter.
while (<listtrees>){
	$tree = $_;
	chomp($tree);
	$treeout = $tree.".fgcol";
	open(tree, "<$tree")||die("Erreur d'ouverture de fichier d'entree ".$tree);  
	open (out, ">$treeout");  # ouverture dun outfile pour ce tree en particulier
	print "tree: ".$tree." tree out: ".$treeout."\n";  

	@intree = ();
	$compt_sps = 0;
	@listspsC = ();
	while (<tree>){
		$treenexus = $_;
		chomp($treenexus);
		@intree = split(/,/, $treenexus);  # split de la ligne d'arbre

		$spsF = 0;
		$sps = 0;
		$spsC = 0;
		foreach $element(@intree){  #Recherche des noms des leaves par slipts successifs
			$element =~ s/\(//g;
			@split_element = split(/\:/,$element);
			$sps =  $split_element[0];
			chomp($sps);
			#($species) = split(/\:/,$element);
			$spsF = "\t".$sps."\n";;

			foreach $taxon (keys %hashcolor){  # Recherche du pattern taxa ou sps, et ajout de couleur si besoin.
				#print "taxa teste: ".$taxon."\n";
				if ($sps =~ m/$taxon/){
					$color = $hashcolor{$taxon};
					chomp($color);
					$spsC = "\t".$sps.$color."\n";
					$spsF = $spsC;
					#print "line sps: ".$spsC." pour le taxon: ".$taxon."\n";
				}
			}
			push(@listspsC, $spsF);  # Remplissage de la table pour ecriture du fichier figtree
			$compt_sps++;
		}

	
		# Ecriture du fichier figtree, avec avant et apres l'arbre.
		print out "#NEXUS\nbegin taxa;\n\tdimensions ntax=".$compt_sps.";\n\ttaxlabels\n";
		foreach $spsC (@listspsC){
			print out $spsC;
		}
		print out ";\nend;\n\nbegin trees;\n\ttree tree_1 = [&R] ".$treenexus."\nend;\n\nbegin figtree;\n";
		print out "\tset appearance.backgroundColorAttribute=\"Default\";\n";
		print out "\tset appearance.backgroundColour=#ffffff;\n";
		print out "\tset appearance.branchColorAttribute=\"User selection\";\n";
		print out "\tset appearance.branchColorGradient=false;\n";
		print out "\tset appearance.branchLineWidth=1.0;\n";
		print out "\tset appearance.branchMinLineWidth=0.0;\n";
		print out "\tset appearance.branchWidthAttribute=\"Fixed\";\n";
		print out "\tset appearance.foregroundColour=#000000;\n";
		print out "\tset appearance.hilightingGradient=false;\n";
		print out "\tset appearance.selectionColour=#2d3680;\n";
		print out "\tset branchLabels.colorAttribute=\"User selection\";\n";
		print out "\tset branchLabels.displayAttribute=\"Branch times\";\n";
		print out "\tset branchLabels.fontName=\"Agency FB\";\n";
		print out "\tset branchLabels.fontSize=8;\n";
		print out "\tset branchLabels.fontStyle=0;\n";
		print out "\tset branchLabels.isShown=false;\n";
		print out "\tset branchLabels.significantDigits=4;\n";
		print out "\tset layout.expansion=0;\n";
		print out "\tset layout.layoutType=\"RECTILINEAR\";\n";
		print out "\tset layout.zoom=0;\n";
		print out "\tset legend.attribute=\"label\";\n";
		print out "\tset legend.fontSize=10.0;\n";
		print out "\tset legend.isShown=false;\n";
		print out "\tset legend.significantDigits=4;\n";
		print out "\tset nodeBars.barWidth=4.0;\n";
		print out "\tset nodeBars.displayAttribute=null;\n";
		print out "\tset nodeBars.isShown=false;\n";
		print out "\tset nodeLabels.colorAttribute=\"User selection\";\n";
		print out "\tset nodeLabels.displayAttribute=\"label\";\n";
		print out "\tset nodeLabels.fontName=\"$police\";\n";
		print out "\tset nodeLabels.fontSize=$sizenode;\n";
		print out "\tset nodeLabels.fontStyle=0;\n";
		print out "\tset nodeLabels.isShown=true;\n";
		print out "\tset nodeLabels.significantDigits=4;\n";
		print out "\tset nodeShape.colourAttribute=\"User selection\";\n";
		print out "\tset nodeShape.isShown=false;\n";
		print out "\tset nodeShape.minSize=10.0;\n";
		print out "\tset nodeShape.scaleType=Width;\n";
		print out "\tset nodeShape.shapeType=Circle;\n";
		print out "\tset nodeShape.size=4.0;\n";
		print out "\tset nodeShape.sizeAttribute=\"Fixed\";\n";
		print out "\tset polarLayout.alignTipLabels=false;\n";
		print out "\tset polarLayout.angularRange=0;\n";
		print out "\tset polarLayout.rootAngle=0;\n";
		print out "\tset polarLayout.rootLength=100;\n";
		print out "\tset polarLayout.showRoot=true;\n";
		print out "\tset radialLayout.spread=0.0;\n";
		print out "\tset rectilinearLayout.alignTipLabels=false;\n";
		print out "\tset rectilinearLayout.curvature=0;\n";
		print out "\tset rectilinearLayout.rootLength=100;\n";
		print out "\tset scale.offsetAge=0.0;\n";
		print out "\tset scale.rootAge=1.0;\n";
		print out "\tset scale.scaleFactor=1.0;\n";
		print out "\tset scale.scaleRoot=false;\n";
		print out "\tset scaleAxis.automaticScale=true;\n";
		print out "\tset scaleAxis.fontSize=8.0;\n";
		print out "\tset scaleAxis.isShown=false;\n";
		print out "\tset scaleAxis.lineWidth=1.0;\n";
		print out "\tset scaleAxis.majorTicks=1.0;\n";
		print out "\tset scaleAxis.origin=0.0;\n";
		print out "\tset scaleAxis.reverseAxis=false;\n";
		print out "\tset scaleAxis.showGrid=true;\n";
		print out "\tset scaleBar.automaticScale=true;\n";
		print out "\tset scaleBar.fontSize=10.0;\n";
		print out "\tset scaleBar.isShown=true;\n";
		print out "\tset scaleBar.lineWidth=1.0;\n";
		print out "\tset scaleBar.scaleRange=0.0;\n";
		print out "\tset tipLabels.colorAttribute=\"User selection\";\n";
		print out "\tset tipLabels.displayAttribute=\"Names\";\n";
		print out "\tset tipLabels.fontName=\"$police\";\n";
		print out "\tset tipLabels.fontSize=$sizeleaves;\n";
		print out "\tset tipLabels.fontStyle=0;\n";
		print out "\tset tipLabels.isShown=true;\n";
		print out "\tset tipLabels.significantDigits=4;\n";
		print out "\tset trees.order=true;\n";
		print out "\tset trees.orderType=\"increasing\";\n";
		print out "\tset trees.rooting=true;\n";
		print out "\tset trees.rootingType=Midpoint;\n";
		print out "\tset trees.transform=false;\n";
		print out "\tset trees.transformType=\"cladogram\";\n";
		print out "end;\n"


	}
	close(tree);
	close (out);
}


