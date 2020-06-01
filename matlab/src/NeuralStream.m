function out = NeuralStream(H,m,filename)
C0 = 16.35;
freqs = C0*2.^((0:127)/12);
H(H<0) = 0;
movielength = size(H,2)/m.framerate;
fs = 44100;  % sampling frequency
t1 = linspace(0,movielength,size(H,2));
t2 = 0:1/fs:movielength;
if m.keys(end) > 128
    out = 0;
    return
else
    out = 1;
end
for i = 1:size(H,1)
    a(i,:) = sin(2*pi*freqs(m.keys(i))*t2);
    Hrs(i,:) = interp1(t1,H(i,:),t2);
end
song = sum(a.*Hrs,1);
song = song/max(song);
audiowrite([filename '.wav'],song,fs);
