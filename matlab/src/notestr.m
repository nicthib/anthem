function [out, ps] = notestr(noteval)
% Gets the file name you need to load based on note value, including the
% associated pitch shift (0-3).

note = mod(noteval,12); % mod of 1 is C
if note == 0
    note = 12;
end
oct = (noteval-note)/12;

switch note 
    case {1,2,3,4}
        out = ['C' mat2str(oct)];
    case {5,6,7,8}
        out = ['E' mat2str(oct)];
    case {9,10,11,12}
        out = ['G' mat2str(oct)];
end

ps = mod(note-1,4);
