function keysout = makekeys(scale,scaletype,nnotes,addoct)
noteref = csvread('NoteIDX.csv');
noteIDX = noteref(scaletype,:);
noteIDX(isnan(noteIDX)) = [];
numoct = ceil(nnotes/numel(noteIDX));
keys = noteIDX+scale;
keysout = [];
for i = 1:numoct
    keysout = [keysout keys+(i-1)*12];
end
keysout = keysout(1:nnotes);
keysout = keysout+addoct*12;
keysout = keysout - 1; % Matlab doesn't index starting at 0. This fixes that issue
