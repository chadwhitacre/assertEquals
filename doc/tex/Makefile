# Makefile to create documentation using the Python LaTeX system.

VERSION=0.4.2
PYTHON_SRC = /Users/whit537/src/Python-2.4.2
MKHOWTO    = $(PYTHON_SRC)/Doc/tools/mkhowto \
				--iconserver icons \
				--split 5 \
				--link 2 \
				--favicon icons/zeta.ico \
				--dir ./html \
				--logging \
				--up-link "https://github.com/whit537/assertEquals" \
				--up-title "assertEquals homepage" \
				--address "<a href=\"https://github.com/whit537/assertEquals\">assertEquals</a> is copyright &copy; 2005-2012 by Chad Whitacre, and is offered free of charge, warranty, and restrictions." \
#				--style style.css


default: html

html: clean
	$(MKHOWTO) assertEquals.tex
	cp -r ../icons ./html/
	rm -rf ../../../assertEqualsDocs/* && mv ./html/* ../../../assertEqualsDocs/ && rm -rf ./html

pdf:
	$(PYTHON_SRC)/Doc/tools/mkhowto --pdf assertEquals.tex
	mv assertEquals.pdf ../assertEquals-$(VERSION).pdf

clean:
	rm -rf *~ *.aux *.idx *.ilg *.ind *.log *.toc *.bkm *.syn \
			*.pla *.eps *.pdf *.ps *.lof *.l2h *.tex2 *.dvi html ../*.pdf
