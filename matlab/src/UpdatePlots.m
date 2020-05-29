function UpdatePlots(h)
% Some variables
ti = 5; % tick interval on H plot
H_sep = str2num(h.vscale.String); % std multiple for line seperation on H plot
tmp = zeros(1,size(h.H,1)); tmp(h.m.Wshow) = 1;
Wim = find(h.m.W_sf & tmp);

axes(h.axesH); cla
Hstd = std(h.H(:));
outinds = round(h.m.vstart*size(h.H,2))+1:round(h.m.vend*size(h.H,2));
t = 1/h.m.framerate:1/h.m.framerate:size(h.H,2)/h.m.framerate;
l_idx = numel(Wim);
for i = Wim
    if h.offsetH.Value
        plot(t(outinds),h.H(i,outinds)+(size(h.H,1)-i+1)*Hstd*H_sep,'Color',h.cmap(i,:))
    else
        plot(t(outinds),h.H(i,outinds),'Color',h.cmap(i,:))
    end
    hold on
end
if ~h.offsetH.Value
    line([0,size(h.H,2)],[h.m.thresh h.m.thresh],'LineStyle','--','Color','k','LineWidth',2)
end
colormap(h.cmap); caxis([0 size(h.cmap,1)]); %colorbar('EastOutside')
xlim([h.m.vstart h.m.vend]*size(h.H,2)/h.m.framerate)
if h.offsetH.Value
    ylim([-Hstd*H_sep (size(h.H,1)+1)*Hstd*H_sep])
    set(gca,'YTick',[(mod(size(h.H,1),ti)+1:ti:size(h.H,1)-1) size(h.H,1)]*Hstd*H_sep)
    ytlab = [fliplr(ti:ti:size(h.H,1)) 1];
    ytstr = {};
    for i = 1:numel(ytlab)
        yt_str{i} = ['H_{' num2str(ytlab(i)) '}'];
    end
    set(gca,'YTickLabel',yt_str)
    ylabel('Component #')
    colorbar('off')
else
    ylim([min(h.H(:))-Hstd max(h.H(:))-Hstd])
    ylabel('Amplitude')
    yticks('auto')
    yticklabels('auto')
    c1 = colorbar;
    ylabel(c1,'Component #')
end
set(gca,'XTick',[])

if isfield(h,'Mfinal')
    axes(h.axesMIDI)
    Mimg = zeros(size(h.H));
    cla
    for j = 1:numel(h.M.notestart)
        t = round(h.M.notestart(j)*h.m.framerate:h.M.noteend(j)*h.m.framerate)+1;
        Mimg(Wim(find(h.M.notekey(j)==h.m.keys)),t) = h.M.notemag(j);
    end
    imagesc(1-repmat(Mimg/max(Mimg(:)),[1 1 3]))
    xlim([0 h.m.vend-h.m.vstart]*size(h.H,2))
    hold on
    axes(h.axesH)
    xlabel('')
    axes(h.axesMIDI)
    xlabel('time (sec)');
    set(gca,'XTickLabels',round(xticks/h.m.framerate));
    h.axesMIDI.Position(3) = h.axesH.Position(3);
    set(gca,'YTick',[1 ti:ti:max(Wim)])
    ytlab = [1 ti:ti:max(Wim)];
    ytstr = {};
    for i = 1:numel(ytlab)
        yt_str{i} = ['H_{' num2str(ytlab(i)) '}'];
    end
    set(gca,'YTickLabel',yt_str)
    ylabel('Component #')
end
axes(h.axesW); cla
Wtmp = reshape(h.W(:,h.m.Wshow).*h.m.W_sf(h.m.Wshow)*h.cmap(h.m.Wshow,:),[h.m.ss(1:2) 3]);
imagesc(Wtmp)
axis equal
axis off

axes(h.axesWH); cla
sc = 256/str2num(h.clim.String);
im = reshape(h.W(:,h.m.Wshow)*diag(h.H(h.m.Wshow,h.framenum))*h.cmap(h.m.Wshow,:),[h.m.ss(1:2) 3]);
imagesc(uint8(im*sc))
caxis([0 str2num(h.clim.String)])
axis equal
axis off

drawnow
