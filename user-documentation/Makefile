all: documentation.pdf

documentation.pdf: documentation.tex
	TEXINPUTS=".:../style:$$TEXINPUTS" latexmk -pdf -interaction=nonstopmode -halt-on-error documentation.tex

clean:
	latexmk -c

distclean: clean
	rm -f documentation.pdf