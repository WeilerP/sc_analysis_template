# Raise an error listing `values` after `message` if `values` is not empty.
stop_if_any <- function(values, message) {
  if (length(values) > 0) {
    stop(message, paste(values, collapse = ", "), call. = FALSE)
  }
}

# Raise an error if a default is neither a string (command line arguments) nor a boolean (--name --no-name logic)
check_defaults <- function(defaults) {
  is_valid <- vapply(
    defaults,
    function(default) (is.character(default) && length(default) == 1) || isTRUE(default) || isFALSE(default),
    logical(1)
  )
  stop_if_any(names(defaults)[!is_valid], "Defaults must be a single string, or TRUE/FALSE for a switch: ")
}

# Split flag arguments into option names and values:
# - ``--name=value`` -> string value
# - `switches`: ``--name`` -> ``TRUE``; ``--no-name`` -> FALSE
# Note: an argument `no_name` has higher precedence than a switch variable.
parse_flags <- function(args, known_options, positional, switches) {
  # standard args
  flag_names <- gsub("-", "_", sub("=.*$", "", sub("^--", "", args)))
  is_negated <- !flag_names %in% known_options & sub("^no_", "", flag_names) %in% switches
  flag_names[is_negated] <- sub("^no_", "", flag_names[is_negated])
  has_value <- grepl("^--[^=]+=", args)

  # switch variables, and possible flags
  is_switch <- flag_names %in% switches
  flag_options <- setdiff(known_options, positional)
  allowed_flags <- paste0("--", ifelse(flag_options %in% switches, "[no-]", ""), gsub("_", "-", flag_options))

  # unknown arg or flag without value or switch var with value -> stop
  stop_if_any(
    args[!flag_names %in% known_options],
    paste0("Unknown flags (allowed: ", paste(allowed_flags, collapse = ", "), "): ")
  )
  stop_if_any(args[!has_value & !is_switch], "Flags must have the form --name=value: ")
  stop_if_any(args[has_value & is_switch], "Switches take no value: ")

  # construct flags
  flag_values <- as.list(sub("^--[^=]+=", "", args))
  flag_values[is_switch] <- as.list(!is_negated[is_switch])
  list(names = flag_names, values = flag_values)
}

# Parse command line arguments into a named list.
# flags: ``--sample-name=values``
# swich: arg with boolean default (supports ``--name`` ``--no-name`` logic)
# ``--sample-name`` -> ``sample_name``
# arguments without ``--name`` flags map to ``positionals`` in order
# `required` defines required inputs
parse_args <- function(positional, defaults = list(), required = character(), args = commandArgs(trailingOnly = TRUE)) {
  check_defaults(defaults)
  known_options <- union(positional, names(defaults))
  switches <- names(defaults)[vapply(defaults, is.logical, logical(1))]
  is_flag <- startsWith(args, "--")
  flags <- parse_flags(args[is_flag], known_options, positional, switches)
  positional_args <- args[!is_flag]

  stop_if_any(
    positional_args[seq_along(positional_args) > length(positional)],
    paste0("Too many positional arguments (expected: ", paste(positional, collapse = ", "), "); unexpected: ")
  )

  given_names <- c(positional[seq_along(positional_args)], flags$names)
  stop_if_any(unique(given_names[duplicated(given_names)]), "Options given more than once: ")
  stop_if_any(setdiff(required, given_names), "Missing required options: ")

  parsed <- setNames(as.list(rep(NA_character_, length(known_options))), known_options)
  parsed[names(defaults)] <- defaults
  parsed[given_names] <- c(as.list(positional_args), flags$values)
  parsed
}

# Convert a parsed string value to an integer; ``name`` is the name of the argument associated with the value.
as_integer_arg <- function(value, name) {
  numeric_value <- suppressWarnings(as.numeric(value))
  integer_value <- suppressWarnings(as.integer(numeric_value))
  if (is.na(integer_value) || integer_value != numeric_value) {
    stop("Option ", name, " must be an integer, got: ", value, call. = FALSE)
  }
  integer_value
}

# Convert string value `value` to a number or, if `value` is "NULL", to NULL; ``name`` is the name of the argument
# associated with the value.
as_numeric_or_null_arg <- function(value, name) {
  if (identical(value, "NULL")) {
    return(NULL)
  }
  numeric_value <- suppressWarnings(as.numeric(value))
  if (is.na(numeric_value)) {
    stop("Option ", name, " must be a number or \"NULL\", got: ", value, call. = FALSE)
  }
  numeric_value
}
