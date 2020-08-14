# Maven Tree Search

Searches for a given term in a file that contains the output from `mvn
dependency:tree`.

## Usage

`python3 main.py <maven-tree.txt> <search-term>`

### Examples

* `python3 main.py example-input-files/simple-tree-1.txt logback`
* `python3 main.py example-input-files/simple-tree-2.txt core`
* `python3 main.py example-input-files/complex-tree.txt platform`
