function makeInitMatFiles(visitFile,outFile)

dat = importdata(visitFile)
header = dat.textdata(1,2:end-1);
patID = dat.textdata(2:end,1);
outcome = dat.data(:,end);
patDat = dat.data(:,1:end-1);

%% We want to stratify data to ensure that there are equal pos and neg labels %%
posInd = (outcome==1);
negInd = (outcome==0);
posDat = patDat(posInd,:);
posLabel = outcome(posInd);
posID = patID(posInd);
negDat = patDat(negInd,:);
negLabel = outcome(negInd);
negID = patID(negInd);
%%%%%

%% First randomly partition negative into 2 groups %%
[m n] = size(negDat);
valInd = crossvalind('Kfold', m, 2);
d1Ind = (valInd==1); d2Ind = ~d1Ind;
dSet1Neg = negDat(d1Ind,:);
dSet1LabelNeg = negLabel(d1Ind);
dSet1IDNeg = negID(d1Ind);

dSet2Neg = negDat(d2Ind,:);
dSet2LabelNeg = negLabel(d2Ind);
dSet2IDNeg = negID(d2Ind);

%% Next randoly partition positive into 2 groups %%
[m n] = size(posDat);
valInd = crossvalind('Kfold', m, 2);
d1Ind = (valInd==1); d2Ind = ~d1Ind;
dSet1Pos = posDat(d1Ind,:);
dSet1LabelPos = posLabel(d1Ind);
dSet1IDPos = posID(d1Ind);

dSet2Pos = posDat(d2Ind,:);
dSet2LabelPos = posLabel(d2Ind);
dSet2IDPos = posID(d2Ind);

%% Now concatenate pos and neg elems to form all component of dSet1 and dSet2 %%
dSet1 = vertcat(dSet1Neg,dSet1Pos);
dSet1Label = vertcat(dSet1LabelNeg,dSet1LabelPos);
dSet1IDs = vertcat(dSet1IDNeg,dSet1IDPos);

dSet2 = vertcat(dSet2Neg,dSet2Pos);
dSet2Label = vertcat(dSet2LabelNeg,dSet2LabelPos);
dSet2IDs = vertcat(dSet2IDNeg,dSet2IDPos);


save(outFile,'header','dSet1','dSet1Label','dSet1IDs','dSet2','dSet2Label','dSet2IDs');

end
