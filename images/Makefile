HS = localhost:5000
DK = docker build
DP = docker push $(HS)/

default: basic analyzers assemblers basecallers correction monolithics trimmers
.PHONY: default basic tests analyzers assemblers basecallers correction monolithics trimmers

tests: basic spades-test


basic:
	$(DK) -t $(HS)/basecase-basic basic/
	$(DK) -t $(HS)/basecase-basic-jre basic/jre/
	$(DP)basecase-basic
	$(DP)basecase-basic-jre

#Assemblers
	
assemblers: basic mhap sga spades

spades: basic
	$(DK) -t $(HS)/spades:latest assemblers/SPAdes/3.1/
	$(DK) -t $(HS)/spades:3.1 assemblers/SPAdes/3.1/
	$(DK) -t $(HS)/spades:3.0 assemblers/SPAdes/3.0/
	$(DP)spades:3.1
	$(DP)spades:3.0
	$(DP)spades:latest
	
mhap: basic
	$(DK) -t $(HS)/mhap:latest assemblers/MHAP/
	$(DP)mhap:latest
	
sga: basic
	$(DK) -t $(HS)/sga:latest assemblers/SGA/
	$(DP)sga:latest
	
#Analyzers
	
analyzers: basic circos 

circos: basic
	#$(DK) -t $(HS)/circos:latest analyzers/Circos/
	#@touch analyzers/Circos/.build

#Basecallers

basecallers: basic

#Reads correction tools

correction: basic

#Monolithic superpackages

monolithics: basic smrtportal snp-pipeline qiime

smrtportal: basic
	$(DK) -t $(HS)/smrtportal:latest monolithics/SMRTPortal/2.2.0
	$(DK) -t $(HS)/smrtportal:2.2.0 monolithics/SMRTPortal/2.2.0
	$(DP)smrtportal:latest
	
snp-pipeline: basic

qiime: basic

#Reads trimmers

trimmers: basic fastx-trimmer scythe

fastx-trimmer: basic
	$(DK) -t $(HS)/fastx-trimmer:latest trimmers/fastx-trimmer/0.0.14
	$(DK) -t $(HS)/fastx-trimmer:0.0.14 trimmers/fastx-trimmer/0.0.14
	$(DP)fastx-trimmer:latest
	
scythe: basic
	
	
#Tests

spades-test: basic spades
	$(DK) -t spades-test tests/spades/
	$(DP)spades-test
