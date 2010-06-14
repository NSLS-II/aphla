all: hla.pdf
HLA_TMP=hla.tps hla.fns hla.cps hla.vr hla.pg hla.ky hla.tp hla.toc hla.fn hla.cp hla.aux hla.log hlaversion.texi
HGREV = $(shell hg -q id -n)
HGVERSION = $(shell hg id)
hla.pdf: hla.texi
	echo "HG version: ${HGVERSION}"
	echo "[Revision: r${HGREV}]@*" > hlaversion.texi
	echo "[Modified: `hg parents --template '{date|date}'`]" >> hlaversion.texi
	texi2pdf -V hla.texi

clean:
	rm -f ${HLA_TMP}

clean-all:
	rm -f ${HLA_TMP} hla.pdf hla.dvi

