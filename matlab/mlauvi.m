function varargout = mlauvi(varargin)
gui_Singleton = 1;
gui_State = struct('gui_Name', mfilename, ...
    'gui_Singleton',  gui_Singleton, ...
    'gui_OpeningFcn', @mlauvi_OpeningFcn, ...
    'gui_OutputFcn',  @mlauvi_OutputFcn, ...
    'gui_LayoutFcn',  [] , ...
    'gui_Callback',   []);
if nargin && ischar(varargin{1}); gui_State.gui_Callback = str2func(varargin{1}); end
if nargout; [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:}); else; gui_mainfcn(gui_State, varargin{:}); end

function mlauvi_OpeningFcn(hO, ~, h, varargin)
warning('off','all')
% cd to active script location
tmp = matlab.desktop.editor.getActive;
h.mlauvipath = fileparts(tmp.Filename);
h.savepath.String = strrep(h.mlauvipath,'matlab','outputs');
h.oggpath = strrep(h.mlauvipath,'matlab','AE');
cd(h.mlauvipath);
% Addpath GUI folder
addpath(genpath(h.mlauvipath));
% set ffmpeg path (for combining V/A)
try
    setenv('PATH', cell2mat(importdata('ffmpegpath.txt')))
    h.St.String = 'Status: ffmpeg path set. Ready to load a dataset';
catch
    h.St.String = 'Status: No ffmpeg path found in ffmpegpath.txt. Please update this file to add audio and video seamlessly.';
end
% Make gui 90% of screen size
hO.Units = 'normalized';
hO.Position = [.05 .05 .75 .65];
guidata(hO, h);

function varargout = mlauvi_OutputFcn(hO, ~, h)
varargout{1} = hO;

%%%%%%%%%%%%%%%%%%%%%%%%%% MAIN CALLBACKS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function LoadData_Callback(hO, ~, h)
[file,path] = uigetfile('.mat','Please choose a data file');
if ~file
    return
end
matObj = matfile(fullfile(path,file));
matvars = whos(matObj);
for i = 1:numel({matvars.name})
    varstr{i} = ['Name = ' matvars(i).name ', size = ' mat2str(matvars(i).size)];
end
varH = listdlg('ListString',varstr,'Name','Choose Temporal Variable','ListSize',[300 100]);
varW = listdlg('ListString',varstr,'Name','Choose Spatial Variable','ListSize',[300 100]);

h.H = matObj.(matvars(varH).name);
h.W = matObj.(matvars(varW).name);
h.ss = size(h.W); % Makes reshaping in the future easier
if ndims(h.W) == 3 && h.ss(end) == size(h.H,1) % Checking that inner dimensions of WxH match
    % Initialize some params
    h.cmap = jet(size(h.H,1));
    h.W = reshape(h.W,[prod(h.ss(1:2)) h.ss(3)]);
    
    % Video panel enables
    h.fr_in.String = '10'; h.fr_in.Value = str2num(h.fr_in.String); h.fr_in.Enable = 'on';
    h.vs_str.String = '0'; h.vs_str.Value = 0; h.vs_str.Enable = 'on';
    h.ve_str.String = '100'; h.ve_str.Value = 100; h.ve_str.Enable = 'on';
    h.baseline.String = '0'; h.baseline.Value = str2num(h.baseline.String); h.baseline.Enable = 'on';
    h.filterH.String = '0'; h.filterH.Value = str2num(h.filterH.String); h.filterH.Enable = 'on';
    h.brightness.Value = max(h.H(:)); h.brightness.String = num2str(h.brightness.Value); h.brightness.Enable = 'on';
    h.editcmap.Enable = 'on';
    
    % Audio panel enables
    h.thresh.String = num2str(mean(h.H(:))); h.thresh.Value = str2num(h.thresh.String); h.thresh.Enable = 'on';
    h.addoct.Enable = 'on';
    h.scaletype.Enable = 'on'; h.scale.Enable = 'on'; h.audio_fmt.Enable = 'on';
    h.noteGUI.Enable = 'on'; h.PlayNotes.Enable = 'on';
    
    % Other enables
    h.PlayVid.Enable = 'on';
    h.vscale.String = '5'; h.vscale.Value = str2num(h.vscale.String); h.vscale.Enable = 'on';
    h.Wshow.Value = 1:size(h.H,1); h.Wshow.Enable = 'on';
    h.framenum = 1; h.frameslider.Enable = 'on';
    h.offsetH.Enable = 'on';
    
    pts = strsplit(file,'.');
    h.filenameout.String = pts{1}; h.filenamein.String = pts{1};
    h = UpdateH(h);
    guidata(hO, h);
    
    frameslider_Callback(hO, [], h)
elseif h.ss(end) == size(h.H,1)
    errordlg('Inner dimensions of HxW do not match!')
    h.St.String = 'Status: Data load failed!';
elseif size(h.W) ~= 3
    errordlg('W must be 3 dimensional!')
    h.St.String = 'Status: Data load failed!';
end

function Loadcfg_Callback(hO,~,h)
[file,path] = uigetfile('.mat','Please choose a cfg file');
if ~file
    return
end
close all
load(fullfile(path,file))
h.St.String = 'Status: config file successfuly loaded.';
drawnow
guidata(hO, h);

function frameslider_Callback(hO, ~, h)
h.framenum = round(h.frameslider.Value*size(h.H_p,2));
if h.framenum == 0
    h.framenum = 1;
end
h.frametxt.String = [mat2str(round(h.framenum*100/str2num(h.fr_in.String))/100) ' sec'];
axes(h.axesWH);
im = reshape(h.W(:,h.Wshow.Value)*diag(h.H_p(:,h.framenum))*h.cmap(h.Wshow.Value,:),[h.ss(1:2) 3]);
sc = 256/h.brightness.Value;
imagesc(uint8(im*sc))
caxis([0 h.brightness.Value])
axis equal; axis off
guidata(hO, h);

function PlayVid_Callback(hO, ~, h)
while h.PlayVid.Value
    axes(h.axesWH);
    h.frameslider.Enable = 'off';
    sc = 256/h.brightness.Value;
    im = reshape(h.W(:,h.Wshow.Value)*diag(h.H_p(:,h.framenum))*h.cmap(h.Wshow.Value,:),[h.ss(1:2) 3]);
    imagesc(uint8(sc*im))
    caxis([0 h.brightness.Value])
    axis equal; axis off
    h.frametxt.String = [mat2str(round(h.framenum*100/str2num(h.fr_in.String))/100) ' sec'];
    h.framenum = h.framenum + 1;
    h.frameslider.Value = h.framenum/size(h.H_p,2);
    if ~h.PlayVid.Value
        break
    end
    if h.framenum == size(h.H_p,2)
        h.PlayVid.Value = 0;
        h.frameslider.Value = 0;
    end
    drawnow
end
h.frameslider.Enable = 'on';
guidata(hO, h);

function editcmap_Callback(hO, ~, h)
editcmap(hO,h);
guidata(hO,h);

function ExportAudio_Callback(hO, ~, h)
h = UpdateH(h);
if h.audio_fmt.Value == 1 % Stream
    h.St.String = 'Status: Writing Audio stream...'; drawnow
    %out = NeuralStream(h.H_p,h.m,fullfile(savepath,h.filenameout.String));
    out = NeuralStream(h);
    if ~out
        h.St.String = 'Status: ERROR: The number of components and note arrangement you have chosen is too broad. Please try using less components or a tighter note arrangement (e.g. scale)';
        return
    end
    h.St.String = ['Audio stream ' h.filenameout.String ' written to ' savepath]; drawnow
    
elseif h.audio_fmt.Value == 2
    h.St.String = 'Status: Writing Dynamic Audio file...'; drawnow
    if isfield(h,'nd')
        nd_to_wav(h);
    end
    h.St.String = 'Status: Dynamic Audio file written.'; drawnow
    
elseif h.audio_fmt.Value == 3
    h.St.String = 'Status: Writing MIDI...'; drawnow
    midiout = matrix2midi(h.Mfinal,300,[4,2,24,8],0);
    writemidi(midiout, fullfile(h.savepath.String,h.filenameout.String));
    h.St.String = 'Status: MIDI file written'; drawnow
    h.combineAV.Enable = 'on';
    
else
    h.St.String = 'Status: Please select an audio format in the edit menu drop down'; drawnow
end
guidata(hO,h)

function ExportAVI_Callback(hO, ~, h)
h = UpdateH(h);
h.St.String = 'Status: Writing AVI file...'; drawnow
sc = 256/h.brightness.Value;
Wtmp = h.W(:,h.Wshow.Value); Htmp = h.H_p;
cmaptmp = h.cmap(h.Wshow.Value,:);
vidObj = VideoWriter(fullfile(h.savepath.String,[h.filenameout.String '.avi']));
vidObj.FrameRate = str2num(h.fr_in.String); open(vidObj)
for i = 1:size(Htmp,2)
    im = reshape(Wtmp*diag(Htmp(:,i))*cmaptmp,[h.ss(1:2) 3]);
    im = uint8(im*sc);
    frame.cdata = im;
    frame.colormap = [];
    writeVideo(vidObj,frame);
    pct_updt = 5;
    if mod(i,pct_updt) == 1
        h.St.String = ['Writing AVI file... ' mat2str(round(i*100/numel(h.outinds))) '% done'];
        drawnow
    end
end
h.St.String = 'Status: AVI file written';
close(vidObj);

function combineAV_Callback(hO, ~, h)
fn = fullfile(h.savepath.String,h.filenameout.String); 
system(['ffmpeg -loglevel panic -i ' fn '.avi -i ' fn '.wav -codec copy -shortest ' fn '_audio.avi -y']);
if exist([fn '_audio.avi'])
    h.St.String = 'Status: AVI w/ audio successfully written.';
else
    h.St.String = 'Status: AVI w/ audio was unable to be written. Check to make sure you have the proper path to ffmpeg.exe in the ffmpegpath.txt file.';
end

function Savecfg_Callback(hO, ~, h)
save(fullfile(h.savepath.String,[h.filenameout.String '_cfg.mat']))
h.St.String = ['Config file saved as ' h.filenameout.String '_cfg.mat.'];

function targ = vF(targ) % visibility toggle
if strcmp(targ.Visible,'on')
    targ.Visible = 'off';
else
    targ.Visible = 'on';
end

function PlayNotes_Callback(hO,~,h)
h.keys = makekeys(h.scale.Value,h.scaletype.Value,numel(h.Wshow.Value),h.addoct.Value-1);
h.St.String = 'Status: Loading keys...'; drawnow
for i = 1:numel(h.keys)
    fn = [num2str(h.keys(i)) '_5_2.ogg'];
    y{i} = audioread(fullfile(h.oggpath,fn),[1 44100]);
end

h.St.String = 'Status: Playing keys...'; drawnow
axes(h.axesW)
axis image; axis off; hold on
for i = 1:numel(y)
    tic
    Wtmp = reshape(h.W(:,h.Wshow.Value(i))*h.cmap(h.Wshow.Value(i),:),[h.ss(1:2) 3]);
    imagesc(Wtmp); 
    drawnow
    sound(y{i},44100)
    pause(.333-toc)
end

h.St.String = 'Status: Done playing keys.';
Wtmp = reshape(h.W(:,h.Wshow.Value)*h.cmap(h.Wshow.Value,:),[h.ss(1:2) 3]);
imagesc(Wtmp)
axis equal; axis off
guidata(hO,h)

function vs_str_Callback(hO, ~, h)
tmp = str2num(h.vs_str.String);
if ~isempty(tmp) && 100 > tmp && tmp >= 0
    h.vs_str.Value = tmp;
    h.framenum = 1;
    h = UpdateH(h);
else
    errordlg('Please input a number >= 0  and < 100 for start %')
    h.vs_str.String = num2str(h.vs_str.Value);
end
guidata(hO,h);

function ve_str_Callback(hO, ~, h)
tmp = str2num(h.ve_str.String);
if ~isempty(tmp) && 100 >= tmp && tmp > 0
    h.ve_str.Value = tmp;
    h.framenum = 1;
    h = UpdateH(h);
else
    errordlg('Please input a number > 0  and <= 100 for end %')
    h.ve_str.String = num2str(h.ve_str.Value);
end
guidata(hO,h);

function addoct_Callback(hO, ~, h)
guidata(hO, h);

function scaletype_Callback(hO, ~, h)
guidata(hO, h);

function scale_Callback(hO, ~, h)
guidata(hO, h);

function offsetH_Callback(hO, ~, h)
h.vscale = vF(h.vscale);
h.text28 = vF(h.text28);
h.axesMIDI.Position(3) = h.axesH.Position(3);
UpdatePlots(h)
guidata(hO, h);

function vscale_Callback(hO, ~, h)
tmp = str2num(h.vscale.String);
if ~isempty(tmp) && tmp > 0
    h.vscale.Value = tmp;
    UpdatePlots(h)
else
    errordlg('Please input a positive number for vertical scaling')
    h.vscale.String = num2str(h.vscale.Value);
end

function baseline_Callback(hO, ~, h)
tmp = str2num(h.baseline.String);
if ~isempty(tmp)
    if isempty(find(h.H(:) + tmp > h.thresh.Value))
        errordlg('Baseline is too low! Please input a baseline less than -max(H)')
        h.baseline.String = num2str(h.baseline.Value);
    else
        h.baseline.Value = tmp;
        h = UpdateH(h);
        UpdatePlots(h)
    end
else
    errordlg('Please input a number for baseline')
    h.baseline.String = num2str(h.baseline.Value);
end

function brightness_Callback(hO, ~, h)
tmp = str2num(h.brightness.String);
if ~isempty(tmp) && tmp > 0
    h.brightness.Value = tmp;
    UpdatePlots(h)
else
    errordlg('Please input a number greater than 0 for max brightness')
    h.brightness.String = num2str(h.brightness.Value);
end
frameslider_Callback(hO, [], h)
guidata(hO, h);

function filterH_Callback(hO, ~, h)
tmp = str2num(h.filterH.String);
if ~isempty(tmp) && tmp >= 0
    h.filterH.Value = tmp;
    h = UpdateH(h);
else
    errordlg('Please input a positive HP frequency (0 = no filtering)')
    h.filterH.String = num2str(h.filterH.Value);
end
guidata(hO, h);

function audio_fmt_Callback(hO, ~, h)
UpdatePlots(h)
guidata(hO, h);

function Wshow_Callback(hO, ~, h)
if strcmp(h.Wshow.String,'all')
    h.Wshow.Value = 1:size(h.H,1);
else
    h.Wshow.Value = str2num(h.Wshow.String);
end
h = UpdateH(h);
guidata(hO, h);

function fr_in_Callback(hO, ~, h)
tmp = str2num(h.fr_in.String);
if ~isempty(tmp) && tmp > 0
    h.fr_in.Value = tmp;
    h = UpdateH(h);
else
    errordlg('Please input a positive number for framerate')
    h.fr_in.String = num2str(h.fr_in.Value);
end
guidata(hO, h);

function thresh_Callback(hO, ~, h)
tmp = str2num(h.thresh.String);
if ~isempty(tmp)
    h.thresh.Value = tmp;
    h = UpdateH(h);
else
    errordlg('Please input a number for threshold')
    h.thresh.String = num2str(h.thresh.Value);
end
guidata(hO, h);

function savepath_Callback(hO, ~, h)
tmp = uigetdir(h.savepath.String);
if tmp
    h.savepath.String = tmp;
end
guidata(hO, h);

function editsavepath_Callback(hO, ~, h)
savepath_Callback(hO, [], h)

%%%%%%%%%%%%%%%%%%%%%%%%%%%% UNUSED CALLBACKS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function fr_in_CreateFcn(hO, ~, h)
function Wshow_CreateFcn(hO, ~, h)
function thresh_CreateFcn(hO, ~, h)
function frameslider_CreateFcn(hO, ~, h)
function scale_CreateFcn(hO, ~, h)
function filenameout_Callback(hO, ~, h)
function filenameout_CreateFcn(hO, ~, h)
function scaletype_CreateFcn(hO, ~, h)
function addoct_CreateFcn(hO, ~, h)
function ve_str_CreateFcn(hO, ~, h)
function vs_str_CreateFcn(hO, ~, h)
function vscale_CreateFcn(hO, ~, h)
function noteGUI_Callback(hO, ~, h)
function baseline_CreateFcn(hO, ~, h)
function audio_fmt_CreateFcn(hO, ~, h)
function filterH_CreateFcn(hO, ~, h)
function doNothing_Callback(hO, ~, h)
function brightness_CreateFcn(hO, ~, h)
function savepath_CreateFcn(hO, ~, h)
