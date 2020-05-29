function [Mfinal,nd] = H_to_nd(H,fr,thr,keys)
MIDImat = []; %MIDImat is for MIDI files
nd = []; % ND is for WAV files
us_f = 100;
for i = 1:size(H,1)
    Hr(i,:) = interp(H(i,:),us_f);
end

for i = 1:size(H,1)
    TC = Hr(i,:);
    TC(TC <= thr) = NaN;
    if sum(isnan(TC)) ~= numel(TC)
        notechange = diff(isnan(TC));
        notestart = find(notechange == -1);
        noteend = find(notechange == 1);
        if ~isnan(TC(1))
            notestart = [1 notestart];
        end
        if ~isnan(TC(end))
            noteend = [noteend numel(TC)];
        end
        notemag = []; notekey = [];
        for j = 1:numel(notestart)
            tmp = Hr(i,notestart(j):noteend(j));
            tmp(tmp < thr) = 0;
            notemag(j) = max(tmp); 
            notekey(j) = keys(i);
        end
        MIDItmp = [notekey;notemag;notestart;noteend];
        MIDImat = [MIDImat MIDItmp];
        nd = [nd;[notestart'/(us_f*fr) noteend'/(us_f*fr) notekey' round(notemag*127)']];
        tmp = zeros(size(TC)); tmp(tmp == 0) = NaN;
    end
end

MIDImat(2,:) = round(min(MIDImat(2,:)*127/max(MIDImat(2,:)),127));
Mfinal = zeros(size(MIDImat,2),6);
Mfinal(:,3) = MIDImat(1,:)';
Mfinal(:,4) = MIDImat(2,:)';
Mfinal(:,5) = MIDImat(3,:)/(fr*us_f)';
Mfinal(:,6) = MIDImat(4,:)/(fr*us_f)';
