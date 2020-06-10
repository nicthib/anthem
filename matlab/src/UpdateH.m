function h = UpdateH(h)
st = str2num(h.vs_str.String)/100;
en = str2num(h.ve_str.String)/100;
h.outinds = round(st*size(h.H,2))+1:round(en*size(h.H,2));
h.St.String = 'Status: Updating H''...'; drawnow
h.H_p = h.H(h.Wshow.Value,h.outinds) + str2num(h.baseline.String);
if str2num(h.filterH.String) > 0
    h.St.String = 'Status: Filtering H...'; drawnow
    for i = 1:size(h.H_p,1)
        h.H_p(i,:) = highpass(h.H_p(i,:),str2num(h.filterH.String),str2num(h.fr_in.String));
        h.St.String = ['Status: Filtering H...' round(num2str(i*100/size(h.H_p,1))) '%']; drawnow
    end
end
h.St.String = 'Status: H updated.';
h.keys = makekeys(h.scale.Value,h.scaletype.Value,numel(h.Wshow.Value),h.addoct.Value-1);
[h.Mfinal,h.nd] = H_to_nd(h.H_p,str2num(h.fr_in.String),h.thresh.Value,h.keys);
h.M.notekey =   h.Mfinal(:,3);
h.M.notemag =   h.Mfinal(:,4);
h.M.notestart = h.Mfinal(:,5);
h.M.noteend =   h.Mfinal(:,6);
h.St.String = 'Status: H'' updated.';
UpdatePlots(h)
