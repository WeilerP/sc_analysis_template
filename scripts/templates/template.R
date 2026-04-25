library("this.path")

library("anndata")

source(paste(dirname(this.dir()), "r/_constants.R", sep = "/"))

# Constants
DATASET_ID <- ""

# Data loading
adata <- anndata::read_h5ad(file.path(DATA_DIR, DATASET_ID, "adata.h5ad"))
