function out = editcmap(hO,h)
uf = uifigure;
uf.Position(3:4) = [822 360];
c = zeros(size(h.cmap,1),1);
c(h.m.Wshow) = 1;
uit = uitable(uf,'CellEditCallback',@updatePlot);
uit.ColumnName = {'Red','Green','Blue','Visible'};
uit.Data = [h.cmap c];
uit.ColumnEditable = true;
uit.ColumnFormat = {'numeric','numeric','numeric','logical'};
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

function updatePlot(src,eventdata)
    h.m.Wshow = find(uit.Data(:,4));
    imagesc(reshape(h.W(:,h.m.Wshow)*uit.Data(h.m.Wshow,1:3),[h.m.ss(1:2) 3]),'Parent',ax)
    pbaspect(ax,[1 1 1])
    ax.XLim = [0 h.m.ss(1)];
    ax.YLim = [0 h.m.ss(1)];
    ax.XTick = [];
    ax.YTick = [];
    drawnow
end

function resetcmap(uit)
    uit.Data(:,1:3) = h.cmap;
    updatePlot
end

function makerandcmap(uit)
    uit.Data(:,1:3) = uit.Data(randperm(size(uit.Data,1)),1:3);
    updatePlot
end

function flipcmap(uit)
    uit.Data(:,1:3) = flipud(uit.Data(:,1:3));
    updatePlot
end

function selection(dd)
    val = dd.Value;
    tmp = eval([lower(val) '(size(h.cmap,1));']);
    uit.Data(:,1:3) = tmp;
    updatePlot
end

function exitGUI(uit,hO,h)
    h.cmap = uit.Data(:,1:3);
    h.m.Wshow = find(uit.Data(:,4));
    h = UpdateH(hO,h);
    guidata(hO,h);
    close(uf)
end
end
