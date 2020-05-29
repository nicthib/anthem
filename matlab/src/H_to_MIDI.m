function [Mfinal] = H_to_MIDI(H,fr,thr,keys)
MIDImat = [];
t1 = 0:size(H,2)-1;
us_f = 100; % Upsampling factor
t2 = linspace(0,size(H,2),size(H,2)*us_f);
for i = 1:size(H,1)
    Hr(i,:) = interp1(t1,H(i,:),t2);
end

for i = 1:size(H,1)
    TC = Hr(i,:);
    TC(TC <= thr) = NaN;
    if sum(isnan(TC)) ~= numel(TC)
        notechange = diff(isnan(TC));
        notestart = find(notechange == -1);
        noteend = find(notechange == 1);
        if isnan(TC(1)) == 0
            notestart = [1 notestart];
        end
        if isnan(TC(end)) == 0
            noteend = [noteend numel(TC)];
        end
        
        notemag = []; notekey = [];
        for j = 1:numel(notestart)
            tmp = Hr(i,notestart(j):noteend(j));
            tmp(tmp < thr) = 0;
            notemag(j) = max(tmp); notekey(j) = keys(i);
        end
        MIDItmp = [notekey;notemag;notestart;noteend];
        MIDImat = [MIDImat MIDItmp];
        tmp = zeros(size(TC)); tmp(tmp == 0) = NaN;
    end
end

MIDImat(2,:) = round(min(MIDImat(2,:)*127/max(MIDImat(2,:)),127));
Mfinal = zeros(size(MIDImat,2),6);
Mfinal(:,3) = MIDImat(1,:)';
Mfinal(:,4) = MIDImat(2,:)';
Mfinal(:,5) = MIDImat(3,:)/(fr*us_f)';
Mfinal(:,6) = MIDImat(4,:)/(fr*us_f)';
