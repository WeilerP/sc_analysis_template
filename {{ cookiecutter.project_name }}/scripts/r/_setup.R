# Install (if missing) and attach packages from CRAN or Bioconductor. When install = FALSE, missing packages raise an
# error instead of being installed, since installing is unsafe/undesired in a multi-worker run, for example.
load_library <- function(packages, source = c("CRAN", "Bioconductor"), install = TRUE) {
  source <- match.arg(source)
  is_installed <- vapply(packages, requireNamespace, logical(1), quietly = TRUE)
  missing_packages <- packages[!is_installed]
  if (length(missing_packages) > 0) {
    if (!install) {
      stop(
        "The following packages are not installed: ",
        paste(missing_packages, collapse = ", "),
        ". In a multi worker setup, run once with n_workers = 1 to install them first.",
        call. = FALSE
      )
    }
    if (source == "CRAN") {
      install.packages(missing_packages, repos = "https://cloud.r-project.org")
    } else {
      if (!requireNamespace("BiocManager", quietly = TRUE)) {
        install.packages("BiocManager", repos = "https://cloud.r-project.org")
      }
      BiocManager::install(missing_packages, update = FALSE, ask = FALSE)
    }
  }
  for (package_name in packages) {
    library(package_name, character.only = TRUE)
  }
}
