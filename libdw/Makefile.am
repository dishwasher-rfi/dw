## Process this file with automake to produce Makefile.in
## Created by Anjuta

SUBDIRS = src 

libdwdocdir = ${prefix}/doc/libdw
libdwdoc_DATA = \
	README\
	COPYING\
	AUTHORS\
	ChangeLog\
	INSTALL\
	NEWS


EXTRA_DIST = $(libdwdoc_DATA)


# Remove doc directory on uninstall
uninstall-local:
	-rm -r $(libdwdocdir)
