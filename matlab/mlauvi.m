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
% cd to active scriptlocation
tmp = matlab.desktop.editor.getActive;
h.mlauvipath = fileparts(tmp.Filename);
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
[File,Path] = uigetfile('.mat','Please choose a data file');
matObj = matfile(fullfile(Path, File));
matvars = whos(matObj);

for i = 1:numel({matvars.name})
    varstr{i} = ['Name = ' matvars(i).name ', size = ' mat2str(matvars(i).size)];
end
varH = listdlg('ListString',varstr,'Name','Choose Temporal Variable','ListSize',[300 100]);
varW = listdlg('ListString',varstr,'Name','Choose Spatial Variable','ListSize',[300 100]);

h.H = matObj.(matvars(varH).name);
h.W = matObj.(matvars(varW).name);
if (ndims(h.W) == 3 && size(h.H,1) == size(h.W,3)) || (ndims(h.W) == 2 && size(h.H,1) == size(h.W,2))
    % Initialize some params
    n = size(h.H,1);
    h.cmap = jet(n);
    h.m.Wshow = 1:n;
    h.m.ss = size(h.W);
    h.W = reshape(h.W,[prod(h.m.ss(1:2)) h.m.ss(3)]);
    h.framenum = 1;
    h.frameslider.Enable = 'on';
    h.vs_str.String = '0';
    h.ve_str.String = '100';
    h.m.fr_in = str2num(h.fr_in.String);
    h.m.thresh = str2num(h.thresh.String);
    h.m.brightness = max(h.H(:));
    pts = strsplit(File,'.');
    h.filename.String = pts{1};
    h.filenametext.String = pts{1};
    h = UpdateH(hO,h);
    guidata(hO, h);
else
    errordlg('Inner dimensions of HxW do not match!')
    h.St.String = 'Status: Data load failed!';
    drawnow
end

function Loadcfg_Callback(hO,~,h)
[file,path] = uigetfile('.mat','Please choose a cfg file');
close all
load(fullfile(path,file))
h.St.String = 'Status: config file successfuly loaded.';
drawnow
guidata(hO, h);

function Wshow_Callback(hO, ~, h)
if strcmp(h.Wshow.String,'all')
    h.m.Wshow = 1:size(h.H,1);
else
    h.m.Wshow = str2num(h.Wshow.String);
end
h = UpdateH(hO,h);
guidata(hO, h);

function fr_in_Callback(hO, ~, h)
h.m.fr_in = str2num(h.fr_in.String);
h = UpdateH(hO,h);
guidata(hO, h);

function thresh_Callback(hO, ~, h)
h.m.thresh = str2num(h.thresh.String);
h = UpdateH(hO,h);
guidata(hO, h);

function frameslider_Callback(hO, ~, h)
h.framenum = round(h.frameslider.Value*size(h.H_p,2));
if h.framenum == 0
    h.framenum = 1;
end
h.frametxt.String = [mat2str(round(h.framenum*100/str2num(h.fr_in.String))/100) ' sec'];
UpdatePlots(h)
guidata(hO, h);

function PlayVid_Callback(hO, ~, h)
while h.PlayVid.Value
    axes(h.axesWH);
    h.frameslider.Enable = 'off';
    sc = 256/h.m.brightness;
    im = reshape(h.W(:,h.m.Wshow)*diag(h.H_p(:,h.framenum))*h.cmap(h.m.Wshow,:),[h.m.ss(1:2) 3]);
    imagesc(uint8(sc*im))
    caxis([0 h.m.brightness])
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
h = UpdateH(hO,h);
savepath = strrep(h.mlauvipath,'matlab','outputs');
if h.audio_fmt.Value == 1 % Stream
    h.St.String = 'Status: Writing Audio stream...'; drawnow
    out = NeuralStream(h.H_p,h.m,fullfile(savepath,h.filename.String));
    if ~out
        h.St.String = 'Status: ERROR: The number of components and note arrangement you have chosen is too broad. Please try using less components or a tighter note arrangement (e.g. scale)';
        return
    end
    h.St.String = ['Audio stream ' h.filename.String ' written to ' savepath]; drawnow
    
elseif h.audio_fmt.Value == 2
    h.St.String = 'Status: Writing Dynamic Audio file...'; drawnow
    if ~isempty(h.nd)
        nd_to_wav(fullfile(strrep(h.mlauvipath,'matlab','outputs'),h.filename.String),h.nd,h);
    end
    h.St.String = 'Status: Dynamic Audio file written.'; drawnow
    
elseif h.audio_fmt.Value == 3
    h.St.String = 'Status: Writing MIDI...'; drawnow
    midiout = matrix2midi_nic(h.Mfinal,300,[4,2,24,8],0);
    writemidi(midiout, fullfile(strrep(h.mlauvipath,'matlab','outputs'),h.filename.String));
    h.St.String = 'Status: MIDI file written'; drawnow
    h.combineAV.Enable = 'on';
    
else
    h.St.String = 'Status: Please select an audio format in the edit menu drop down'; drawnow
end
guidata(hO,h)

function ExportAVI_Callback(hO, ~, h)
h = UpdateH(hO,h);
savepath = strrep(h.mlauvipath,'matlab','outputs');
h.St.String = 'Status: Writing AVI file...'; drawnow
sc = 256/h.m.brightness;
Wtmp = h.W(:,h.m.Wshow); Htmp = h.H_p;
cmaptmp = h.cmap(h.m.Wshow,:);
vidObj = VideoWriter(fullfile(savepath,[h.filename.String '.avi']));
vidObj.FrameRate = str2num(h.fr_in.String); open(vidObj)
for i = 1:size(Htmp,2)
    im = reshape(Wtmp*diag(Htmp(:,i))*cmaptmp,[h.m.ss(1:2) 3]);
    im = uint8(im*sc);
    frame.cdata = im;
    frame.colormap = [];
    writeVideo(vidObj,frame);
    pct_updt = 5;
    if mod(i,pct_updt) == 1
        h.St.String = ['Writing AVI file... ' mat2str(round(i*100/numel(h.m.outinds))) '% done'];
        drawnow
    end
end
h.St.String = 'Status: AVI file written';
close(vidObj);

function combineAV_Callback(hO, ~, h)
fn = fullfile(strrep(h.mlauvipath,'matlab','outputs'),h.filename.String); 
system(['ffmpeg -loglevel panic -i ' fn '.avi -i ' fn '.wav -codec copy -shortest ' fn '_audio.avi -y']);
if exist([fn '_audio.avi'])
    h.St.String = 'Status: AVI w/ audio successfully written.';
else
    h.St.String = 'Status: AVI w/ audio was unable to be written. Check to make sure you have the proper path to ffmpeg.exe in the ffmpegpath.txt file.';
end

function Savecfg_Callback(hO, ~, h)
save([h.filename.String '_cfg.mat'])
h.St.String = ['Config file saved as ' h.filename.String '_cfg.mat.'];

function targ = vF(targ) % visibility toggle
if strcmp(targ.Visible,'on')
    targ.Visible = 'off';
else
    targ.Visible = 'on';
end

function targ = eF(targ) % enable toggle
if strcmp(targ.Enable,'on')
    targ.Enable = 'off';
else
    targ.Enable = 'on';
end

function vs_str_Callback(hO, ~, h)
h.framenum = 1;
h = UpdateH(hO,h);
guidata(hO,h);

function ve_str_Callback(hO, ~, h)
h.framenum = 1;
h = UpdateH(hO,h);
guidata(hO,h);

%%%%%%%%%%%%%%%%%%%%%%%%%%% DROP DOWN CALLBACKS %%%%%%%%%%%%%%%%%%%%%%%%%%%

function check_fmt_1_Callback(hO, ~, h)
h.check_fmt_1.Checked = 'on';
h.check_fmt_2.Checked = 'off';
h.check_fmt_3.Checked = 'off';
guidata(hO,h)

function check_fmt_2_Callback(hO, ~, h)
h.check_fmt_1.Checked = 'off';
h.check_fmt_2.Checked = 'on';
h.check_fmt_3.Checked = 'off';
guidata(hO,h)

function check_fmt_3_Callback(hO, ~, h)
h.check_fmt_1.Checked = 'off';
h.check_fmt_2.Checked = 'off';
h.check_fmt_3.Checked = 'on';
guidata(hO,h)

function PlayNotes_Callback(hO,~,h)
if isfield(h.m,'keys')
    h.St.String = 'Status: Playing keys...'; drawnow
    for i = 1:numel(h.m.keys)
        tic
        if strcmp(h.check_fmt_1.Checked,'on') % Stream
            freq = 16.35*2.^(h.m.keys(i)/12);
            if ~exist('t')
                t = 0:(1/16384):.5;
                g = [linspace(0,1,2000) ones(1,8193-4000) linspace(1,0,2000)];
            end
            y = g.*sin(2*pi*freq*t);
        else
            [note,ps] = notestr(h.m.keys(i)+1);
            y = loadnote(note,ps,0);
        end
        pause(.5-toc)
        sound(y,44100)
    end
    h.St.String = 'Status: Done playing keys.';
else
end
guidata(hO,h)

function addoct_Callback(hO, ~, h)
h = UpdateH(hO,h);
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
UpdatePlots(h)

function yoffset_Callback(hO, ~, h)
h = UpdateH(hO,h);
UpdatePlots(h)

function brightness_Callback(hO, ~, h)
tmp = inputdlg({'New max brightness:'},'Brightness adjustment',1,{mat2str(h.m.brightness)});
h.m.brightness = str2num(tmp{1});
UpdatePlots(h)
guidata(hO, h);

function audio_fmt_Callback(hO, ~, h)
UpdatePlots(h)
guidata(hO, h);

function filterH_Callback(hO, ~, h)
h = UpdateH(hO,h);
guidata(hO, h);

%%%%%%%%%%%%%%%%%%%%%%%%%%%% UNUSED CALLBACKS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function fr_in_CreateFcn(hO, ~, h)
function Wshow_CreateFcn(hO, ~, h)
function thresh_CreateFcn(hO, ~, h)
function frameslider_CreateFcn(hO, ~, h)
function scale_CreateFcn(hO, ~, h)
function filename_Callback(hO, ~, h)
function filename_CreateFcn(hO, ~, h)
function scaletype_CreateFcn(hO, ~, h)
function addoct_CreateFcn(hO, ~, h)
function ve_str_CreateFcn(hO, ~, h)
function vs_str_CreateFcn(hO, ~, h)
function vscale_CreateFcn(hO, ~, h)
function noteGUI_Callback(hO, ~, h)
function yoffset_CreateFcn(hO, ~, h)
function audio_fmt_CreateFcn(hO, ~, h)
function filterH_CreateFcn(hO, ~, h)
