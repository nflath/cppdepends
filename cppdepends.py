import re, os, sys, tempfile, collections

usage = """
cppdepends v1.0.  (C) 2009, 2010 Nathaniel Flath.
http://github.com/nflath/cppdepends

usage: python cppdepends.py dir out [threshold

dir is the path to the directory you wish to generate a dependency graph for.
out is the file that you wish to generate.
threshhold is a multiple of the average number of times a file is included.   If
   a file is included more than average # of includes * threshhold times, it is
 highlighted in red.  Defaults to 1.

Example usage: python cppdenends.py code/project/src graph.pdf 2
"""

includePattern = re.compile( """#include *"([^"]*)""" )
ignorePattern = re.compile( "~|\\.svn")
nodes = collections.defaultdict(lambda : 0)

#TODO: Make subdirectories work better
def generate_edges_for_dir(dir, out, size):
    """Iterates through all files in dir, writing edges for each file to 'out'.
    Will call itself recursively on directories, so that all files are
    processed.  The size argument controls how many characters are cut off the
    path of the file, to normalize files relative to the same directory."""
    print dir
    for f in os.listdir(dir):
        full_file = os.path.abspath(os.path.join(dir,f))
        if os.path.isfile(full_file) and not ignorePattern.search(f):
            for line in file(full_file):
                if includePattern.match(line) is not None:
                    #Write an edge for a single include statement
                    out.write("  ")
                    out.write('"' + full_file[size:] + '"')
                    out.write(" -> ")
                    out.write('"')
                    includeName = os.path.abspath(
                        os.path.join(dir,
                                     includePattern.match( line ).group(1)))[size:]
                    out.write(includeName)
                    nodes[includeName] += 1;
                    out.write('"')
                    out.write("\n")
        elif not ignorePattern.search(f):
            generate_edges_for_dir(full_file, out, size)

if __name__ == "__main__":
    #Error checking of input
    if len(sys.argv) < 3:
        print("ERROR: Wrong number of arguments.")
        print(usage)
        sys.exit()
    dir = os.path.abspath(sys.argv[1])
    if not os.path.isdir(dir):
        print("ERROR: " + dir + " is not a directory.")
        print(usage)
        sys.exit()
    outpdf = sys.argv[2]
    threshold = 1
    if len(sys.argv) > 3:
        threshold = sys.argv[3]
    outdot = tempfile.NamedTemporaryFile(delete=False)
    outdot.write("digraph G {\n")
    generate_edges_for_dir(dir, outdot, len(dir) + 1)
    num_includes = sum(nodes.values())
    avg = float(num_includes) / float(len(nodes.values()))
    for key in nodes:
        if  nodes[key] > float(threshold) * avg:
            outdot.write('"' + key + '" [color=red]\n')
    outdot.write("}\n")
    outdot.close()
    os.system( "dot -Tpdf -o " + outpdf + " " + outdot.name )

