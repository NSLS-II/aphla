all: hla.pdf
HLA_TMP=hla.tps hla.fns hla.cps hla.vr hla.pg hla.ky hla.tp hla.toc hla.fn hla.cp hla.aux hla.log
hla.pdf: hla.texi
	texi2pdf -V hla.texi

clean:
	rm -f ${HLA_TMP}

clean-all:
	rm -f ${HLA_TMP} hla.pdf hla.dvi

