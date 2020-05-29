function nd_to_wav(filename,nd,h)
% nd should contain an array with columns in this order:
% ns (note start), ne (note end), k (note value), v (velocity)

r = .25;
nd(:,3) = nd(:,3);

% Initialize audio track
fs = 44100;
wav = zeros(max([round(fs*max(nd(:,2)+11)),10*fs]),2);

% Sort nd array by note value. We do this to avoid having to load in wav
% files repeatedly.
nd = sortrows(nd,3);

notes = unique(nd(:,3));

currnote = -1;
for i = 1:size(nd,1)
    % Check if we need to load a new note
    if currnote ~= nd(i,3)
        [note,ps] = notestr(nd(i,3)+1); % add 1 since C starts at 1 for these files. (C starts at 0 for MIDI)
        raw = loadnote(note,ps,1);
    end
    l = nd(i,2) - nd(i,1);
    if l <= .08
        lidx = 1;
    elseif l > .08 && l <= .5
        lidx = 2;
    elseif l > .5  && l <= 1
        lidx = 3;
    elseif l > 1   && l <= 2
        lidx = 4;
    elseif l > 2
        if l > 10
            l = 10;
        end
        lidx = 5;
    end
    
    smap = [repmat([1 0 0],32,1);[linspace(1,0,32)' linspace(0,1,32)' zeros(32,1)]...
        ;[zeros(64,1) linspace(1,0,64)' linspace(0,1,64)']]; % strength map
    v_c = linspace(0,1,128)';
    smap = smap .* v_c;
    tmpnote = raw{lidx,1}*smap(nd(i,4),1)+raw{lidx,2}*smap(nd(i,4),2)+raw{lidx,3}*smap(nd(i,4),3);
    
    % truncate note to length + release (only for longer notes)
    if lidx > 2
        tmpnote = tmpnote(1:round((l+r)*fs),:);
        env = ones(round((l+r)*fs),1);
        ridx = numel(env)-round(r*fs):numel(env);
        env(ridx) = linspace(1,0,numel(ridx));
        tmpnote = tmpnote .* env;
    end
    
    % Add 100 samples ramp on and off to prevent clipping
    tmpnote(1:100,:) = tmpnote(1:100,:) .* repmat(linspace(0,1,100)',[1 2]);
    tmpnote(end-99:end,:) = tmpnote(end-99:end,:) .* repmat(linspace(1,0,100)',[1 2]);
    
    % add note to master file
    wavidx = round(nd(i,1)*fs)+1:round(nd(i,1)*fs)+size(tmpnote,1);
    wav(wavidx,:) = wav(wavidx,:) + tmpnote;
    currnote = nd(i,3);
    h.St.String = ['Writing DynAud file... ' mat2str(round(i*100/size(nd,1))) ' % done'];
    drawnow
end
wav = wav-min(wav(:));
wav = wav*2/max(wav(:))-1;

audiowrite([filename '.wav'],wav(1:round(fs*max(nd(:,2))),:)/max(wav(:)),fs);