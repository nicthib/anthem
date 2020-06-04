function out = editcmap(hO,h)
uf = uifigure;
uf.Position(3:4) = [822 360];

uit = uitable(uf,'CellEditCallback',@updatePlot);
uit.ColumnName = {'Red','Green','Blue'};
uit.Data = h.cmap(h.m.Wshow,:);
uit.ColumnEditable = true;
uit.Position(3) = 375;

bpos = [470 310 50 25;520 310 50 25;570 310 50 25;620 310 50 25;670 310 50 25];

b1 = uibutton(uf,'Text','Reset','ButtonPushedFcn',@(b1,event) resetcmap(uit));
b1.Position = bpos(4,:);

b2 = uibutton(uf,'Text','Random','ButtonPushedFcn',@(b2,event) makerandcmap(uit));
b2.Position = bpos(2,:);

b3 = uibutton(uf,'Text','Flip','ButtonPushedFcn',@(b3,event) flipcmap(uit));
b3.Position = bpos(3,:);

b4 = uidropdown(uf,...
    'Position',bpos(1,:),...
    'Items',{'Jet','HSV','Hot','Parula'},...
    'Value','Jet',...
    'ValueChangedFcn',@(b4,event) selection(b4));

b5 = uibutton(uf,'Text','Done','ButtonPushedFcn',@(b5,event) exitGUI(uit,hO,h));
b5.Position = bpos(5,:);


ax = uiaxes(uf);
ax.Position(1) = 415;

updatePlot

function updatePlot()
    imagesc(reshape(h.W(:,h.m.Wshow)*uit.Data,[h.m.ss(1:2) 3]),'Parent',ax)
    pbaspect(ax,[1 1 1])
    ax.XLim = [0 h.m.ss(1)];
    ax.YLim = [0 h.m.ss(1)];
    ax.XTick = [];
    ax.YTick = [];
    drawnow
end

function resetcmap(uit)
    uit.Data = h.cmap;
    updatePlot
end

function makerandcmap(uit)
    uit.Data = uit.Data(randperm(size(uit.Data,1)),:);
    updatePlot
end

function flipcmap(uit)
    uit.Data = flipud(uit.Data);
    updatePlot
end

function selection(dd)
    val = dd.Value;
    tmp = eval([lower(val) '(numel(h.m.Wshow));']);
    uit.Data = tmp;
    updatePlot
end

function exitGUI(uit,hO,h)
    h.cmap = uit.Data;
    guidata(hO,h);
    close(uf)
end
end
