function out = NeuralStream(h)
filename = fullfile(h.savepath.String,h.filenameout.String);
C0 = 16.35;
freqs = C0*2.^((0:127)/12);
h.H(h.H<0) = 0;
movielength = size(h.H,2)/h.fr_out.Value;
fs = 44100;  % sampling frequency
t1 = linspace(0,movielength,size(h.H,2));
t2 = 0:1/fs:movielength;
if h.keys(end) > 128
    out = 0;
    return
else
    out = 1;
end
for i = 1:size(h.H,1)
    a(i,:) = sin(2*pi*freqs(h.keys(i))*t2);
    Hrs(i,:) = interp1(t1,h.H(i,:),t2);
end
song = sum(a.*Hrs,1);
song = song/max(song);
audiowrite([filename '.wav'],song,fs);
