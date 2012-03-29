# (c) 2005-2012 Chad Whitacre <http://www.zetadev.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

prefix=/usr/local
version=0.4


configure:
# create the script to be installed
	rm -f testosterone
	cp bin/testosterone testosterone
	chmod 555 testosterone

# [re]create the man page to be installed
	rm -f testosterone.1.gz
	gzip -c -9 doc/man1/testosterone.1 > testosterone.1.gz
	chmod 444 testosterone.1.gz


clean:
# remove all of the cruft that gets auto-generated on doc/install/release
	rm -f testosterone testosterone.1.gz
	rm -rf build
	rm -rf dist
	find . -name \*.pyc | xargs rm
	make -C doc/tex clean


install: configure
	install -o root -m 555 testosterone ${prefix}/bin
	install -o root -m 444 testosterone.1.gz ${prefix}/man/man1
	python setup.py install


uninstall:
	rm -f ${prefix}/bin/testosterone
	rm -f ${prefix}/man/man1/testosterone.1.gz




# Target for building a distribution
# ==================================

dist: clean
	mkdir dist
	mkdir dist/testosterone-${version}
	cp -r Makefile README bin site-packages setup.py dist/testosterone-${version}

	make -C doc/tex html pdf clean
	mkdir dist/testosterone-${version}/doc
	cp -r doc/html doc/testosterone* dist/testosterone-${version}/doc

	find dist/testosterone-${version} -name \.svn | xargs rm -r
	tar --directory dist -zcf dist/testosterone-${version}.tgz testosterone-${version}
	tar --directory dist -jcf dist/testosterone-${version}.tbz testosterone-${version}

# ZIP archive gets different line endings and script name
	svneol clean -w dist/testosterone-${version}
	mv dist/testosterone-${version}/bin/testosterone.py dist/testosterone-${version}/bin/testosterone
	cd dist && zip -9rq testosterone-${version}.zip testosterone-${version}
#	rm -rf dist/testosterone-${version}




# Run our tests using ourself.
# ============================
# This was added for Grig's buildbot: http://pybots.org/. The demos are removed
# because they yield errors/failures (on purpose).

test:
	python bin/testosterone -s -x demo testosterone.tests
