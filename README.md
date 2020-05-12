# go-test-stats
Utilities to analyze verbose Go test logs

## How to use

1. run your `go test -v` command via the provided `annotate` script,
   for example:

   ```
   $ go test ./... -p 1 -v 2>&1 | ./annotate >test.log
   ```

   (NB: `-p 1` is "one package at a time", and is recommended)

2. extract the data from the log:

   ```
   $ python3 analyze-go-test-output.py test.log >results.py
   ```

3. produce reports:

   ```
   $ python3 summarize-go-test-output.py <results.py >report.txt
   $ python3 dump-csv.py <results.py   # outputs packages.csv, tests.csv, subtests.csv
   $ python3 dump-html.py <results.py  # outputs report.html

## Explanation of programs

| Program                       | Description                                                                                                                                        |
|-------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| `annotate`                    | Prefix each line of output with a timestamp and summary of current resource usage. Developed primarily on BSD, may or may not work on macOS/Linux. |
| `analyze-go-test-output.py`   | Parse a Go verbose test log file and produce a Python object with the test metadata per package.                                                   |
| `dump-csv.py`                 | Dump the raw test metadata as CSV files.                                                                                                           |
| `dump-html.py`                | Produce two browsable and interactively sortable tables of packages and tests.                                                                     |
| `summarize-go-test-output.py` | Produce a text-only summary of the "top" packages and tests in various categories.                                                                 |
