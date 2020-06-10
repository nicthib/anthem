function UpdatePlots(h)
ti = 5; % tick interval on H plot
Hsep = h.vscale.Value; % std multiple for line seperation on H plot
Hstd = std(h.H_p(:));
fr = str2num(h.fr_in.String);

axes(h.axesH); cla
for i = 1:numel(h.Wshow.Value)
    if h.offsetH.Value
        plot(h.H_p(i,:)-h.H_p(i,1)+(size(h.H,1)-h.Wshow.Value(i)+1)*Hstd*Hsep,'Color',h.cmap(h.Wshow.Value(i),:))
    else
        plot(h.H_p(i,:),'Color',h.cmap(h.Wshow.Value(i),:))
    end
    hold on
end
if ~h.offsetH.Value
    l1 = line([0,size(h.H_p,2)],[h.thresh.Value h.thresh.Value],'LineStyle','--','Color','k','LineWidth',2);
    baseline = str2num(h.baseline.String);
    l2 = line([0,size(h.H_p,2)],[baseline,baseline],'LineStyle','--','Color',[.5 .5 .5],'LineWidth',2);
    legend([l1,l2],'Threshold','Offset')
end
colormap(h.cmap); caxis([0 size(h.cmap,1)]); xlim([0 size(h.H_p,2)])

if h.offsetH.Value
    ylim([-Hstd*Hsep (size(h.H,1)+1)*Hstd*Hsep])
    set(gca,'YTick',[(mod(size(h.H,1),ti)+1:ti:size(h.H,1)-1) size(h.H,1)]*Hstd*Hsep)
    ytlab = [fliplr(ti:ti:size(h.H,1)) 1];
    ytstr = {};
    for i = 1:numel(ytlab)
        yt_str{i} = ['H_{' num2str(ytlab(i)) '}'];
    end
    set(gca,'YTickLabel',yt_str)
    ylabel('Component #')
    colorbar('off')
    legend('off')
else
    ylim([min(h.H_p(:))-Hstd max(h.H_p(:))+Hstd])
    ylabel('Amplitude')
    yticks('auto')
    yticklabels('auto')
    c1 = colorbar('eastoutside');
    ylabel(c1,'Component #')
end
set(gca,'XTick',[])

if isfield(h,'Mfinal')
    axes(h.axesMIDI)
    Mimg = zeros(size(h.H_p));
    cla
    if h.audio_fmt.Value == 1
        Mimg = h.H_p;% Mimg(Mimg<0) = 0;
    else
        for j = 1:numel(h.M.notestart)
            t = round(h.M.notestart(j)*fr:h.M.noteend(j)*fr)+1;
            Mimg(h.Wshow.Value(find(h.M.notekey(j)==h.keys)),t) = h.M.notemag(j);
        end
    end
    imagesc(1-repmat(Mimg/max(Mimg(:)),[1 1 3]))
    ylim([0.5 size(h.H,1)+.5])
    xlim([0.5 size(h.H_p,2)])
    hold on
    axes(h.axesH)
    xlabel('')
    axes(h.axesMIDI)
    xlabel('time (sec)');
    set(gca,'XTickLabels',round(xticks/fr));
    h.axesMIDI.Position(3) = h.axesH.Position(3);
    set(gca,'YTick',[1 ti:ti:max(h.Wshow.Value)])
    ytlab = [1 ti:ti:max(h.Wshow.Value)];
    ytstr = {};
    for i = 1:numel(ytlab)
        yt_str{i} = ['H_{' num2str(ytlab(i)) '}'];
    end
    set(gca,'YTickLabel',yt_str)
    ylabel('Component #')
end

axes(h.axesW); cla
Wtmp = reshape(h.W(:,h.Wshow.Value)*h.cmap(h.Wshow.Value,:),[h.ss(1:2) 3]);
imagesc(Wtmp)
axis equal; axis off


drawnow
