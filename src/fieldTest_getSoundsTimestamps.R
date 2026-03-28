#!/usr/bin/Rscript

library(baRulho)

master_annotations = as.data.frame(
	readRDS("./data/test_localisation_20250808/master_propagation_2025_annotations.rds")
)
PATH = "./data/test_localisation_20250808/SYNC"

options(sound.files.path = PATH)

markers_positions = find_markers(X = master_annotations, cores=10, )
aligned_tests = align_test_files(X = master_annotations, Y = markers_positions)

getOption('baRulho')$files_to_check_align_test_files

length(unique(aligned_tests$sound.files))

table(aligned_tests$sound.id)[table(aligned_tests$sound.id)==48]

write.csv(aligned_tests, "./results/aligned_sounds_20250808.csv")

print("All sounds aligned and annotations savec in ./results/aligned_sounds_20250808.csv")
