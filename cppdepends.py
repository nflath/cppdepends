import re, os, sys, tempfile

usage = """
cppdepends v1.0.  (C) 2009, 2010 Nathaniel Flath.
http://github.com/nflath/cppdepends

usage: python cppdepends.py dir out

dir is the path to the directory you wish to generate a dependency graph for.
out is the file that you wish to generate.

Example usage: python cppdenends.py code/project/src graph.pdf
"""

includePattern = re.compile( "#include *\"([^\"]*)" )
ignorePattern = re.compile( "~" )
nodes = []

#TODO: Make subdirectories work better
def generate_edges_for_dir(dir, out, size):
    """Iterates through all files in dir, writing edges for each file to 'out'.
    Will call itself recursively on directories, so that all files are
    processed.  The size argument controls how many characters are cut off the
    path of the file, to normalize files relative to the same directory."""
    for f in os.listdir(dir):
        full_file = os.path.abspath(os.path.join(dir,f))
        if os.path.isfile(full_file) and not ignorePattern.match(f):
            for line in file(full_file):
                if includePattern.match(line) is not None:
                    #Write an edge for a single include statement
                    out.write("  ")
                    out.write("\"" + full_file[size:] + "\"")
                    out.write(" -> ")
                    out.write("\"")
                    out.write(os.path.abspath(
                            os.path.join(dir,
                                         includePattern.match( line ).group(1)))[size:])
                    out.write("\"")
                    out.write("\n")
        else:
            generate_edges_for_dir(full_file, out, size)

if __name__ == "__main__":
    #Error checking of input
    if len(sys.argv) != 3:
        print("ERROR: Wrong number of arguments.")
        print(usage)
        sys.exit()
    dir = os.path.abspath(sys.argv[1])
    if not os.path.isdir(dir):
        print("ERROR: " + dir + " is not a directory.")
        print(usage)
        sys.exit()
    outpdf = sys.argv[2]
    outdot = tempfile.NamedTemporaryFile(delete=False)
    outdot.write("digraph G {\n")
    generate_edges_for_dir(dir, outdot, len(dir) + 1)
    outdot.write("}\n")
    outdot.close()
    os.system( "dot -Tpdf -o " + outpdf + " " + outdot.name )
