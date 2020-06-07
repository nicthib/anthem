function h = UpdateH(hO,h)
st = str2num(h.vs_str.String)/100;
en = str2num(h.ve_str.String)/100;
h.m.outinds = round(st*size(h.H,2))+1:round(en*size(h.H,2));
h.St.String = 'Status: Updating H''...'; drawnow
h.H_p = h.H(h.m.Wshow,h.m.outinds) + str2num(h.yoffset.String);
if str2num(h.filterH.String) > 0
    h.St.String = 'Status: Filtering H...'; drawnow
    for i = 1:size(h.H_p,1)
        h.H_p(i,:) = highpass(h.H_p(i,:),str2num(h.filterH.String),str2num(h.fr_in.String));
        h.St.String = ['Status: Filtering H...' round(num2str(i*100/size(h.H_p,1))) '%']; drawnow
    end
end
h.St.String = 'Status: H updated.';
tmp = zeros(1,size(h.H,1)); tmp(h.m.Wshow) = 1;
h.m.keys = makekeys(h.scale.Value,h.scaletype.Value,numel(find(tmp==1)),str2num(h.addoct.String));
[h.Mfinal,h.nd] = H_to_nd(h.H_p,str2num(h.fr_in.String),h.m.thresh,h.m.keys);
h.M.notekey =   h.Mfinal(:,3);
h.M.notemag =   h.Mfinal(:,4);
h.M.notestart = h.Mfinal(:,5);
h.M.noteend =   h.Mfinal(:,6);
h.St.String = 'Status: H'' updated.';
UpdatePlots(h)
