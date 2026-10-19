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

  # Suppress Python UserWarnings during write; reticulate's with() mirrors Python's `with` statement
  with(warnings$catch_warnings(), {
    warnings$simplefilter("ignore", category = import_builtins()$UserWarning)
    adata$write_zarr(store)
  })

  store$close()
}
