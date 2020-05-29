% Compiling audio engine from raw audio files
function notefull = AudioEngine_GUI(y,fs)
sig = repmat([ones(1,fs*9) linspace(1,0,fs)]',[1 2]);
notefull = zeros(128,1+size(sig,1)+fs,2);
for i = 1:128
    notefull(i,:,:) = [[0 0]; y((i-1)*fs*12+1:i*fs*12-fs*2,:).*sig; zeros(fs,2)];
end

