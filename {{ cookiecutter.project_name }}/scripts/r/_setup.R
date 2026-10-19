# Install (if missing) and attach packages from CRAN, Bioconductor, or GitHub (given as "owner/repo"). When
# install = FALSE, missing packages raise an error instead of being installed, since installing is unsafe/undesired in a
# multi-worker run, for example.
load_library <- function(packages, source = c("CRAN", "Bioconductor", "github"), install = TRUE) {
  source <- match.arg(source)
  if (source == "github") {
    package_names <- vapply(strsplit(packages, "/"), `[`, character(1), 2)
  } else {
    package_names <- packages
  }
  is_installed <- vapply(package_names, requireNamespace, logical(1), quietly = TRUE)
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
    } else if (source == "Bioconductor") {
      if (!requireNamespace("BiocManager", quietly = TRUE)) {
        install.packages("BiocManager", repos = "https://cloud.r-project.org")
      }
      BiocManager::install(missing_packages, update = FALSE, ask = FALSE)
    } else if (source == "github") {
      if (!requireNamespace("pak", quietly = TRUE)) {
        install.packages("pak", repos = "https://cloud.r-project.org")
      }
      pak::pak(missing_packages)
    }
  }
  for (package_name in package_names) {
    library(package_name, character.only = TRUE)
  }
}
