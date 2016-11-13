function makeVisitSVM(visitFile,d1Box,d1Sig,d2Box,d2Sig,d1CostParam,d2CostParam,outFile)


load(visitFile);

trainDSet1 = dSet1;
testDSet2 = dSet2;

testDSet1 = dSet1;
trainDSet2 = dSet2;

%%% Normalize trainDset1 and testDSet2 %%%%

max_train = nanmax(trainDSet1,[],1);
min_train = nanmin(trainDSet1,[],1);

nanTrain = isnan(trainDSet1);
nanMeanTrain = nanmean(trainDSet1);
[dum,rowIndex] = find(nanTrain);
trainDSet1(nanTrain) = nanMeanTrain(rowIndex);


nanTest = isnan(testDSet2);
nanMeanTest = nanmean(testDSet2);
[dum2,rowIndex2] = find(nanTest);
testDSet2(nanTest) = nanMeanTrain(rowIndex2);

[tee,c] = size(trainDSet1);
trainDSet1 = ((trainDSet1 - repmat(min_train,tee,1))./(repmat(max_train-min_train,tee,1)));

[r,c] = size(testDSet2);
testDSet2 = ((testDSet2-repmat(min_train,r,1))./(repmat(max_train-min_train,r,1)));

trainDSet1(isnan(trainDSet1))=0;
testDSet2(isnan(testDSet2))=0;

%%%% End norm trainDSet1 testDSet2 %%%%%%


%%%% Normalize trainDSet2 and testDSet1 %%%%%
max_train = nanmax(trainDSet2,[],1);
min_train = nanmin(trainDSet2,[],1);

nanTrain = isnan(trainDSet2);
nanMeanTrain = nanmean(trainDSet2);
[dum,rowIndex] = find(nanTrain);
trainDSet2(nanTrain) = nanMeanTrain(rowIndex);


nanTest = isnan(testDSet1);
nanMeanTest = nanmean(testDSet1);
[dum2,rowIndex2] = find(nanTest);
testDSet1(nanTest) = nanMeanTrain(rowIndex2);

[tee,c] = size(trainDSet2);
trainDSet2 = ((trainDSet2 - repmat(min_train,tee,1))./(repmat(max_train-min_train,tee,1)));

[r,c] = size(testDSet1);
testDSet1 = ((testDSet1-repmat(min_train,r,1))./(repmat(max_train-min_train,r,1)));

trainDSet2(isnan(trainDSet2))=0;
testDSet1(isnan(testDSet1))=0;

clearvars tee c r dum2 rowIndex2 nanTest nanMeanTest nanTrain nanMeanTrain dum rowIndex max_train min_train

%%%% End norm trainDSet2 testDSet1 %%%%%

%%% Build SVM Models based on train datasets %%%

d1SvmStruct = fitcsvm(trainDSet1, dSet1Label, 'KernelFunction', 'rbf', 'BoxConstraint', d1Box, 'KernelScale', d1Sig, 'Cost', [0,1;d1CostParam,0]);

d2SvmStruct = fitcsvm(trainDSet2, dSet2Label, 'KernelFunction', 'rbf', 'BoxConstraint', d2Box, 'KernelScale', d2Sig, 'Cost', [0,1;d2CostParam,0]);

d1AlphaVals = d1SvmStruct.Alpha;
d1Sigma = d1Sig;
d1SupportVectorLabels = dSet1Label(d1SvmStruct.IsSupportVector);
d1SupportVectors = trainDSet1(d1SvmStruct.IsSupportVector,:);
d1BiasTerm = d1SvmStruct.Bias;

d2AlphaVals = d2SvmStruct.Alpha;
d2Sigma = d2Sig;
d2SupportVectorLabels = dSet2Label(d2SvmStruct.IsSupportVector);
d2SupportVectors = trainDSet2(d2SvmStruct.IsSupportVector);
d2BiasTerm = d2SvmStruct.Bias;

clearvars d1SvmStruct d2SvmStruct;

[m n] = size(trainDSet1);

d1KFoldAlpha = containers.Map('KeyType', 'int32', 'ValueType', 'any');
d1KFoldInd = crossvalind('Kfold', m, 10);
d1KFoldLabel = containers.Map('KeyType', 'int32', 'ValueType', 'any');
d1KFoldSV = containers.Map('KeyType', 'int32', 'ValueType', 'any');
d1KFoldSigma = containers.Map('KeyType', 'int32', 'ValueType', 'any');
d1KFoldBias = containers.Map('KeyType', 'int32', 'ValueType', 'any');


for i =1:10
    test = (d1KFoldInd==i); train = ~test;
    dTrain = trainDSet1(train,:);
    dTrainLabel = dSet1Label(train);
    svmStruct = fitcsvm(dTrain, dSet1Label(train), 'KernelFunction', 'rbf', 'BoxConstraint', d1Box, 'KernelScale', d1Sig, 'Cost', [0,1;d1CostParam,0]);
    d1KFoldAlpha(i) = svmStruct.Alpha;
    d1KFoldLabel(i) = dTrainLabel(svmStruct.IsSupportVector);
    d1KFoldSV(i) = dTrain(svmStruct.IsSupportVector,:);
    d1KFoldSigma(i) = d1Sig;
    d1KFoldBias(i) = svmStruct.Bias;

end

[m n] = size(trainDSet2);

d2KFoldAlpha = containers.Map('KeyType', 'int32', 'ValueType', 'any');
d2KFoldInd = crossvalind('Kfold', m, 10);
d2KFoldLabel = containers.Map('KeyType', 'int32', 'ValueType', 'any');
d2KFoldSV = containers.Map('KeyType', 'int32', 'ValueType', 'any');
d2KFoldSigma = containers.Map('KeyType', 'int32', 'ValueType', 'any');
d2KFoldBias = containers.Map('KeyType', 'int32', 'ValueType', 'any');

for i =1:10

    test = (d2KFoldInd==i); train = ~test;
    dTrain = trainDSet2(train,:);
    dTrainLabel = dSet2Label(train);
    svmStruct = fitcsvm(dTrain, dSet2Label(train), 'KernelFunction', 'rbf', 'BoxConstraint', d2Box, 'KernelScale', d2Sig, 'Cost', [0,1;d2CostParam,0]);
    d2KFoldAlpha(i) = svmStruct.Alpha;
    d2KFoldLabel(i) = dTrainLabel(svmStruct.IsSupportVector);
    d2KFoldSV(i) = dTrain(svmStruct.IsSupportVector,:);
    d2KFoldSigma(i) = d2Sig;
    d2KFoldBias(i) = svmStruct.Bias;

end

clearvars m n test train i dTrain dTrainLabel svmStruct;

%%%% End SVM model construction %%%%%

%%%% Define unchange, indirectly change and changeable indices, changeable costs and direction of change %%%%


unchangeableIndex = [1:26];
indirectlyIndex = [27:91];
changeableIndex = [92:122];
binaryChangeable = [];
ordinalChangeable = [];
costChange = [10000 3 4 5 8 10000 6 6 6 10000 10000 9 9 10 10000 10000 6 7 7 5 6 5 7 3 10000 4 10000 4 2 2 7];
increaseCost = [-1 1 1 1 -1 1 -1 1 1 -1 -1 -1 -1 1 -1 -1 -1 1 -1 -1 1 -1 1 1 1 -1 1 -1 1 1 1];

%% Alcohol and sport hours cut off depends %%%
directionDependsCutoff = [.25 .45];
directionDependsInd = [12 14];

%% Whether or not we want to recommend an aspirin regement depends on the current level of risk %%
riskDependsInd = [30];
riskDependsCutoff = [.1];


%%%% Save vars in a .mat structure file %%%%

save(outFile);


