
%% Split ogg
L = {'S','M','L'};
fs = 44100;
for j = 1:3
    y = audioread(['ae_' L{j} '.ogg']);
    for i = 0:(128*8)-1
        tmp = y(i*fs*10+1:(i+1)*fs*10,:);
        note = mod(i,128);
        mag = (i-mod(i,128))/128;
        % note_Length_mag.ogg
        filename = [num2str(note) '_'  num2str(mag) '_' num2str(j) '.ogg'];
        audiowrite(fileparts('split', filename),tmp,fs)
    end
end