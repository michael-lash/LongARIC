function estFeatV2(matDataModel,matDataEst,outFile)


%%%% These will be used to add the bin/cont feats to the v2 data structure %%%%%
v1BinFeats = [18,19,20,21,69];
v1ContFeats = [1,26,28,34,35,37,38,39,40,42,43,44,48,49,50,51,52,53,54,55,56,57,58,59,60,63,64,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85];
v2FeatName = {'ESTmsra08e','ESTmsra08f','ESTmsra08g','ESTmsra08h','ESTtglefh01','ESTchma16','ESTcigtyr01','ESThdl01','ESTanta07a','ESTanta07b','ESThmta03', ...
'ESTlipa06','ESTlipa07','ESTlipa08','ESTfev1fvc1','ESTpfta26','ESTpfta24','ESThmta05','ESThmta06','ESThmta07','ESThmta08','ESThmta09','ESThmta10', ...
'ESThema05','ESThema07','ESThema09','ESThema11','ESThema13','ESThema15','ESThema17','ESTmntrcp01','ESTmnsscp01','ESTanta07c','ESTanta06b',...
'ESTglucos01','ESTglusiu01','ESTanta05b','ESTchma15','ESTchma14','ESTchma13','ESTchma12','ESTchma11','ESTchma10','ESTchma08','ESTchma06','ESTchma05', ...
'ESTchma09'};

%v2FeatName = {'ESTchma16','ESTmsra08e','ESTmsra08f','ESTmsra08g','ESTmsra08h','ESTcigtyr01','ESThdl01','ESTanta07a','ESTanta07b','ESThmta03', ...
%'ESTlipa06','ESTlipa07','ESTlipa08','ESTfev1fvc1','ESTpfta26','ESTpfta24','ESThmta05','ESThmta06','ESThmta07','ESThmta08','ESThmta09','ESThmta10', ...
%'ESThema05','ESThema07','ESThema09','ESThema11','ESThema13','ESThema15','ESThema17','ESTmntrcp01','ESTmnsscp01','ESTtglefh01','ESTanta07c','ESTanta06b',...
%'ESTglucos01','ESTglusiu01','ESTanta05b','ESTchma15','ESTchma14','ESTchma13','ESTchma12','ESTchma11','ESTchma10','ESTchma08','ESTchma06','ESTchma05', ...
%'ESTchma09'};

v2Ind = [1,18,19,20,21,26,28,34,35,37,38,39,40,42,43,44,48,49,50,51,52,53,54,55,56,57,58,59,60,63,64,69,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85]; % a=[1:num-1], b=[num:end], horzcat(a,estFeatColumn,b); --- for loop
estMatConcord = [6,1,2,3,4,7:32,5,33:length(v2Ind)]; %% houses the concordance of feats
reOrderIndsInit = [45];
reOrderIndsNew = [46];

size(v2FeatName)
size(v2Ind)

totEstFeats = length(v2Ind);

d1= load(matDataModel);
d2 = load(matDataEst);

[a b] = size(d2.dSet1);
[c d] = size(d2.dSet2);
keepIndVals = [1:b];
keepIndVals(d1.v3RemVals) = [];
estValMat1 = zeros(a,totEstFeats); % Holds the missing values
estValMat2 = zeros(c,totEstFeats);



id1 = vertcat(d1.dSet1IDs,d1.dSet2IDs);

[gg hh] = size(v1BinFeats);
%%% Begin iterating for bin feats %%%%
for i =1:hh
varPred1 = v1BinFeats(i);
%% Setup the training data (V1 data) %%
data1 = vertcat(d1.dSet1,d1.dSet2);
remInd = ~isnan(data1(:,varPred1));
id1x = id1(remInd);
data1 = data1(remInd,:);%Remove the data points that are missing the dep feature
y1 = data1(:,varPred1);
remOL = d1.v3OverlapVals;
data1 = data1(:,remOL);


%data2 = vertcat(d2.dSet1,d2.dSet2);
%remInd = ~isnan(data2(:,varPred2));
%id2 = id2(remInd);
%data2 = data2(remInd,:);
%[mm,nn] = size(data2);

%% Setup the testing data (V2 data) %%
%indVals2 = [1:nn];
%indVals2 = indVals2(indVals2~=varPred2);
%y2 = data2(:,varPred2);
%data2 = data2(:,indVals2);

%%%%% Fill in missing values %%%%%

%% Will use these for normalization %%
max_train = nanmax(data1,[],1);
min_train = nanmin(data1,[],1);

nanTrain = isnan(data1);
nanMeanTrain = nanmean(data1);
[dum,rowIndex] = find(nanTrain);
data1(nanTrain) = nanMeanTrain(rowIndex);
data21 = d2.dSet1;
data22 = d2.dSet2;

data21 = data21(:,keepIndVals);
data22 = data22(:,keepIndVals);

nanTest = isnan(data21);
[dum2,rowIndex2] = find(nanTest);
data21(nanTest) = nanMeanTrain(rowIndex2);

nanTest = isnan(data22);
[dum2,rowIndex2] = find(nanTest);
data22(nanTest) = nanMeanTrain(rowIndex2);

%%%% Normalize training and testing data %%%%
[tee,c] = size(data1);
data1 = ((data1 - repmat(min_train,tee,1))./(repmat(max_train-min_train,tee,1)));

[r,c] = size(data21);
data21 = ((data21-repmat(min_train,r,1))./(repmat(max_train-min_train,r,1)));

[r,c] = size(data22);
data22 = ((data22-repmat(min_train,r,1))./(repmat(max_train-min_train,r,1)));

data1(isnan(data1))=0;
data21(isnan(data21))=0;
data22(isnan(data22))=0;

%%%%% END DATA PRE-PROCESSING %%%%%

%%%% Use best binary model -- Logistic Regression %%%%%
model = glmfit(data1,y1,'binomial','link','logit');
inter = model(1);
newY1 = (data21*model(2:end)+inter);
newY2 = (data22*model(2:end)+inter);
estValMat1(:,i) = newY1;
estValMat2(:,i) = newY2;
end

addVal = hh; %% usee this to insert into the zeroes matrix hold the est values
%%% Begin iteratng for cont feats %%%

[gg hh] = size(v1ContFeats);
for i =1:hh
varPred1 = v1ContFeats(i);
%% Setup the training data (V1 data) %%
data1 = vertcat(d1.dSet1,d1.dSet2);
remInd = ~isnan(data1(:,varPred1));
id1x = id1(remInd);
data1 = data1(remInd,:);%Remove the data points that are missing the dep feature
y1 = data1(:,varPred1);
remOL = d1.v3OverlapVals;
data1 = data1(:,remOL);

%data2 = vertcat(d2.dSet1,d2.dSet2);
%remInd = ~isnan(data2(:,varPred2));
%id2 = id2(remInd);
%data2 = data2(remInd,:);
%[mm,nn] = size(data2);

%% Setup the testing data (V2 data) %%
%indVals2 = [1:nn];
%indVals2 = indVals2(indVals2~=varPred2);
%y2 = data2(:,varPred2);
%data2 = data2(:,indVals2);

%%%%% Fill in missing values %%%%%

%% Will use these for normalization %%
max_train = nanmax(data1,[],1);
min_train = nanmin(data1,[],1);

nanTrain = isnan(data1);
nanMeanTrain = nanmean(data1);
[dum,rowIndex] = find(nanTrain);
data1(nanTrain) = nanMeanTrain(rowIndex);
data21 = d2.dSet1;
data22 = d2.dSet2;
data21 = data21(:,keepIndVals);
data22 = data22(:,keepIndVals);
nanTest = isnan(data21);
[dum2,rowIndex2] = find(nanTest);
data21(nanTest) = nanMeanTrain(rowIndex2);

nanTest = isnan(data22);
[dum2,rowIndex2] = find(nanTest);
data22(nanTest) = nanMeanTrain(rowIndex2);

%%%% Normalize training and testing data %%%%
[tee,c] = size(data1);
data1 = ((data1 - repmat(min_train,tee,1))./(repmat(max_train-min_train,tee,1)));

[r,c] = size(data21);
data21 = ((data21-repmat(min_train,r,1))./(repmat(max_train-min_train,r,1)));

[r,c] = size(data22);
data22 = ((data22-repmat(min_train,r,1))./(repmat(max_train-min_train,r,1)));

data1(isnan(data1))=0;
data21(isnan(data21))=0;
data22(isnan(data22))=0;

%%%%% END DATA PRE-PROCESSING %%%%%

%%% Use best continuous model -- ridge reg w/ lambda=.01 %%%%%
model = ridge(y1,data1,.01,0);
inter = model(1);
newY1 = (data21*model(2:end)+inter);
newY2 = (data22*model(2:end)+inter);
estValMat1(:,i+addVal) = newY1;
estValMat2(:,i+addVal) = newY2;

end

%%%% End Feat Estimation %%%%

%%%% Begin adding features to matrix %%%%
dSet1 = d2.dSet1;
dSet2 = d2.dSet2;
dSet1 = dSet1(:,keepIndVals);
dSet2 = dSet2(:,keepIndVals);

header = d2.header(keepIndVals);
dSet1Label = d2.dSet1Label;
dSet2Label = d2.dSet2Label;
dSet1IDs = d2.dSet1IDs;
dSet2IDs = d2.dSet2IDs;

for k=1:length(v2Ind)
    conVal = estMatConcord(k);
    actInd = v2Ind(k);

    if actInd == 1
        dSet1 = horzcat(estValMat1(:,conVal),dSet1(:,1:end));
        dSet2 = horzcat(estValMat2(:,conVal),dSet2(:,1:end));
        header = [v2FeatName(conVal),header];
    else
        dSet1 = horzcat(dSet1(:,1:actInd-1),estValMat1(:,conVal),dSet1(:,actInd:end));
        dSet2 = horzcat(dSet2(:,1:actInd-1),estValMat2(:,conVal),dSet2(:,actInd:end));
        header = [header(1:actInd-1),v2FeatName(conVal),header(actInd:end)];
    end

end

header


for k=1:length(reOrderIndsInit)
    orVal = reOrderIndsInit(k);
    nVal = reOrderIndsNew(k);
    name = header(orVal);
    header = [header(1:orVal-1),header(orVal+1:end)];
    header = [header(1:nVal-1),name,header(nVal:end)];

    vect = dSet1(:,orVal);
    dSet1 = horzcat(dSet1(:,1:orVal-1),dSet1(:,orVal+1:end));
    dSet1 = horzcat(dSet1(:,1:nVal-1),vect,dSet1(:,nVal:end));

    vect = dSet2(:,orVal);
    dSet2 = horzcat(dSet2(:,1:orVal-1),dSet2(:,orVal+1:end));
    dSet2 = horzcat(dSet2(:,1:nVal-1),vect,dSet2(:,nVal:end));

end

header

save(outFile,'dSet1','dSet2','header','dSet1Label','dSet2Label','dSet1IDs','dSet2IDs');

