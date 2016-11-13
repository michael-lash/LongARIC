#!/usr/bin/env python
import argparse
import os,sys
import logging, pprint
import csv
from utils import writeRes

def getIDs(inFile):
 	'''
	Helper fuction that collects the IDs from an original Visit 1 defined criteria,
	which excludes unsuitable patients based on whether they had one the CVD events
	prior to the start of the study
	'''   
	iFile = open(inFile, 'rb')
	fReader = csv.reader(iFile,delimiter=',')
	ids = []
	for row in fReader:
		ids.append(row[0])

	iFile.close()
	return ids

def establishPatVals(patSet,exYr,exFiles,yrNames,eventYrs,eventFiles,eventVals,idRName):
	'''
	This function takes the full set of patIDs, excludes those that don't belong and
	sets the event indicator equal to "1" or "0", as appropriate
	'''
	patDict = {}
	for pat in patSet:
		patDict[pat] = {'outcome':0}
	
	weirdCollis = 0
	exclCount = 0
	yesCount = 0
	for f in eventFiles.keys():
		eFeats = eventFiles[f]
		with open(f,'rU') as iFile:
			fReader = csv.reader(iFile,delimiter=',')
			rCounter = 0
			for row in fReader:
				rCounter +=1
				if rCounter == 1:
					eFeatInd = {}
					for eF in eFeats:
						eFeatInd[eF] = row.index(eF)
					idInd = row.index(idRName)
					if yrNames[f] != "":
						yrInd = row.index(yrNames[f])
					else:
						yrInd = 'NA'
				else:
					if row[idInd] in patDict.keys():
						if yrInd != 'NA':
							if int(row[yrInd]) <= int(exYr):
								for eFV in eFeatInd.keys():
									if row[eFeatInd[eFV]] in eventVals[eFV]:
										try:
											del patDict[row[idInd]]
											patSet.remove(row[idInd])
											exclCount +=1
										except:
											weirdCollis+=1
							elif row[yrInd] in eventYrs:
								for eFV in eFeatInd.keys():
									if row[eFeatInd[eFV]] in eventVals[eFV]:
										patDict[row[idInd]]['outcome']= 1
										yesCount+=1
						else:#Means we're looking at a file specific to defining outcome events (not excluding)
							for eFV in eFeatInd.keys():
								if row[eFeatInd[eFV]] in eventVals[eFV]:
									patDict[row[idInd]]['outcome'] = 1
									yesCount+=1

		iFile.close()

	# Now look only at exclusion files
	for f in exFiles.keys():
		exFeats = exFiles[f]
		with open(f,'rU') as iFile:
			fReader = csv.reader(iFile,delimiter=',')
			rCounter = 0
			for row in fReader:
				rCounter+=1
				if rCounter == 1:
					exFeatInd = {}
					for exF in exFeats:
						exFeatInd[exF] = row.index(exF)
					idInd = row.index(idRName)
				else:
					if row[idInd] in patDict.keys():
						for exFV in exFeatInd.keys():
							if row[exFeatInd[exFV]] in eventVals[exFV]:
								del patDict[row[idInd]]
								patSet.remove(row[idInd])
								exclCount +=1
		iFile.close()
			
	print ("Finished excluding patients and defining outcomes... "+str(exclCount)+" patients excluded... "+str(yesCount)+" positive inst...")
	if weirdCollis > 0:
		print("There were "+str(weirdCollis)+" patients who were excluded and were -- for some reason -- attempted to be removed again...")
	return patDict


def main(args):
	#need to re-write code for this task
	#begin with defining file names
	ids = getIDs(args.inFile)
    	
	#root directory appended to the beginning of each file name
	rootDir = args.rootDir
	v1Dir = "V1/csv/"
	v2Dir = "V2/csv/"
	v3Dir = "V3/csv/"
	v4Dir = "V4/csv/"


	#the individual files and the corresponding column names that should be checked
	#look into: "comm_CHD/csv/sevtps10.csv":["INCFATCHD"]
	
	#### visitYrs defines the years in which we look for events ####
	### exclYrs defines the years in which we will excluded patients

	if args.visit == 'V1':## Visit 1 ##
		exclYrs = '1989'
		visitYrs = ['1990','1991','1992']
	elif args.visit == 'V2':## Visit 2 ##
		exclYrs = '1992'
		visitYrs = ['1993','1994','1995']
	elif args.visit == 'V3':## Visit 3 ##
		exclYrs = '1995'
		visitYrs = ['1996','1997','1998']
	else:
		print("Visit identifier not recognized...should be one of: 'V1', 'V2', or 'V3'...exitting...")
		sys.exit()	

	#### outcomeFiles define when a patient outcome should be coded as '1' vs '0' (i.e., yes/no) #####
	if args.visit == 'V1':## Visit 1 ##
		#not using: "V2/csv/derive2_10.csv":["PRVSTR21","MDDXMI21","ECGMI24","MACHMI22"],
		outcomeFiles = {rootDir+v2Dir+"stroke2.csv":["STROKE21"],#denoted "Y" if they did have a stroke
				rootDir+"comm_CHD/csv/sevtps10.csv":["MIDX3","FATALDX3"]
				}
		yearCols = {rootDir+v2Dir+"stroke2.csv":"",
				rootDir+"comm_CHD/csv/sevtps10.csv":"EVTYR"} 
	elif args.visit == 'V2':## Visit 2 ##

		#old: "V3/csv/derive37.csv":["PRVSTR31","MDDXMI31","ECGMI31","MACHMI31"],
		outcomeFiles = {rootDir+v3Dir+"stroke32.csv":["STROKE31"],
				rootDir+"comm_CHD/csv/sevtps10.csv":["MIDX3","FATALDX3"]
				}
		yearCols = {rootDir+v3Dir+"stroke32.csv":"",
                                rootDir+"comm_CHD/csv/sevtps10.csv":"EVTYR"}

	elif args.visit == 'V3':## Visit 3 ##
	
		#old: "V4/csv/derive47.csv":["PRVSTR41","MDDXMI41","ECGMI41","MACHMI41"],
		outcomeFiles = {rootDir+v4Dir+"stroke41.csv":["STROKE41"],
				rootDir+"comm_CHD/csv/sevtps10.csv":["MIDX3","FATALDX3"]
				}
		yearCols = {rootDir+v4Dir+"stroke41.csv":"",
                                rootDir+"comm_CHD/csv/sevtps10.csv":"EVTYR"}

	#No need for else here: caught above

	##### excludeFiles defines the files used to exclude IDs #####

	if args.visit == 'V1':## Visit 1##
		excludeFiles = {}
	elif args.visit == 'V2':## Visit 2##
		#old:  "V2/csv/derive2_10.csv":["PRVSTR21","MDDXMI21","ECGMI24","MACHMI22"],
		excludeFiles = {rootDir+v2Dir+"stroke2.csv":["STROKE21"]#denoted "Y" if they did have a stroke
		                }
	elif args.visit == 'V3':## Visit 3 ##
		#old: "V3/csv/derive37.csv":["PRVSTR31","MDDXMI31","ECGMI31","MACHMI31"],
		excludeFiles = {rootDir+v3Dir+"stroke32.csv":["STROKE31"]
		                }
	#No need for else here: caught above

	#the value that designates a 'positive' finding for each of the columns being checked
	outDataType = {"STROKE21":["Y"],"STROKE31":["Y"],"STROKE41":["Y"],
			"MIDX3":["DEFMI","SUSPMI","PROBMI"], "FATALDX3":["POSSFATCHD","DEFFATCHD"]
		}

	#### The file and features we need to collect for each patient ####

	if args.visit == 'V1':## Visit 1 ##
		fD = rootDir + v1Dir
		featureFiles = {fD+"anta.csv":["ANTA01","ANTA04","ANTA05B","ANTA07A","ANTA07B","ANTA07C","ANTA06B"],
				fD+"anut2.csv":["MFAT","PROT","AFAT","VFAT","DFIB","SFAT","PFAT","CHOL","ALCO",
						"CAFF","SODI","TFAT","P_TFAT","P_ALC","P_PROT","P_AFAT","P_VFAT",
						"P_CARB","P_SFAT","P_PFAT","CARB","SUCR","LACT","FRUC","OMEGA","P_MFAT"],
				fD+"chma.csv":["CHMA05","CHMA06","CHMA08","CHMA09","CHMA10","CHMA11","CHMA12","CHMA13",
						"CHMA14","CHMA15","CHMA16"],
				fD+"derive13.csv":["STATINCODE01","ASPIRINCODE01","RACEGRP","GENDER","CIGTYR01",
						"BMI01","MNTRCP01","MNSSCP01","WSTHPR01","GLUCOS01","TGLEFH01",
						"GLUSIU01","TCHSIU01","ELEVEL01","DIABTS02","EVRSMK01","INTPS01",
						"ABI04","PAD01","PAD02","INTPLQ01","CHOLMDCODE01","HYPERT05",
						"MENOPS01","HDL01","LDL02","TRGSIU01","LVHSCR01","V1AGE01"],
				fD+"hmta.csv":["HMTA01","HMTA02","HMTA03","HMTA04","HMTA05","HMTA06","HMTA07","HMTA08",
						"HMTA09","HMTA10"],
				fD+"hom.csv":["HOM32"],
				fD+"rhxa.csv":["RHXA08"],
				fD+"msra.csv":["MSRA08A","MSRA08B","MSRA08C","MSRA08D","MSRA08E","MSRA08F","MSRA08G",
						"MSRA08H","MSRA09","MSRA10"],
				fD+"sbpa02.csv":["SBPA21","SBPA22"],
				fD+"ecgma03.csv":["ECGMA31"],
				fD+"lipa.csv":["LIPA06","LIPA07","LIPA08"],
				fD+"pulm.csv":["FEV1FVC1"],
				fD+"pfta.csv":["PFTA24","PFTA26"],
				fD+"hema.csv":["HEMA05","HEMA07","HEMA09","HEMA11","HEMA13","HEMA15","HEMA17"],
				fD+"dtia.csv":["DTIA51","DTIA52","DTIA55","DTIA66","DTIA67"]
				}

		## These are files and features that should be aggregated to a single feeature
		aggFeats = {fD+"dtia.csv":[{"w_carb":["DTIA50","DTIA53","DTIA54","DTIA56","DTIA57","DTIA58"]},
					{"veges":["DTIA15","DTIA16","DTIA17","DTIA18","DTIA19","DTIA20",
					"DTIA21","DTIA22","DTIA23","DTIA24","DTIA25"]},
					{"fruit":["DTIA09","DTIA10","DTIA12","DTIA13","DTIA14"]},
					{"fish":["DTIA34","DTIA35","DTIA36","DTIA37"]},
					{"cereals":["DTIA48","DTIA49"]}],
				fD+"rpaa02.csv":[{"sport_hrs":["RPAA49","RPAA53","RPAA57","RPAA61"]}
				]}
		## prevFeats are to acquire features from previous years -- these are delineated separately although
		### could be included in featureFiles
		prevFeats = {}
		## This specifies the order in which the features should be output
		orderedFeats = ["CHMA16","ANTA01","V1AGE01","PAD01","PAD02","INTPS01","INTPLQ01","HYPERT05",
				"ELEVEL01","DIABTS02","RHXA08","MENOPS01","EVRSMK01","MSRA08A","MSRA08B","MSRA08C","MSRA08D",
				"MSRA08E","MSRA08F","MSRA08G","MSRA08H","MSRA09","MSRA10","GENDER","RACEGRP","CIGTYR01","BMI01",
				"HDL01","LDL02","TCHSIU01","TRGSIU01","SBPA21","SBPA22","ANTA07A","ANTA07B","ECGMA31","HMTA03",
				"LIPA06","LIPA07","LIPA08","ABI04","FEV1FVC1","PFTA26","PFTA24","HMTA01","HMTA02","HMTA04","HMTA05",
				"HMTA06","HMTA07","HMTA08","HMTA09","HMTA10","HEMA05","HEMA07","HEMA09","HEMA11","HEMA13","HEMA15",
				"HEMA17","LVHSCR01","WSTHPR01","MNTRCP01","MNSSCP01","P_VFAT","P_CARB","P_ALC","P_AFAT",
				"TGLEFH01","OMEGA","ANTA07C","ANTA06B","GLUCOS01","GLUSIU01",
				"ANTA05B","CHMA15","CHMA14","CHMA13","CHMA12","CHMA11","CHMA10","CHMA08","CHMA06","CHMA05",
				"CHMA09","ANTA04","P_TFAT","P_SFAT","P_PROT","P_PFAT","P_MFAT","TFAT","DTIA51","DTIA52",
				"DTIA55","DTIA66","DTIA67","w_carb","veges","fruit","fish","cereals","ALCO","HOM32","sport_hrs",
				"CAFF","CARB","CHOL","DFIB","SODI","AFAT","VFAT","SFAT","PFAT","MFAT","PROT","SUCR","LACT","FRUC",
				"STATINCODE01","ASPIRINCODE01","CHOLMDCODE01","outcome"
				]
		
		listOrdFeats1 = ["DTIA51","DTIA52","DTIA55","DTIA50","DTIA53","DTIA54","DTIA56","DTIA57","DTIA58",
				"DTIA15","DTIA16","DTIA17","DTIA18","DTIA19","DTIA20","DTIA21","DTIA22","DTIA23","DTIA24","DTIA25",
				"DTIA09","DTIA10","DTIA12","DTIA13","DTIA14","DTIA34","DTIA35","DTIA36","DTIA37","DTIA48","DTIA49"]
		listOrdFeats2 = ["DTIA66"]
		listOrdFeats3 = ["RPAA49","RPAA53","RPAA57","RPAA61"]
		listBinFeats = ["MSRA08A","MSRA08B","MSRA08C","MSRA08D","MSRA08E","MSRA08F","MSRA08G","MSRA08H","MSRA09","MSRA10",
				"DTIA67"]
		listGen = ["GENDER"]
		listRGrp = ["RACEGRP"]
		


	
	elif args.visit == 'V2':## Visit 2 ##
		fD = rootDir + v2Dir
		featureFiles = {fD+"antb.csv":["ANTB01","ANTB02B","ANTB03B","ANTB04A","ANTB04B"],
				fD+"nutv2.csv":["MFAT","PROT","AFAT","VFAT","DFIB","SFAT","PFAT","CHOL","ALCO",
                                                "CAFF","SODI","TFAT","P_TFAT","P_ALC","P_PROT","P_AFAT","P_VFAT",
                                                "P_CARB","P_SFAT","P_PFAT","CARB","SUCR","LACT","FRUC","OMEGA","P_MFAT"],
				fD+"chmb.csv":["CHMB05","CHMB06","CHMB08","CHMB09","CHMB10"],
				fD+"derive2_10.csv":["STATINCODE21","ASPIRINCODE21","RACEGRP","GENDER",
                                                "BMI21","MNTRCP21","MNSSCP21","WSTHPR21","TGLEFH21",
                                                "GLUSIU21","TCHSIU21","DIABTS22","EVRSMK21","INTPS21",
                                                "INTPLQ21","CHOLMDCODE21","HYPERT25",
                                                "MENOPS21","HDL221","LDL22","TRGSIU21","LVHSCR21","V2AGE22"],
				fD+"hmtb.csv":["HMTB01","HMTB02","HMTB03","HMTB04","HMTB05","HMTB06","HMTB07",
						"HMTB08","HMTB09","HMTB10"],
				fD+"hhxb.csv":["HHXB48"], # Same as HOM32 -- num cig smoked
				fD+"msrb.csv":["MSRB24A","MSRB24B","MSRB24C","MSRB24D","MSRB24E","MSRB24F",
						"MSRB24G","MSRB24H","MSRB25","MSRB26"],
				fD+"sbpb02.csv":["SBPB21","SBPB22"],
				fD+"ecgmb22.csv":["ECGMB31"],
				fD+"pulm21.csv":["FEV1FVC2"],
				fD+"pftb.csv":["PFTB24","PFTB26"],
				fD+"dtib.csv":["DTIB51","DTIB52","DTIB55","DTIB66","DTIB67"]
				}

		aggFeats = {fD+"dtib.csv":[{"w_carb":["DTIB50","DTIB53","DTIB54","DTIB56","DTIB57","DTIB58"]},
                                        {"veges":["DTIB15","DTIB16","DTIB17","DTIB18","DTIB19","DTIB20",
                                        "DTIB21","DTIB22","DTIB23","DTIB24","DTIB25"]},
                                        {"fruit":["DTIB09","DTIB10","DTIB12","DTIB13","DTIB14"]},
                                        {"fish":["DTIB34","DTIB35","DTIB36","DTIB37"]},
                                        {"cereals":["DTIB48","DTIB49"]}]

                                }
                ## prevFeats are to acquire features from previous years -- these are delineated separately although
                ### could be included in featureFiles
                prevFeats = {rootDir+v1Dir+"anta.csv":["ANTA01"],
				rootDir+v1Dir+"derive13.csv":["ELEVEL01"]
                                }

		orderedFeats = ["ANTA01","V2AGE22","INTPS21","INTPLQ21","HYPERT25",
                                "ELEVEL01","DIABTS22","MENOPS21","EVRSMK21","MSRB24A","MSRB24B","MSRB24C","MSRB24D",
                                "MSRB24E","MSRB24F","MSRB24G","MSRB24H","MSRB25","MSRB26","GENDER","RACEGRP","BMI21",
                                "HDL221","LDL22","TCHSIU21","TRGSIU21","SBPB21","SBPB22","ANTB04A","ANTB04B","ECGMB31","HMTB03",
                                "FEV1FVC2","PFTB26","PFTB24","HMTB01","HMTB02","HMTB04","HMTB05",
                                "HMTB06","HMTB07","HMTB08","HMTB09","HMTB10","GLUSIU21",
				"LVHSCR21","WSTHPR21","MNTRCP21","MNSSCP21","P_VFAT","P_CARB","P_ALC","P_AFAT",
                                "TGLEFH21","OMEGA","ANTB03B",
                                "ANTB02B","CHMB10","CHMB09","CHMB08","CHMB06","CHMB05",
                                "ANTB01","P_TFAT","P_SFAT","P_PROT","P_PFAT","P_MFAT","TFAT","DTIB51","DTIB52",
                                "DTIB55","DTIB66","DTIB67","w_carb","veges","fruit","fish","cereals","ALCO","HHXB48",
                                "CAFF","CARB","CHOL","DFIB","SODI","AFAT","VFAT","SFAT","PFAT","MFAT","PROT","SUCR","LACT","FRUC",
                                "STATINCODE21","ASPIRINCODE21","CHOLMDCODE21","outcome"
                                ]

		listOrdFeats1 = ["DTIB51","DTIB52","DTIB55","DTIB50","DTIB53","DTIB54","DTIB56","DTIB57","DTIB58",
                                "DTIB15","DTIB16","DTIB17","DTIB18","DTIB19","DTIB20","DTIB21","DTIB22","DTIB23","DTIB24","DTIB25",
                                "DTIB09","DTIB10","DTIB12","DTIB13","DTIB14","DTIB34","DTIB35","DTIB36","DTIB37","DTIB48","DTIB49"]
		listOrdFeats2 = ["DTIB66"]
		listOrdFeats3 = []
		listBinFeats = ["MSRB24A","MSRB24B","MSRB24C","MSRB24D","MSRB24E","MSRB24F","MSRB24G","MSRB24H","MSRB25",
				"MSRB26","DTIB67"]
		listGen = ["GENDER"]
                listRGrp = ["RACEGRP"]




	elif args.visit == 'V3':## Visit 3 ##
		fD = rootDir + v3Dir
		featureFiles = {fD+"antc04.csv":["ANTC1","ANTC2"],
				fD+"nutv3.csv":["MFAT","PROT","AFAT","VFAT","DFIB","SFAT","PFAT","CHOL","ALCO",
                                                "CAFF","SODI","TFAT","P_TFAT","P_ALC","P_PROT","P_AFAT","P_VFAT",
                                                "P_CARB","P_SFAT","P_PFAT","CARB","SUCR","LACT","FRUC","OMEGA","P_MFAT"],
				fD+"derive37.csv":["STATINCODE31","ASPIRINCODE31","BMI32","WSTHPR31","TCHSIU31",
						"DIABTS33","EVRSMK31","INTPS31","ABI34","PAD31","PAD32","INTPLQ31",
						"CHOLMDCODE31","HYPERT35","MENOPS31","HDLSIU31","LDL32","TRGSIU31",
						"LVHSCR31","V3AGE31"],
				fD+"hmtcv301.csv":["HMTC2","HMTC4","HMTC5","HMTC6","HMTC7","HMTC8",
						"HMTC9","HMTC10"],
				fD+"phxa04.csv":["PHXA30"],
				fD+"rhxb04.csv":["RHXB7"],
				fD+"msrc04.csv":["MSRC24A","MSRC24B","MSRC24C","MSRC24D","MSRC24E","MSRC25","MSRC28"],
				fD+"sbpc04_02.csv":["SBPC22","SBPC23"],
				fD+"ecgmc35.csv":["ECGMC31"],
				fD+"dtic04.csv":["DTIC51","DTIC52","DTIC55","DTIC66","DTIC67"]
				}
		aggFeats = {fD+"dtic04.csv":[{"w_carb":["DTIC50","DTIC53","DTIC54","DTIC56","DTIC57","DTIC58"]},
                                        {"veges":["DTIC15","DTIC16","DTIC17","DTIC18","DTIC19","DTIC20",
                                        "DTIC21","DTIC22","DTIC23","DTIC24","DTIC25"]},
                                        {"fruit":["DTIC9","DTIC10","DTIC12","DTIC13","DTIC14"]},
                                        {"fish":["DTIC34","DTIC35","DTIC36","DTIC37"]},
                                        {"cereals":["DTIC48","DTIC49"]}],
				fD+"rpac04.csv":[{"sport_hrs":["RPAC10","RPAC14","RPAC18","RPAC22"]}
                                ]}
                ## prevFeats are to acquire features from previous years -- these are delineated separately although
                ### could be included in featureFiles
                prevFeats = {rootDir+v2Dir+"derive2_10.csv":["RACEGRP","GENDER"],
				rootDir+v1Dir+"derive13.csv":["ELEVEL01"]
                                }
		
		orderedFeats = ["ANTC1","V3AGE31","PAD31","PAD32","INTPS31","INTPLQ31","HYPERT35",
                                "ELEVEL01","DIABTS33","RHXB7","MENOPS31","EVRSMK31","MSRC24A","MSRC24B","MSRC24C","MSRC24D",
                                "MSRC24E","MSRC25","MSRC28","GENDER","RACEGRP","BMI32",
                                "HDLSIU31","LDL32","TCHSIU31","TRGSIU31","SBPC22","SBPC23","ECGMC31",
                                "ABI34","HMTC2","HMTC4","HMTC5",
                                "HMTC6","HMTC7","HMTC8","HMTC9","HMTC10",
                                "LVHSCR31","WSTHPR31","P_VFAT","P_CARB","P_ALC","P_AFAT",
                                "OMEGA",
                                "ANTC2","P_TFAT","P_SFAT","P_PROT","P_PFAT","P_MFAT","TFAT","DTIC51","DTIC52",
                                "DTIC55","DTIC66","DTIC67","w_carb","veges","fruit","fish","cereals","ALCO","PHXA30","sport_hrs",
                                "CAFF","CARB","CHOL","DFIB","SODI","AFAT","VFAT","SFAT","PFAT","MFAT","PROT","SUCR","LACT","FRUC",
                                "STATINCODE31","ASPIRINCODE31","CHOLMDCODE31","outcome"
                                ]

		listOrdFeats1 = ["DTIC51","DTIC52","DTIC55","DTIC50","DTIC53","DTIC54","DTIC56","DTIC57","DTIC58",
                                "DTIC15","DTIC16","DTIC17","DTIC18","DTIC19","DTIC20","DTIC21","DTIC22","DTIC23","DTIC24","DTIC25",
                                "DTIC09","DTIC10","DTIC12","DTIC13","DTIC14","DTIC34","DTIC35","DTIC36","DTIC37","DTIC48","DTIC49"]
                listOrdFeats2 = ["DTIC66"]
		listOrdFeats3 = ["RPAC10","RPAC14","RPAC18","RPAC22"]
                listBinFeats = ["MSRC24A","MSRC24B","MSRC24C","MSRC24D","MSRC24E","MSRC25","MSRC28",
                                "DTIC67"]
                listGen = ["GENDER"]
                listRGrp = ["RACEGRP"]


    
	#Define the column that denotes the patient ID
	idColumn = "ID_C"

	## Define encodings of binary and ordinal variables
	ordDict1 = {'I':0,'H':.05,'G':.14286,'F':.42857,'E':.7857,'D':1,'C':2.5,'B':5,'A':7}#All other DTIA/B/C
	ordDict2 = {'D':0,'C':.25,'B':.625,'A':1}#DTIA/B/C 66
	ordDict3 = {'A':.5,'B':1.5,'C':2.5,'D':3.5,'E':5}
	binDict = {'N':0,'Y':1}#MSRA,DTIA67
	genDict={'M':1,'F':0}#GENDER
	rGrpDict = {'B':1,'W':0}#RACEGRP!

    	### Prune the patient ids and, for those remaining, define the outcome
	patData = establishPatVals(ids,exclYrs,excludeFiles,yearCols,visitYrs,outcomeFiles,outDataType,idColumn)

	## Check that output/ordered features match features being searched for
	checkOrdering(featureFiles,prevFeats,aggFeats,orderedFeats)

	### Now we want to iterate over the feature files and acquire, for each patient, the appropriate/necessary file
	print("Begin acquisition of patient data from the main set of files (featureFiles)...")
	for f in featureFiles.keys():
		print("Working... "+f)
		with open(f,'rU') as iFile:
			fReader = csv.reader(iFile,delimiter=',')
			rCounter = 0
			for row in fReader:
				rCounter+=1
				if rCounter == 1:
					# Get the indices of the necessary rows #
					indFeat = {}
					indSpc = {}
					for feat in featureFiles[f]:
						indFeat[feat] = row.index(feat)
						if feat in listOrdFeats1:
							indSpc[row.index(feat)] = ordDict1
						elif feat in listOrdFeats2:
							indSpc[row.index(feat)] = ordDict2
						elif feat in listOrdFeats3:
							indSpc[row.index(feat)] = ordDict3
						elif feat in listBinFeats:
							indSpc[row.index(feat)] = binDict
						elif feat in listGen:
							indSpc[row.index(feat)] = genDict
						elif feat in listRGrp:
							indSpc[row.index(feat)] = rGrpDict
						
					idInd = row.index(idColumn)
				else:
					if row[idInd] in patData.keys():
						for feat in indFeat.keys():
							if row[indFeat[feat]] == "" or row[indFeat[feat]] == " ":
								patData[row[idInd]][feat] = "NaN"
							elif indFeat[feat] in indSpc.keys():
								try:
                                                                	patData[row[idInd]][feat] = indSpc[indFeat[feat]][row[indFeat[feat]]]
								except:
									patData[row[idInd]][feat] = "NaN"
							else:
								patData[row[idInd]][feat] = row[indFeat[feat]] 

		iFile.close()
		for pat in patData.keys():
			for feat in indFeat.keys():
				if feat not in patData[pat].keys():
					patData[pat][feat] = "NaN"

	print("Finished main set of files (featureFiles)...")

	print("Begin acquisition of patient data from previous years files (prevFeats)...")
	for f in prevFeats:
		print("working... "+f)
		with open(f,'rU') as iFile:
                        fReader = csv.reader(iFile,delimiter=',')
                        rCounter = 0
                        for row in fReader:
                                rCounter+=1
                                if rCounter == 1:
                                        # Get the indices of the necessary rows #
                                        indFeat = {}
                                        for feat in prevFeats[f]:
                                                indFeat[feat] = row.index(feat)
						if feat in listOrdFeats1:
                                                        indSpc[row.index(feat)] = ordDict1
                                                elif feat in listOrdFeats2:
                                                        indSpc[row.index(feat)] = ordDict2
                                                elif feat in listOrdFeats3:
                                                        indSpc[row.index(feat)] = ordDict3
                                                elif feat in listBinFeats:
                                                        indSpc[row.index(feat)] = binDict
                                                elif feat in listGen:
                                                        indSpc[row.index(feat)] = genDict
                                                elif feat in listRGrp:
                                                        indSpc[row.index(feat)] = rGrpDict

                                        idInd = row.index(idColumn)
                                else:
                                        if row[idInd] in patData.keys():
                                                for feat in indFeat.keys():
							if row[indFeat[feat]] == "" or row[indFeat[feat]] == " ":
								patData[row[idInd]][feat] = "NaN"
							elif indFeat[feat] in indSpc.keys():
								patData[row[idInd]][feat] = indSpc[indFeat[feat]][row[indFeat[feat]]]
							else:
                                                        	patData[row[idInd]][feat] = row[indFeat[feat]]
		iFile.close()
		for pat in patData.keys():
                        for feat in indFeat.keys():
                                if feat not in patData[pat].keys():
                                        patData[pat][feat] = "NaN"


	print("Finished previous years file (prevFeats)...")

	print("Begin acquisition of patient data that requires aggregation (aggFeats)...")
	for f in aggFeats:
		print("Working... "+f)
		with open(f,'rU') as iFile:
                        fReader = csv.reader(iFile,delimiter=',')
                        rCounter = 0
                        for row in fReader:
                                rCounter+=1
                                if rCounter == 1:
                                        # Get the indices of the necessary rows #
					indFeat = {}
                                        for featD in aggFeats[f]:
						for featS in featD.keys():
							indFeat[featS] = []
							for feat in featD[featS]:
                                                		indFeat[featS].append(row.index(feat))
								if feat in listOrdFeats1:
                                                        		indSpc[row.index(feat)] = ordDict1
                                                		elif feat in listOrdFeats2:
                                                        		indSpc[row.index(feat)] = ordDict2
                                                		elif feat in listOrdFeats3:
                                                        		indSpc[row.index(feat)] = ordDict3
                                                		elif feat in listBinFeats:
                                                        		indSpc[row.index(feat)] = binDict
                                                		elif feat in listGen:
                                                        		indSpc[row.index(feat)] = genDict
                                                		elif feat in listRGrp:
                                                        		indSpc[row.index(feat)] = rGrpDict

                                        idInd = row.index(idColumn)
                                else:	
                                        if row[idInd] in patData.keys():
						for aF in indFeat.keys():
							agVal = 0
                                                	for feat in indFeat[aF]:
								if feat in indSpc.keys():
									try:	
										agVal += int(indSpc[feat][row[feat]])
									except:
										agVal +=0
								else:
									try:
										agVal += int(row[feat])
									except:
										agVal += 0
							patData[row[idInd]][aF] = str(agVal)

                iFile.close()
		for pat in patData.keys():
                        for feat in indFeat.keys():
                                if feat not in patData[pat].keys():
                                        patData[pat][feat] = "NaN"


	print("Finished aggregation files (aggFeats)...")
	print("Begin writing output...")
	varExclCriteria = len(orderedFeats) - 15 
	## Now write all collected patient data to output file
	orderedFeats.insert(0,idColumn)#Add the name of the patient identifier
	writeRes(args.outFile,orderedFeats)#Write the header
	orderedFeats.remove(idColumn)#Now remove the patient identifier
	additExcl =0
	for pat in patData.keys():
		newRow = [pat]
		missingCount = 0
		for feat in orderedFeats:
			if patData[pat][feat] == " ":
				patData[pat][feat] = "NaN"
			if patData[pat][feat] == "NaN":
				missingCount+=1
			newRow.append(patData[pat][feat])

		if missingCount >= varExclCriteria:
			additExcl+=1
			continue
		writeRes(args.outFile,newRow)

	print("Number of patient additionally excluded: "+str(additExcl))
	


def checkOrdering(featDict,prevFeatDict,aggFeatDict,orderList):
	'''
	This function checks the match between the features we are acquiring
	and the features tha we are ordering to ensure that none are missed
	'''

	print("Checking that ordered features matches the features being searched for...")
	fullFeats = []
	for f in featDict.keys():
		for fe in featDict[f]:
			fullFeats.append(fe)
	for f in prevFeatDict.keys():
		for fe in prevFeatDict[f]:
			fullFeats.append(fe)

	for f in aggFeatDict.keys():
		for aFe in aggFeatDict[f]:
			for aF in aFe.keys(): 
				fullFeats.append(aF)
	
	fullFeats.append("outcome")	
	for feat in orderList:
		try:
			fullFeats.remove(feat)
		except:
			print("Feature: "+feat+" defined in ordering not found in features searched for...")
	

	if len(fullFeats)>0:
		print("The following features being searched for were not included in the ordering and therefore the output: ")
		print(fullFeats)
	
	print("Done checking feature matches...")


    

if __name__=="__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--rootDir",type=str,
					help="Root directory of ARIC data. Should contain V1, V2, V3, comm_CHD "
					"directories")
	parser.add_argument("-i", "--inFile",type=str,
                                    	help="input file containing only patients and a header")
	parser.add_argument("-o", "--outFile", type=str,
                                    	help="output data file name")
	parser.add_argument("-v", "--visit", type=str,
					help="the visit number (e.g.,'V1')")
	parser.add_argument("-l","--logging", action='store_true',
                                    	help="print logging info (Default OFF)",
                                    	default=True)

	args = parser.parse_args()
        
	if args.logging:
		logging.basicConfig(stream=sys.stdout, level=logging.INFO)

	if not args.outFile or not args.inFile or not args.visit:
		parser.print_help()
		sys.exit()

	main(args)


