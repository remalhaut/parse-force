%% batch_process
% main dir
%  | index.txt (header row: kcant, smpl, cntrl  - without .mat)
%  | glass1.mat
%  | ...
%  | smplname1.mat
%  | ...
%%%%%%%%%%%%%%%%%%%%%%%%%%%
clear all;
close all;
currfold = pwd;
folder = uigetdir('Pick directory');
cd(folder);
if and(not(exist('index.txt', 'file') == 2), not(exist('index.csv', 'file') == 2))
    display('Index file (index.txt/index.csv) not found. Please create a comma-separate index file containing three columns: kcant, smpl and cntrl(first line should be headers)');
    return
elseif (exist('index.csv', 'file') == 2)
    fid = fopen('index.csv');
else
    fid = fopen('index.txt');
end
depths = input('Input depths (nm) to use as a vector in square brackets\n');

lines = textscan(fid, '%s', 'delimiter', '\n');
fclose(fid);
lines = lines{1};
header = regexp(lines{1},',','split');
lines = lines(2:end);
for i = 1:length(header)
    head = strtrim(header(i));
end
results(1) = struct();
for i = 1:length(lines)
    row = regexp(lines{i},',','split');
    for j = 1: length(header)
        results(i).(header{j}) = strtrim(row{j});
    end
    kcant = eval(results(i).kcant);
    results(i).cntrl_result_fname = [results(i).cntrl '-results.mat'];
    if exist(results(i).cntrl_result_fname, 'file') == 2
        load(results(i).cntrl_result_fname);
    else
        control_struct = load(results(i).cntrl);
        cntrl_result = control_func(control_struct, results(i).cntrl);
        save(results(i).cntrl_result_fname, 'cntrl_result');
    end
    sens = cntrl_result.fitted.mean_sensitivity;
    results(i).smpl_graph_fname = [results(i).smpl '-graph'];
    results(i).smpl_result_fname = [results(i).smpl '-results.mat'];
    if exist(results(i).smpl_result_fname, 'file') == 2
        load(results(i).smpl_result_fname);
    else
        sample_struct = load(results(i).smpl);
        smpl_result = sample_func(sample_struct, cntrl_result, kcant, depths,results(i).smpl);
        g = smplgraphs(smpl_result, cntrl_result, kcant, results(i).smpl);
        result_graph = handle2struct(gcf);
        save([results(i).smpl '-results.mat'], 'smpl_result');
        saveas(g, [results(i).smpl '-graph.fig']);
        saveas(g, [results(i).smpl '-graph.png']);
        waitfor(g);
    end
    results(i).kmm = smpl_result.fitted.k_measured_mean;
    results(i).ksm = smpl_result.fitted.k_sample_mean;
    results(i).kcant = kcant;
    results(i).sens = sens;
    close all;
end
save([folder '.mat'], 'results');
outf = fopen([folder '-.txt'],'wt');
fprintf(outf,'\t\tDepths:\t');
for i = 1:length(depths)
    fprintf(outf, '\t %3s nm', num2str(depths(i)));
end
fprintf(outf, '\r\n');
fprintf(outf,'SmplName\tkcant\tsens\tStiffness(N/m)');
fprintf(outf, '\r\n');
for i = 1:length(results)
    fprintf(outf,'%8s\t%2.3f\t%3.2f',results(i).smpl,results(i).kcant,results(i).sens);
    for j=1:length(results(i).ksm)
        fprintf(outf,'\t%2.3f',results(i).ksm(j));
    end
    fprintf(outf, '\r\n');
end
fclose(outf);