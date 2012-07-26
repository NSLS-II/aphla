import os
import sys

if __name__ == "__main__":
    srcroot = os.path.dirname(os.path.abspath(sys.argv[0]))
    htmlroot = os.path.join(srcroot, "..", "_build", "html") 
    idxhtml = os.path.join(htmlroot, "index.html")
    commandshtml = os.path.join(htmlroot, "commands.html")
    
    i0, i1 = None, None
    for i, s in enumerate(open(commandshtml, 'r').readlines()):
        if s.find("<table border") >= 0: i0 = i
        elif s.find("</table>") >= 0: i1 = i
    if i0 is not None and i1 is not None:
        cmd = os.path.join(srcroot, "..", "_templates", "commands_table.html")
        f = open(cmd, 'w')
        for s in open(commandshtml, 'r').readlines()[i0:i1+1]:
            f.write(s)
        f.close()


    
