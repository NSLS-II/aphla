all: hla.pdf
HLA_TMP=hla.tps hla.fns hla.cps hla.vr hla.pg hla.ky hla.tp hla.toc hla.fn hla.cp hla.aux hla.log hlaversion.texi
HLA_UG_TMP=hla_ug.log hla_ug.aux hla_ug.ind hla_ug.ilg hla_ug.toc hla_ug.out hla_ug.blg hla_ug.bbl hla_ug.idx
HLA_API_TMP=hla_api.tps hla_api.fns hla_api.cps hla_api.vr hla_api.pg hla_api.ky hla_api.tp hla_api.toc hla_api.fn hla_api.cp hla_api.aux hla_api.log hlaversion.texi
HGREV = $(shell hg -q id -n)
HGVERSION = $(shell hg id)

DATE = $(shell hg parents --template '{date|shortdate}')
FILE = $(join HLA_Spec_, ${DATE})
FILENAME = $(addsuffix .pdf, $(FILE))

all: hla.pdf hla_ug.pdf hla_api.pdf

hla.pdf: hla.texi
	echo "HG version: ${HGVERSION}"
	echo "[Revision: r${HGREV}]@*" > hlaversion.texi
	echo "[Modified: `hg parents --template '{date|date}'`]" >> hlaversion.texi
	texi2pdf -V hla.texi
	cp hla.pdf ${FILENAME}

hla_ug.pdf: hla_ug.tex
	makeindex hla_ug
#	bibtex hla_ug
	pdflatex hla_ug
	pdflatex hla_ug
hla_api.pdf: hla_api.texi
	echo "HG version: ${HGVERSION}"
	echo "[Revision: r${HGREV}]@*" > hlaversion.texi
	echo "[Modified: `hg parents --template '{date|date}'`]" >> hlaversion.texi
	texi2pdf -V hla_api.texi

clean:
	rm -f ${HLA_TMP} ${HLA_UG_TMP} ${HLA_API_TMP}

clean-all:
	rm -f ${HLA_TMP} hla.pdf hla.dvi

