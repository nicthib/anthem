function out = loadnote(note,ps,all)
if all
    for i = 1:5
        for j = 1:3
            if ps == 0
                out{i,j} = audioread([note '_' mat2str(i) '_' mat2str(j) '.mp3']);
                out{i,j}(end+1:458700,:) = 0; % append zeros to cells that are too short
            else
                tmp = audioread([note '_' mat2str(i) '_' mat2str(j) '.mp3']);
                tmp(end+1:458700,:) = 0;
                out{i,j} = pitchshift(tmp,ps); % append zeros to cells that are too short
            end
            
        end
    end
else
    if ps == 0
        out = audioread([note '_2_2.mp3']);
        out(end+1:458700,:) = 0; % append zeros to cells that are too short
    else
        tmp = audioread([note '_2_2.mp3']);
        tmp(end+1:458700,:) = 0;
        out = pitchshift(tmp,ps); % append zeros to cells that are too short
    end
end
