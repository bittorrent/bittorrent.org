BEPs are written as reStructured Text (.rst) files.
To create an html file from an rst file:

1. Write your rst file
2. Add the filename to the list of files in the "all:" section of the `beps/Makefile`.
3. `pip install -r beps/requirements.txt`
4. `cd beps && make all`
