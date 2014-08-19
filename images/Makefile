HS = localhost:5000
DK = docker build
DP = docker push $(HS)/

default: basic analyzers assemblers basecallers correction monolithics trimmers
.PHONY: default

tests: basic spades-test

basic: basic/.build

basic/.build:
	$(DK) -t $(HS)/basecase-basic basic/
	$(DK) -t $(HS)/basecase-basic-jre basic/jre/
	$(DP)basecase-basic
	$(DP)basecase-basic-jre
	@touch basic/.build

#Assemblers
	
assemblers: basic mhap sga spades

spades: basic assemblers/SPAdes/.build

assemblers/SPAdes/.build: 
	$(DK) -t $(HS)/spades:latest assemblers/SPAdes/3.1/
	$(DK) -t $(HS)/spades:3.1 assemblers/SPAdes/3.1/
	$(DK) -t $(HS)/spades:3.0 assemblers/SPAdes/3.0/
	@touch assemblers/SPAdes/.build
	
mhap: basic assemblers/MHAP/.build

assemblers/MHAP/.build:
	$(DK) -t $(HS)/mhap:latest assemblers/MHAP/
	@touch assemblers/MHAP/.build
	
sga: basic assemblers/SGA/.build

assemblers/SGA/.build:
	$(DK) -t $(HS)/sga:latest assemblers/SGA/
	@touch assemblers/SGA/.build
	
#Analyzers
	
analyzers: basic circos 

circos: basic analyzers/Circos/.build

analyzers/Circos/.build:
	#$(DK) -t $(HS)/circos:latest analyzers/Circos/
	#@touch analyzers/Circos/.build

#Basecallers

basecallers: basic

#Reads correction tools

correction: basic

#Monolithic superpackages

monolithics: basic smrtportal snp-pipeline qiime

smrtportal: basic monolithics/SMRTPortal/.build

monolithics/SMRTPortal/.build:
	$(DK) -t $(HS)/smrtportal:latest monolithics/SMRTPortal/2.2.0
	$(DK) -t $(HS)/smrtportal:2.2.0 monolithics/SMRTPortal/2.2.0
	@touch monolithics/SMRTPortal/.build
	
snp-pipeline: basic

qiime: basic

#Reads trimmers

trimmers: basic fastx-trimmer scythe

fastx-trimmer: basic trimmers/fastx-trimmer/.build

trimmers/fastx-trimmer/.build:
	$(DK) -t $(HS)/fastx-trimmer:latest trimmers/fastx-trimmer/0.0.14
	$(DK) -t $(HS)/fastx-trimmer:0.0.14 trimmers/fastx-trimmer/0.0.14
	@touch trimmers/fastx-trimmer/.build
	
scythe: basic
	
	
#Tests

spades-test: basic spades
	$(DK) -t spades-test tests/spades/