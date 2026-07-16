library("reticulate")

read_zarr_zip <- function(path) {
  zarr <- import("zarr")
  anndata_py <- import("anndata")
  store <- zarr$storage$ZipStore(path, mode = "r")
  adata <- anndata_py$read_zarr(store)
  store$close()
  adata
}

# Read zarr zip lazily: obs/var materialized, X dask-backed.
# Use adata[r_logical_mask]$to_memory() to load subsets with int32 indices.
read_zarr_zip_lazy <- function(path) {
  zarr <- import("zarr")
  synergy_io <- import("{{ cookiecutter.package_name }}.io")
  store <- zarr$storage$ZipStore(path, mode = "r")
  synergy_io$read_as_dask(store)
}

write_zarr_zip <- function(adata, path) {
  warnings <- import("warnings")
  zarr <- import("zarr")
  store <- zarr$storage$ZipStore(path, mode = "w")

  # Suppress Python UserWarnings during write (equivalent to Python's `with` statement)
  # Manually call context manager protocol: __enter__ and __exit__
  warnings$catch_warnings()$`__enter__`()
  warnings$simplefilter("ignore", category = warnings$UserWarning)
  adata$write_zarr(store)
  warnings$catch_warnings()$`__exit__`(NULL, NULL, NULL)

  store$close()
}
