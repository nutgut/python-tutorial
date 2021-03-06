#!/usr/bin/env python3

# This is free and unencumbered software released into the public
# domain.

# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a
# compiled binary, for any purpose, commercial or non-commercial, and
# by any means.

# In jurisdictions that recognize copyright laws, the author or
# authors of this software dedicate any and all copyright interest in
# the software to the public domain. We make this dedication for the
# benefit of the public at large and to the detriment of our heirs
# and successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to
# this software under copyright law.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# For more information, please refer to <http://unlicense.org>

"""Check for broken links.

This finds links like this...

    [click here](some-file.md)
    [or here](../some/path/another-file.md)
    ![here's an image](../images/some-cool-image.png)

...but not like this:

    [some website](http://github.com/)
    [another website](https://github.com/)
    [local header](#some-header)
"""

import os
import posixpath

import common


def check(filepath, target):
    """Check if a link's target is like it should be.

    Return an error message string or "ok".
    """
    if target.startswith(('http://', 'https://')):
        # We don't need this currently, but checking these links could
        # be added later.
        return "ok"

    if '#' in target:
        where = target.index('#')
        if where == 0:
            # It's a link to a title in the same file, we need to skip it.
            return "ok"
        target = target[:where]

    path = posixpath.join(posixpath.dirname(filepath), target)
    realpath = common.slashfix(path)
    if not os.path.exists(realpath):
        return "doesn't exist"
    if target.endswith('/'):
        # A directory.
        if os.path.isdir(realpath):
            return "ok"
        return "not a directory"
    else:
        # A file.
        if os.path.isfile(realpath):
            return "ok"
        return "not a file"


def main():
    print("Searching and checking links...")
    broken = 0
    total = 0
    for path in common.get_markdown_files():
        with common.slashfix_open(path, 'r') as f:
            for match, lineno in common.find_links(f):
                text, target = match.groups()
                status = check(path, target)
                if status != "ok":
                    # The .group(0) is not perfect, but it's good enough.
                    print("  file %s, line %d: %s" % (path, lineno, status))
                    print("    " + match.group(0))
                    print()
                    broken += 1
                total += 1
    print("%d/%d links seem to be broken." % (broken, total))


if __name__ == '__main__':
    main()
