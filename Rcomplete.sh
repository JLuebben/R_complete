#!/bin/bash

rm -f rfree.data wR2.data r1.data wR2-plot.data

grep "Nfree(all)" .k*.lst > Nfree_all.data
numentries=$(wc Nfree_all.data)


awk '{ sumDF += $5; sumFo += $7; } END {print "Rcomplete = ", sumDF/sumFo; }' Nfree_all.data
echo "   from $numentries entries"
