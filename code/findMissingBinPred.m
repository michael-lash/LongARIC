function [mseLinear] = findPredictor(matDataModel,matDataEst,varPred1,varPred2,saveDirectory,libsvmMatDir)


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

%Logistic Regression
which fitglm -all
model = glmfit(data1,y1,'binomial','link','logit');
inter = model(1);
newY = (data2*model(2:end)+inter);
accuracy = sum(y2 == newY)/numel(y2);
[X,Y,T,AUC] = perfcurve(y2,newY, 1);

display(AUC);
save(strcat(saveDirectory,'auc_logistic.txt'), 'AUC','-ascii');


%%%% Decision Tree %%%%
model = fitctree(data1,y1);
[label,score] = predict(model, data2);
accuracy = sum(y2==label)/numel(y2);
[X,Y,T,AUC] = perfcurve(y2,label, 1);
display(AUC);
save(strcat(saveDirectory,'auc_tree.txt'), 'AUC', '-ascii');


addpath libsvmMatDir;


%%%% SVM Classification -- Linear%%%%

aucLinSVM = []; %holder for mse of svm models (avg cross valid)
cost = [.001,.01,.1,1,2,5,10,20,50,100,200,500];
[c,v] = size(cost);
for f=1:v
    curCost = cost(f);
    svmString = strcat({'-q -s 0 -t 0 -c '}, num2str(curCost));
    model = svmtrain(y1,data1,svmString);
    [newY,acc,prob] = svmpredict(y2,data2,model);
    [X,Y,T,AUC] = perfcurve(y2,newY, 1);
    aucLinSVM = [aucLinSVM AUC];
end
display(aucLinSVM);
save(strcat(saveDirectory,'auc_linear_svm.txt'), 'aucLinSVM', '-ascii');


%%%% SVM Classification -- RBF %%%%

cost = [.001,.01,.1,1,2,5,10,20,50,100,200,500];
rbfVals = [.001,.01,.1,1,2,5,10,20,50,100,200,500];
[c,v] = size(cost);
[t,q] = size(rbfVals);
aucRBFSVM = zeros(v,q);
for f=1:v
    curCost = cost(f);
    for s=1:q
        curRBF = rbfVals(s);
        svmString = strcat({'-q -s 0 -t 2 - c '},num2str(curCost),{' -g '},num2str(curRBF));
        model = svmtrain(y1,data1,svmString);
        [newY,acc,prob] = svmpredict(y2,data2,model);
        [X,Y,T,AUC] = perfcurve(y2,newY, 1);
        aucRBFSVM(f,s) = AUC;
    end
end
display(aucRBFSVM);
save(strcat(saveDirectory,'auc_rbf_svm.txt'), 'aucRBFSVM', '-ascii');

%%%%% kNN Regression %%%%%%%
mdl = fitcknn(data1,y1);
newY = predict(mdl,data2);
[X,Y,T,AUC] = perfcurv(y2,newY,1);
display(AUC);
save(strcat(saveDirectory,'auc_knn.txt'), 'AUC', '-ascii');


%%%%% Simple carryover imputation %%%%%%
[C ia ib] = intersect(id1,id2);
origVals1 = y1(ia);
origVals2 = y2(ib);
accuracy = sum(origVals2 == origVals1)/numel(origVals2);
[X,Y,T,AUC] = perfcurve(origVals2,origVals1, 1);
display(AUC);
save(strcat(saveDirectory,'auc_carryover.txt'),'AUC','-ascii');



exit;
