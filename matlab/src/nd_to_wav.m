function nd_to_wav(h)
% nd should contain an array with columns in this order:
% ns (note start), ne (note end), k (note value), v (velocity)

% Initialize audio track
fs = 44100;
ext_wav = 11; % pad wav file
wav = zeros(max([round(fs*max(h.nd(:,2)+ext_wav)),10*fs]),2);
oggpath = strrep(h.mlauvipath,'matlab','AE');
au = {};
r = .5;

% Sort nd array by note value. We do this to avoid having to load in wav
% files repeatedly.
h.nd = sortrows(h.nd,3);

% currnote also avoids unneccesarily loading notes
currnote = -1;
for i = 1:size(h.nd,1)
    note = h.nd(i,3);
    l = h.nd(i,2) - h.nd(i,1);
    if l <= .25; lidx = 1;
    elseif l < 1; lidx = 2;
    else; lidx = 3;
    end
    mag = ceil(h.nd(i,4)/16);
    % Load .ogg files if needed
    if note ~= currnote
        for j = 1:3
            fn = [num2str(note) '_'  num2str(mag) '_' num2str(j) '.ogg'];
            au{j} = audioread(fullfile(oggpath,fn));
        end
    end
    
    % make note
    tmpnote = au{lidx};
    if l < 9.5
        tmp1 = round(l*fs:(l+r)*fs);
        tmp2 = round((l+r)*fs+1:size(tmpnote,1));
        tmpnote(tmp1,:) = tmpnote(tmp1,:) .* repmat(linspace(1,0,numel(tmp1))',[1,2]);
        tmpnote(tmp2,:) = [];
    end
    
    % add note to master file
    wavidx = round(h.nd(i,1)*fs)+1:round(h.nd(i,1)*fs)+size(tmpnote,1);
    wav(wavidx,:) = wav(wavidx,:) + tmpnote;
    currnote = h.nd(i,3);
    if mod(i,10)
        h.St.String = ['Writing DynAud file... ' mat2str(round(i*100/size(h.nd,1))) ' % done'];
    end
    drawnow
end
% Crop wav file to ext-1
wav = wav(1:end-44100*(ext_wav-1),:);
output = rev(wav(1:441000,1),1,1)
filename = fullfile(h.savepath.String,h.filenameout.String);
audiowrite([filename '.wav'],wav,fs);