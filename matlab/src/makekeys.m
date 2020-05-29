function [keysout,out] = makekeys(scale,scaletype,nnotes,addoct)
noteref = csvread('NoteIDX.csv');
noteIDX = noteref(scaletype,:)-1;
noteIDX(isnan(noteIDX)) = [];
numoct = ceil(nnotes/numel(noteIDX));
keys = noteIDX+scale-1;
keysout = [];
for i = 1:numoct
    keysout = [keysout keys+(i-1)*12];
end
keysout = keysout+addoct*12+1;
% if max(keysout) > 52 % current note range, from C0 to D#4.
%     out = 0; 
%     return
% else
%     out = 1; 
% end
