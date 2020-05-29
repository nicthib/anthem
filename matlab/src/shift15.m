function shift15(notein,noteout,ps)
for i = 1:5
    for j = 1:3
        [tmp,fs] = audioread([notein '_' mat2str(i) '_' mat2str(j) '.ogg']);
        tmp(end+1:458700,:) = 0;
        out = pitchshift(tmp,ps);
        audiowrite([noteout '_' mat2str(i) '_' mat2str(j) '.ogg'],out,fs);        
    end
end