'''

Example:

Below example seem simple at first but it does a lot. It simply merges different

profiling results of a function together into a single file and save it as 

<function_name>.profile.

'''

import yappi

def aggregate(func, stats):

    fname = "%s.profile" % (func.__name__)

    try: 

        stats.add(fname)

    except IOError:

        pass

    stats.save(fname)
