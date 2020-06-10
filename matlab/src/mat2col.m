function out = mat2col(in)
if any(find(diff(in) < 1))
    out = NaN;
    return
end
tmp = min(find(diff(in)>1));
lst = {};
while ~isempty(tmp)
    lst{end+1} = in(1:tmp);
    in(1:tmp) = [];
    tmp = min(find(diff(in)>1)); 
end
lst{end+1} = in;
out = '[';
for i = 1:numel(lst)
    if numel(lst{i}) > 1
        out = [out num2str(lst{i}(1)) ':' num2str(lst{i}(end)) ', '];
    else
        out = [out num2str(lst{i}) ', '];
    end
end
out = [out(1:end-2) ']'];
