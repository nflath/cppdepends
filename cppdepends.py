# <one line to give the program's name and a brief idea of what it does.>
#     Copyright (C) 2009-2013 Nathaniel Flath

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Contact Nathaniel Flath at: flat0103@gmail.com

import re, os, sys, tempfile, collections, copy

usage = """
cppdepends v1.0.  (C) 2009-2013 Nathaniel Flath.
flat0103@gmail.com
http://github.com/nflath/cppdepends

usage: python cppdepends.py dir out [threshold]

dir is the path to the directory you wish to generate a dependency graph for.
out is the file that you wish to generate.
threshhold is a multiple of the average number of times a file is included.   If
   a file is included more than average # of includes * threshhold times, it is
 highlighted in red.  Defaults to 1.

Example usage: python cppdenends.py code/project/src graph.pdf 2
"""

includePattern = re.compile( """#include *"([^"]*)""" )
ignorePattern = re.compile( "~|\\.svn")
nodes = collections.defaultdict(lambda : [])
numNodeIncluded = collections.defaultdict(lambda : 0)

#TODO: Make subdirectories work better
def generate_edges_for_dir(dir, size):
    """Iterates through all files in dir, creating a dictionary representing the graph.
    Will call itself recursively on directories, so that all files are
    processed.  The size argument controls how many characters are cut off the
    path of the file, to normalize files relative to the same directory."""

    for f in os.listdir(dir):
        full_file = os.path.abspath(os.path.join(dir,f))
        if os.path.isfile(full_file) and not ignorePattern.search(f):
            for line in file(full_file):
                if includePattern.match(line) is not None:
                    includeName = os.path.abspath(
                        os.path.join(dir,
                                     includePattern.match( line ).group(1)))[size:]
                    nodes[full_file[size:]] += [includeName]
                    numNodeIncluded[includeName] += 1;
        elif not ignorePattern.search(f):
            generate_edges_for_dir(full_file, size)

#Globals needed for Tarjan's algorithm
index = 0
S = []
cycles = []
def find_cycles(nodes):
    """
    Returns a list of all nodes in a dependency cycle.
    Arguments:
    - `nodes`: Dictionary representing the dependency graph
    """
    nodeIndex = collections.defaultdict( lambda: None )
    lowlink = {}
    for v in copy.deepcopy(nodes):
        if nodeIndex[v] is None:
            tarjan(v, nodes, nodeIndex, lowlink)

def tarjan(v, nodes, nodeIndex, lowlink):
    """
    Tarjan's strongly-connected component algorithm, from wikipedia

    Arguments:
    - `v`: Start node
    - `nodes`: Graph
    - 'nodeIndex': dictionary containing node indices
    - 'lowlink': Dictionary containing node lowlinks
    """
    global index
    global cycles
    nodeIndex[v] = index
    lowlink[v] = index
    index += 1
    S.append(v)
    for v_ in nodes[v]:
        if not nodeIndex[v_]:
            tarjan(v_, nodes, nodeIndex, lowlink)
            lowlink[v] = min (lowlink[v], lowlink[v_])
        elif v_ in S:
            lowlink[v] = min(lowlink[v], nodeIndex[v_] )
    if lowlink[v] == nodeIndex[v]:
        cycle = []
        v_ = S.pop()
        cycle += [v_]
        while v_ != v:
            v_ = S.pop()
            cycle += [v_]

        if len(cycle) > 1:
            cycles += [cycle]

if __name__ == "__main__":
    #Error checking of inputop
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
    outdot = open('dot_file', 'w')
    outdot.write("digraph G {\n")

    #Generate node and numNOdeIncluded
    generate_edges_for_dir(dir, len(dir) + 1)
    find_cycles(nodes)

    #Colorize nodes included above the threshhold
    num_includes = sum(numNodeIncluded.values())
    avg = float(num_includes) / float(len(numNodeIncluded.values()))
    for key in numNodeIncluded:
        if  numNodeIncluded[key] > float(threshold) * avg:
            outdot.write('"' + key + '" [color=orange]\n')

    #Colorize cycles
    for cycle in cycles:
        for i in range(1, len(cycle)):
            nodes[cycle[i]].remove(cycle[i-1])
            outdot.write('"' + cycle[i] + '" [color=red]\n')
            outdot.write('"' + cycle[i] + '" -> "' + cycle[i - 1] + '" [color=red]\n')
        nodes[cycle[0]].remove(cycle[-1])
        outdot.write('"' + cycle[0] + '" [color=red]\n')
        outdot.write('"' + cycle[0] + '" -> "' + cycle[-1] + '" [color=red]\n')

    #Draw graph
    for node in nodes:
        for child in nodes[node]:
            outdot.write('  "' + node + '"' + ' -> "' + child + '"\n')

    outdot.write("}\n")
    outdot.close()
    os.system( "dot -Tpdf -o " + outpdf + " " + outdot.name )

