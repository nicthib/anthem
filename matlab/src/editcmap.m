function out = editcmap(hO,h)
uf = uifigure;
uf.Position(3:4) = [822 360];

uit = uitable(uf,'CellEditCallback',@updatePlot);
uit.ColumnName = {'Red','Green','Blue'};
uit.Data = h.cmap(h.m.Wshow,:);
uit.ColumnEditable = true;
uit.Position(3) = 375;

b1 = uibutton(uf,'Text','Reset','ButtonPushedFcn',@(b1,event) resetcmap(b1,uit));
b1.Position = [470 310 50 25];
b2 = uibutton(uf,'Text','Random','ButtonPushedFcn',@(b2,event) makerandcmap(b2,uit));
b2.Position = [520 310 50 25];
dd = uidropdown(uf,...
    'Position',[570 310 50 25],...
    'Items',{'Jet','HSV','Hot','Parula'},...
    'Value','Jet',...
    'ValueChangedFcn',@(dd,event) selection(dd));

bdone = uibutton(uf,'Text','Done','ButtonPushedFcn',@(bdone,event) exitGUI(bdone,uit,hO,h));
bdone.Position = [620 310 50 25];
b3 = uibutton(uf,'Text','Flip','ButtonPushedFcn',@(b3,event) flipcmap(b3,uit));
b3.Position = [670 310 50 25];

ax = uiaxes(uf);
ax.Position(1) = 415;

updatePlot

function updatePlot(src,eventdata)
    imagesc(reshape(h.W(:,h.m.Wshow).*h.m.W_sf(h.m.Wshow)*uit.Data,[h.m.ss(1:2) 3]),'Parent',ax)
    pbaspect(ax,[1 1 1])
    ax.XLim = [0 h.m.ss(1)];
    ax.YLim = [0 h.m.ss(1)];
    ax.XTick = [];
    ax.YTick = [];
    drawnow
end

function resetcmap(btn,uit)
    uit.Data = h.cmap(h.m.Wshow,:);
    updatePlot
end

function makerandcmap(btn,uit)
    tmp = jet(numel(h.m.Wshow));
    uit.Data = tmp(randperm(numel(h.m.Wshow)),:);
    updatePlot
end

function flipcmap(btn,uit)
    uit.Data = flipud(uit.Data);
    updatePlot
end

function selection(dd)
    val = dd.Value;
    tmp = eval([lower(val) '(numel(h.m.Wshow));']);
    uit.Data = tmp;
    updatePlot
end

function exitGUI(btn,uit,hO,h)
    h.cmap = uit.Data;
    guidata(hO,h);
    UpdatePlots(h)
    close(uf)
end
end
