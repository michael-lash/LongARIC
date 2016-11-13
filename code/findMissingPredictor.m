function [mseLinear] = findPredictor(matDataModel,matDataEst,varPred1,varPred2,saveDirectory,libsvmMatDir)

addpath libsvmMatDir;

d1= load(matDataModel);
d2 = load(matDataEst);


id1 = vertcat(d1.dSet1IDs,d1.dSet2IDs);
id2 = vertcat(d2.dSet1IDs,d2.dSet2IDs);

%% Setup the training data (V1 data) %%
data1 = vertcat(d1.dSet1,d1.dSet2);
remInd = ~isnan(data1(:,varPred1));
id1 = id1(remInd);
data1 = data1(remInd,:);%Remove the data points that are missing the dep feature
y1 = data1(:,varPred1);
remOL = d1.v2OverlapVals(d1.v2OverlapVals~=varPred1);
data1 = data1(:,remOL);
data2 = vertcat(d2.dSet1,d2.dSet2);
remInd = ~isnan(data2(:,varPred2));
id2 = id2(remInd);
data2 = data2(remInd,:);
[mm,nn] = size(data2);

%% Setup the testing data (V2 data) %%
indVals2 = [1:nn];
indVals2 = indVals2(indVals2~=varPred2);
y2 = data2(:,varPred2);
data2 = data2(:,indVals2);

%%%%% Fill in missing values %%%%%

%% Will use these for normalization %%
max_train = nanmax(data1,[],1);
min_train = nanmin(data1,[],1);

nanTrain = isnan(data1);
nanMeanTrain = nanmean(data1);
[dum,rowIndex] = find(nanTrain);
data1(nanTrain) = nanMeanTrain(rowIndex);

nanTest = isnan(data2);
[dum2,rowIndex2] = find(nanTest);
data2(nanTest) = nanMeanTrain(rowIndex2);

%%%% Normalize training and testing data %%%%
[tee,c] = size(data1);
data1 = ((data1 - repmat(min_train,tee,1))./(repmat(max_train-min_train,tee,1)));

[r,c] = size(data2);
data2 = ((data2-repmat(min_train,r,1))./(repmat(max_train-min_train,r,1)));

data1(isnan(data1))=0;
data2(isnan(data2))=0;

%%%%% END DATA PRE-PROCESSING %%%%%

%first do fitglm (linear model) --- Linear Model
modelType = {'linear'};
[c,v] = size(modelType);
for f = 1:v
    curMod = char(modelType(f))
    model = fitglm(data1,y1,curMod);
    newY = feval(model,data2);
    notNaN = ~isnan(newY);
    mse = mean((y2(notNaN)-newY(notNaN)).^2);
end

display(mse);
save(strcat(saveDirectory,'mse_glm.txt'), 'mse','-ascii');




%%%% Ridge Regression %%%%

ridgeVals = [.00000001,.0000001,.000001,.00001,.0001,.001,.01];
[c,v] = size(ridgeVals);
mseLinear = [];
for f= 1:v
    ridParam = ridgeVals(f);
    model = ridge(y1,data1,ridParam,0);
    inter = model(1);
    newY = (data2*model(2:end)+inter);
    notInf = ~isinf(newY);
    mse = mean((y2(notInf)-newY(notInf)).^2);
    mseLinear = [mseLinear mse];
end
display(mseLinear);
save(strcat(saveDirectory,'mse_ridge.txt'), 'mseLinear', '-ascii');



%%%% Regression Tree %%%%
model = fitrtree(data1,y1);
newY = predict(model, data2);
mse = mean((y2-newY).^2);
display(mse);
save(strcat(saveDirectory,'mse_tree.txt'), 'mse', '-ascii');



%%%% SVM Regression -- Linear%%%%

mseLinSVM = []; %holder for mse of svm models (avg cross valid)
cost = [.001,.01,.1,1,2,5,10,20,50,100,200,500];
[c,v] = size(cost);
for f=1:v
    curCost = cost(f);
    svmString = strcat({'-q -s 3 -t 0 -c '}, num2str(curCost));
    svmString
    model = svmtrain(y1,data1,svmString);
    [newY,acc,prob] = svmpredict(y2,data2,model);
    mse = mean((y2-newY).^2);
    mseLinSVM = [mseLinSVM mse];
end
display(mseLinSVM);
save(strcat(saveDirectory,'mse_linear_svm.txt'), 'mseLinSVM', '-ascii');


%%%% SVM Regression -- RBF %%%%

cost = [.001,.01,.1,1,2,5,10,20,50,100,200,500];
rbfVals = [.001,.01,.1,1,2,5,10,20,50,100,200,500];
[c,v] = size(cost);
[t,q] = size(rbfVals);
mseRBFSVM = zeros(v,q);
for f=1:v
    curCost = cost(f);
    for s=1:q
        curRBF = rbfVals(s);
        svmString = strcat({'-q -s 3 -t 2 - c '},num2str(curCost),{' -g '},num2str(curRBF));
        model = svmtrain(y1,data1,svmString);
        [newY,acc,prob] = svmpredict(y2,data2,model);
        mse = mean((y2-newY).^2);
        mseRBFSVM(f,s) = mse;
    end
end
display(mseRBFSVM);
save(strcat(saveDirectory,'mse_rbf_svm.txt'), 'mseRBFSVM', '-ascii');

%%%%% kNN Regression %%%%%%%
mdl = fitcknn(data1,y1);
newY = predict(mdl,data2);
mse = mean((y2-newY).^2);
display(mse);
save(strcat(saveDirectory,'mse_knn.txt'), 'mse', '-ascii');


%%%%% Simple carryover imputation %%%%%%
[C ia ib] = intersect(id1,id2);
origVals1 = y1(ia);
origVals2 = y2(ib);
mse = mean((origVals2-origVals1).^2);
display(mse);
save(strcat(saveDirectory,'mse_carryover.txt'),'mse','-ascii');



exit;
