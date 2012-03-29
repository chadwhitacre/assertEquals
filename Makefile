# (c) 2005-2012 Chad Whitacre <http://www.zetadev.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

prefix=/usr/local
version=0.4


configure:
# create the script to be installed
	rm -f assertEquals
	cp bin/assertEquals assertEquals
	chmod 555 assertEquals

# [re]create the man page to be installed
	rm -f assertEquals.1.gz
	gzip -c -9 doc/man1/assertEquals.1 > assertEquals.1.gz
	chmod 444 assertEquals.1.gz


clean:
# remove all of the cruft that gets auto-generated on doc/install/release
	rm -f assertEquals assertEquals.1.gz
	rm -rf build
	rm -rf dist
	find . -name \*.pyc | xargs rm
	make -C doc/tex clean


install: configure
	install -o root -m 555 assertEquals ${prefix}/bin
	install -o root -m 444 assertEquals.1.gz ${prefix}/man/man1
	python setup.py install


uninstall:
	rm -f ${prefix}/bin/assertEquals
	rm -f ${prefix}/man/man1/assertEquals.1.gz




# Target for building a distribution
# ==================================

dist: clean
	mkdir dist
	mkdir dist/assertEquals-${version}
	cp -r Makefile README bin site-packages setup.py dist/assertEquals-${version}

	make -C doc/tex html pdf clean
	mkdir dist/assertEquals-${version}/doc
	cp -r doc/html doc/assertEquals* dist/assertEquals-${version}/doc

	find dist/assertEquals-${version} -name \.svn | xargs rm -r
	tar --directory dist -zcf dist/assertEquals-${version}.tgz assertEquals-${version}
	tar --directory dist -jcf dist/assertEquals-${version}.tbz assertEquals-${version}

# ZIP archive gets different line endings and script name
	svneol clean -w dist/assertEquals-${version}
	mv dist/assertEquals-${version}/bin/assertEquals.py dist/assertEquals-${version}/bin/assertEquals
	cd dist && zip -9rq assertEquals-${version}.zip assertEquals-${version}
#	rm -rf dist/assertEquals-${version}




# Run our tests using ourself.
# ============================
# This was added for Grig's buildbot: http://pybots.org/. The demos are removed
# because they yield errors/failures (on purpose).

test:
	python bin/assertEquals -s -x demo assertEquals.tests
