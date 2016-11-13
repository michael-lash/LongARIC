# LongARIC -- Deriving Longitudinal Datasets from ARIC Study DAta

_If using this code, please cite:_ **Michael T. Lash** and _W. Nick Street_, "Realistic risk-mitigating recommendations via inverse classification"

The paper can be found [here](http://michaeltlash.com/papers/risk_ic.pdf) and is currently under review.

### Generating initial visit data files (Step 1)  
Run ./deriveARICVisitData.py from the command line. You should be using Python 2.X. You can using the file /data/ids_only.csv as the input and specify your own output csv file.  **You _must_ use ARIC data acquired from BioLINCC for this to work**. The directory flag should be the resulting directory after downloading and unzipping the BioLINCC-acquired ARIC data.  

### Generating initial matlab files from csv data files (Step 2)  
From the commandline run matlab -r "makeInitMatFiles('visitFile','outputFile')" on each of the csv files generated using Step 1. You should specify your own output. Mine is visit1original.csv, visit2original.csv, and visit3original.csv  

**Note:** you will need to add the code "snippet" from data/addToVisit1Mat.txt to visit1original.mat, thus generating visit1over.mat. Instructions are provided within this file for performing this task   

### Estimating future visit missing features (Step 3)   
This task is meant to find a best estimator (regressor) of *known* continuous/semi-continuous features in Visit 2 using the data in Visit 1 to construct each model. This "best" regressor will then be used to estimate features that were collected during Visit 1, but were not during Visit 2.   

The code that goes through a handful of regression algorithms is "code/findMissingPredictor.m".  A couple of examples are provided in the file "code/callFMP.job".  The three examples reflect estimating "ALCO", "STATINCODE" and "HMTB01" (using "HTMA01" to build the regressors).  It can be noted here that STATINCODE is a binary feature, and we have attempted to estimate it using a regressor.  To deal with features that are binary "code/findMissingBinPred.m" has been included to estimate such features, with an example included in "code/callFMBP.job".

From conducting these expriments, the best regressor was found to be *Ridge Regression* and the best classifier was found to be *Logistic Regression*. While it may be naive to apply the best regressor and best classifier to estimate each of the corresponding missing values in V1 and V2 that is not the focus of these experiments and should be sufficient.

Therefore we use these classifiers to estimate and then order the features in V2 and V3.  The code to do this for V2 is in "code/estFeatV2.m" with an example in "code/callEstFeatV2.job" and the code for V3 is in "code/estFeatV3.m", with an example in "code/callEstFeatV3.job".  These generate the datasets "visit2EST.mat" and "visit3EST.mat", respectively.
