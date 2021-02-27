#!/usr/bin/python

"""This returns the shortest edit script between two sequences, based on
the algorithm described in

S. Wu, E. Myers, U. Manber, and W. Miller,
``An O(NP) Sequence Comparison Algorithm,''
Information Processing Letters 35, 6 (1990), 317-323.

The authors present the algorithm as solving an edit graph, starting
from a source in the upper left proceeding to a sink in the lower
right, where inserts move you right and deletes move you down.  Where
the two sequences are equal, you can slide diagonally along a 'snake.'
At each iteration you try to start as far right as possible,
considering a wider and wider range of diagonals until you can reach
the sink.  At each diagonal, you look to see where you can start from
coming from the diagonal below (by inserting) or above (by deleting).

Once the above algorithm has solved for the shortest edit script, we
can compress the edit script to return runs of inserts or deletes as a
command followed by a start and stop value, e.g. [(insert, 1),
(insert, 2), (insert, 3)] can be compressed to [(insert, 1, 3)].

In the edit script, 'i' means insert and 'd' means delete.

***LICENSE***"""

from __future__ import print_function

#def grid(A, B):
#    """Print grid.  This is helpful to visualize the search space
#       when A and B are strings."""

#    print "  %s" % B
#    print
#    for aletter in list(A):
#        row = "%s " % aletter
#        for bletter in list(B):
#            if aletter == bletter:
#                row = row + "\\"
#            else:
#                row = row + " "
#        print row


def ses(sequence1, sequence2, flag="compressed"):
    """Calculate shortest edit script between two sequences."""

    DEBUG = 0
    IC = "i"  # Insert command
    DC = "d"  # Delete command

    def consider(FP, SES, A, B, M, N, IC, DC, k):
        """ Calculate how far you can get on this diagonal (k) """

        def snake(A, B, M, N, k, y):
            """Return length of a diagonal."""

            x = y - k
            while (x < M) and (y < N) and (A[x] == B[y]):
                x = x + 1
                y = y + 1
            return y

        insert = FP[k - 1] + 1 # An insert will add a letter
        delete = FP[k + 1]     # A delete will not
        if (insert > delete):
            # We get a better start with an insert than a delete
            # Add an insert to the shortest edit script to this point
            SES[k] = SES[k - 1][:]
            SES[k].append( (IC, insert - 1) )
            # How far can we slide now
            progress = snake(A, B, M, N, k, insert)
        else:
            # We get a better start with a delete than an insert
            # Add a delete to the shortest edit script to this point
            SES[k] = SES[k + 1][:]
            SES[k].append( (DC, delete) )
            # How far can we slide now
            progress = snake(A, B, M, N, k, delete)
        return progress

    def compress(script):
        """ Parse edit script to compress runs of deletes and inserts """

        DEBUG = 0
        
        CES = []
        which =  ''
        start = -1
        stop  = -1
        for edit in script:
            command, position = edit

            startrun = 0
            endrun = 0

            if which == '':
                startrun = 1

            elif command == 'i':
                if which == 'd':
                    endrun = 1
                else:
                    if stop != position - 1:
                        endrun = 1
                    else:
                        stop = stop + 1

            elif command == 'd':
                if which == 'i':
                    endrun = 1
                else:
                    if start != position:
                        endrun = 1
                    else:
                        stop = stop + 1
            else:
                raise NotImplementedError("Unexpected command %s" % command)

            if endrun:
                CES.append( ( which, start, stop ) )
                startrun = 1
            if startrun:
                which = command
                start = position
                stop  = position

        # End last run
        if which != '':
            CES.append( ( which, start, stop ) )

        if DEBUG:
            print("Compressed edit script: ")
            print(CES)

        return CES

    def reverse(script):
        """Reverse sense of script.  Necessary if len(A) > len(B)."""

        offset = 0
        RCES = []    # Reversed, compressed edit script

        for edit in script:
            command, start, stop = edit
            if command == "i":
                RCES.append( ('d', start + offset, stop + offset) )
                offset = offset - (stop - start) - 1
            elif command == "d":
                RCES.append( ('i', start + offset, stop + offset) )
                offset = offset + (stop - start) + 1
            else:
                raise NotImplementedError("Unexpected command %s" % command)

        return RCES
        
    # Calculate shortest edit script
        
    # Put the sequences in the order we want:
    # A is the shorter sequence, and our edit script will tell us
    # how to get from A to B.
    if len(sequence1) < len(sequence2):
        A = sequence1
        B = sequence2
        order = "regular"
    else:
        A = sequence2
        B = sequence1
        order = "backwards"

    M = len(A)     # Size of shorter sequence
    N = len(B)     # Size of longer sequence
    Delta = N - M  # Diagonal of sink

    FP = {}   # Farthest point possible on this diagonal
    SES = {}  # Shortest edit script to get to FP, as (command, position) tuples
    for x in range(-(M+1), (N+2)):
        FP[x] = -1
        SES[x] = []

    i = 0     # Count how long it takes to determine path
    p = -1    # Number of deletes

    # Loop until we have found path to N on diagonal delta
    while FP[Delta] != N:
        p = p + 1
        i = i + Delta + (2 * p) + 1
        # Consider diagonals below delta
        for k in range(-p, Delta):
            FP[k] = consider(FP, SES, A, B, M, N, IC, DC, k)
        # Consider diagonals above delta
        for k in range(Delta + p, Delta, -1):
            FP[k] = consider(FP, SES, A, B, M, N, IC, DC, k)
        # Consider delta
        FP[Delta] = consider(FP, SES, A, B, M, N, IC, DC, Delta)

    if DEBUG:
        print(A)
        print(B)
        print("The edit distance is %s" % (Delta + (2 * p) ))
        print("Number of iterations to determine this: %s" % i)
        print("Shortest edit script (uncompressed): ")
        print(SES[Delta][1:])

    if flag == "noncompressed":
        CES = map(lambda x: (x[0], x[1], x[1]), SES[Delta][1:])
    else:
        CES = compress(SES[Delta][1:])

    if order == "regular":
        return CES
    else:
        return reverse(CES)

#callback(seq, index, total_position)
#source, target's length should match to that of parameter source, target in ses()
def apply(ses, source, target, callback):
    #def handle_re(l, ri):
    #    if ri == None:
    #        return l
    #    for prog, repl in ri:
    #        l = prog.sub(repl, l)
    #    return l
    #def writelines(_list, _list_prefix, write_count, begin, end):
    #    if riw == None:
    #        for i in range(begin, end):
    #            f_nt.write(u'%s%s\n' % (_list_prefix[write_count], _list[i]))
    #    else:
    #        for i in range(begin, end):
    #            f_nt.write(u'%s%s\n' % (_list_prefix[write_count], riw.translate(_list[i])))
    #            write_count += 1
    #    return write_count
        

    count_i = 0
    count_d = 0

    offset = 0
    cy = 0
    
    total_position = 0

    for what, start, stop in ses:
        stop += 1

        if cy + offset < start:
            #if DEBUG:
            #    print "Copy A[%s:%s]: %s" % (cy, start - offset,
            #                                    A[cy:start - offset])

            for i in range(cy, start - offset):
                callback(source, i, total_position)
                total_position += 1

            cy = start - offset

        if what == "i":
            #if DEBUG:
            #    print "Insert B[%s:%s]: %s" % (start, stop, B[start:stop])

            for i in range(start, stop):
                callback(target, i, total_position)
                total_position += 1

            offset += (stop - start)
            count_i += (stop - start)

        else: #elif what == "d":
            #if DEBUG:
            #    print "Delete A[%s:%s]: %s" % (start - offset, stop - offset,
            #                                    A[start - offset:stop - offset])
            #final.append(d_beg)
            #final.append(A[start - offset:stop - offset])
            #final.append(d_end)
            cy = stop - offset
            offset -= (stop - start)
            count_d += (stop - start)

        #else:
        #   print "Unknown command: %s" % what

        #if DEBUG:
        #    print "Offset: %s" % offset
        #    print

    if cy + offset < len(target):
        for i in range(cy, len(source)):
            callback(source, i, total_position)
            total_position += 1

    return count_i, count_d




#def displayCES(A, B, CES, i_beg, i_end, d_beg, d_end):
#    """ Parse through script, printing changed elements of sequence. """

#    DEBUG = 0

#    offset = 0
#    cy = 0
#    final = []
#    for command in CES:
#        what, start, stop = command
#        stop = stop + 1

#        if DEBUG:
#            print "CY:    %s" % cy
#            print "Start:  %s" % start
#            print "Stop:   %s" % stop

#        if cy + offset < start:
#            if DEBUG:
#                print "Copy A[%s:%s]: %s" % (cy, start - offset,
#                                             A[cy:start - offset])
#            final.append(A[cy:start - offset])
#            cy = start - offset

#        if what == "i":
#            if DEBUG:
#                print "Insert B[%s:%s]: %s" % (start, stop, B[start:stop])
#            final.append(i_beg)
#            final.append(B[start:stop])
#            final.append(i_end)
#            offset = offset + (stop - start)

#        elif what == "d":
#            if DEBUG:
#                print "Delete A[%s:%s]: %s" % (start - offset, stop - offset,
#                                               A[start - offset:stop - offset])
#            final.append(d_beg)
#            final.append(A[start - offset:stop - offset])
#            final.append(d_end)
#            cy = stop - offset
#            offset = offset - (stop - start)

#        else:
#            print "Unknown command: %s" % what

#        if DEBUG:
#            print "Offset: %s" % offset
#            print

#    if cy + offset < len(B):
#        final.append(A[cy:])

#    return final
