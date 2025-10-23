function compare_MPSO()
    % 文件夹路径
    folder1 = 'SLPSO';
    folder2 = 'OLPSO';
    folder3 = 'MPSO';
    folder4 = 'LEO';
    folder5 = 'GLPSO';
    folder6 = 'ALC-PSO';
    
    better_1=0;
    better_2=0;
    better_3=0;
    better_4=0;
    better_5=0;
    
    similar_1=0;
    similar_2=0;
    similar_3=0;
    similar_4=0;
    similar_5=0;
    
    worse_1=0;
    worse_2=0;
    worse_3=0;
    worse_4=0;
    worse_5=0;


    % 获取文件列表并筛选出符合命名规则的文件
    files1 = dir(fullfile(folder1, '*_30_10total_DRLPSO.txt'));  % 假设文件为 .txt 格式
    files2 = dir(fullfile(folder2, '*_30total_OLPSO.txt'));
    files3 = dir(fullfile(folder3, '*_30total_GPSO.txt'));
    files4 = dir(fullfile(folder4, '*_30_total_LEO.txt'));
    files5 = dir(fullfile(folder5, '*_30total_GLPSO.txt'));
    files6 = dir(fullfile(folder6, '*_30total_ALC_PSO.txt'));


    % 提取并排序文件前缀（函数编号）
    funcNumbers1 = arrayfun(@(x) str2double(extractBefore(x.name, '_30')), files1);
    funcNumbers2 = arrayfun(@(x) str2double(extractBefore(x.name, '_30total')), files2);
    funcNumbers3 = arrayfun(@(x) str2double(extractBefore(x.name, '_30total')), files3);
    funcNumbers4 = arrayfun(@(x) str2double(extractBefore(x.name, '_30total')), files4);
    funcNumbers5 = arrayfun(@(x) str2double(extractBefore(x.name, '_30total')), files5);
    funcNumbers6 = arrayfun(@(x) str2double(extractBefore(x.name, '_30total')), files6);


    % 按编号排序文件列表
    [~, sortedIdx1] = sort(funcNumbers1);
    [~, sortedIdx2] = sort(funcNumbers2);
    [~, sortedIdx3] = sort(funcNumbers3);
    [~, sortedIdx4] = sort(funcNumbers4);
    [~, sortedIdx5] = sort(funcNumbers5);
    [~, sortedIdx6] = sort(funcNumbers6);


    files1 = files1(sortedIdx1);
    files2 = files2(sortedIdx2);
    files3 = files3(sortedIdx3);
    files4 = files4(sortedIdx4);
    files5 = files5(sortedIdx5);
    files6 = files6(sortedIdx6);


    % Excel 文件路径
    excelFile = 'comparison_results_10.xlsx';
    
    % 初始化 Excel 表头
    headers = {'Function', 'SLPSO','OLPSO','MPSO','LEO','GLPSO','ALC-PSO'};
    writecell(headers, excelFile, 'Sheet', 1, 'Range', 'A1');
    
    % 行数初始化
    row = 2;
    
    % 遍历排序后的文件列表
    for i = 1:length(files1)
        % 提取函数编号前缀
        funcPrefix1 = extractBefore(files1(i).name, '_30');
        funcPrefix2 = extractBefore(files2(i).name, '_30');
        funcPrefix3 = extractBefore(files3(i).name, '_30');
        funcPrefix4 = extractBefore(files4(i).name, '_30');
        funcPrefix5 = extractBefore(files5(i).name, '_30');
        funcPrefix6 = extractBefore(files6(i).name, '_30');


        % 确保函数编号一致
        if strcmp(funcPrefix1, funcPrefix2) && strcmp(funcPrefix1, funcPrefix3)
            % 构建完整文件路径
            slFile = fullfile(folder1, files1(i).name);
            olFile = fullfile(folder2, files2(i).name);
            mFile = fullfile(folder3, files3(i).name);
            leoFile = fullfile(folder4, files4(i).name);
            glFile = fullfile(folder5, files5(i).name);
            alcFile = fullfile(folder6, files6(i).name);


            % 读取 ALC_MAPSO 和 MFCPSO 文件的数据
            data1 = readmatrix(slFile);
            data2 = readmatrix(olFile);
            data3 = readmatrix(mFile);
            data4 = readmatrix(leoFile);
            data5 = readmatrix(glFile);
            data6 = readmatrix(alcFile);





            % 提取前 30 行
            data1 = data1(1:30);
            data2 = data2(1:30);
            data3 = data3(1:30);
            data4 = data4(1:30);
            data5 = data5(1:30);
            data6 = data6(1:30);


            % 计算 ALC_MAPSO 统计量
            mean1 = mean(data1);
            std1 = std(data1);
            min1 = min(data1);
            
            % 计算 MFCPSO 统计量
            mean2 = mean(data2);
            std2 = std(data2);
            min2 = min(data2);

            % 计算 APSO 统计量
            mean3 = mean(data3);
            std3 = std(data3);
            min3 = min(data3);
            
            mean4 = mean(data4);
            std4 = std(data4);
            min4 = min(data4);
            
            mean5 = mean(data5);
            std5 = std(data5);
            min5 = min(data5);
            
            mean6 = mean(data6);
            std6 = std(data6);
            min6 = min(data6);


            % 进行 Wilcoxon 符号秩检验
            [p1, ~, ~] = signrank(data1, data2, 'alpha', 0.05);
            if p1 < 0.05
                if mean1 < mean2
                    significance1 = '+';
                    better_1=better_1+1;
                else
                    significance1 = '-';
                    worse_1=worse_1+1;
                end
            else
                significance1 = '≈';
                similar_1=similar_1+1;
            end

            [p2, ~, ~] = signrank(data1, data3, 'alpha', 0.05);
            if p2 < 0.05
                if mean1 < mean3
                    significance2 = '+';
                    better_2=better_2+1;
                else
                    significance2 = '-';
                    worse_2=worse_2+1;
                end
            else
                significance2 = '≈';
                similar_2=similar_2+1;
            end
            
            [p3, ~, ~] = signrank(data1, data4, 'alpha', 0.05);
            if p3 < 0.05
                if mean1 < mean4
                    significance3 = '+';
                    better_3=better_3+1;
                else
                    significance3 = '-';
                    worse_3=worse_3+1;
                end
            else
                significance3 = '≈';
                similar_3=similar_3+1;
            end
            
            [p4, ~, ~] = signrank(data1, data5, 'alpha', 0.05);
            if p4 < 0.05
                if mean1 < mean5
                    significance4 = '+';
                    better_4=better_4+1;
                else
                    significance4 = '-';
                    worse_4=worse_4+1;
                end
            else
                significance4 = '≈';
                similar_4=similar_4+1;
            end
            
            [p5, ~, ~] = signrank(data1, data6, 'alpha', 0.05);
            if p5 < 0.05
                if mean1 < mean6
                    significance5 = '+';
                    better_5=better_5+1;
                else
                    significance5 = '-';
                    worse_5=worse_5+1;
                end
            else
                significance5 = '≈';
                similar_5=similar_5+1;
            end

%             % 写入 Excel 表格
%             writecell({['F', funcPrefix1]}, excelFile, 'Sheet', 1, 'Range', sprintf('A%d', row));
%             
%             % 写入 ALC_MAPSO 数据
%             writecell({sprintf('%.2E ± %.2E', mean1, std1)}, excelFile, 'Sheet', 1, 'Range', sprintf('B%d', row));
% 
%             % 写入显著性结果
%             writecell({significance1}, excelFile, 'Sheet', 1, 'Range', sprintf('C%d', row));
% 
%             % 写入 ALCPSO 数据
%             writecell({sprintf('%.2E ± %.2E', mean2, std2)}, excelFile, 'Sheet', 1, 'Range', sprintf('D%d', row));
%             
%             % 写入显著性结果
%             writecell({significance2}, excelFile, 'Sheet', 1, 'Range', sprintf('E%d', row));
% 
%             % 写入 APSO 数据
%             writecell({sprintf('%.2E ± %.2E', mean3, std3)}, excelFile, 'Sheet', 1, 'Range', sprintf('F%d', row));
%             
%             % 写入显著性结果
%             writecell({significance3}, excelFile, 'Sheet', 1, 'Range', sprintf('G%d', row));
% 
%             % 写入 MFCPSO 数据
%             writecell({sprintf('%.2E ± %.2E', mean4, std4)}, excelFile, 'Sheet', 1, 'Range', sprintf('H%d', row));
% 
%             % 写入显著性结果
%             writecell({significance4}, excelFile, 'Sheet', 1, 'Range', sprintf('I%d', row));
% 
%             % 写入 TAPSO 数据
%             writecell({sprintf('%.2E ± %.2E', mean5, std5)}, excelFile, 'Sheet', 1, 'Range', sprintf('J%d', row));
% 
%             % 写入显著性结果
%             writecell({significance5}, excelFile, 'Sheet', 1, 'Range', sprintf('K%d', row));
% 
%             % 写入 AWPSO 数据
%             writecell({sprintf('%.2E ± %.2E', mean6, std6)}, excelFile, 'Sheet', 1, 'Range', sprintf('L%d', row));
% 
                        % 写入 Excel 表格
            writecell({['F', funcPrefix1]}, excelFile, 'Sheet', 1, 'Range', sprintf('A%d', row));
            
            writecell({sprintf('%.2E±%.2E', mean1, std1)}, excelFile, 'Sheet', 1, 'Range', sprintf('B%d', row));

            writecell({[sprintf('%.2E±%.2E (', mean2, std2),significance1,')']}, excelFile, 'Sheet', 1, 'Range', sprintf('C%d', row));
            writecell({[sprintf('%.2E±%.2E (', mean3, std3),significance2,')']}, excelFile, 'Sheet', 1, 'Range', sprintf('D%d', row));
            writecell({[sprintf('%.2E±%.2E (', mean4, std4),significance3,')']}, excelFile, 'Sheet', 1, 'Range', sprintf('E%d', row));
             writecell({[sprintf('%.2E±%.2E (', mean5, std5),significance4,')']}, excelFile, 'Sheet', 1, 'Range', sprintf('F%d', row));
              writecell({[sprintf('%.2E±%.2E (', mean6, std6),significance5,')']}, excelFile, 'Sheet', 1, 'Range', sprintf('G%d', row));
            



            % 更新行数，为下一个函数准备
            row = row + 1;
        end
    end
    writecell({[num2str(better_1),'/',num2str(similar_1),'/',num2str(worse_1)]}, excelFile, 'Sheet', 1, 'Range', sprintf('C%d', row));
    writecell({[num2str(better_2),'/',num2str(similar_2),'/',num2str(worse_2)]}, excelFile, 'Sheet', 1, 'Range', sprintf('D%d', row));
    writecell({[num2str(better_3),'/',num2str(similar_3),'/',num2str(worse_3)]}, excelFile, 'Sheet', 1, 'Range', sprintf('E%d', row));
    writecell({[num2str(better_4),'/',num2str(similar_4),'/',num2str(worse_4)]}, excelFile, 'Sheet', 1, 'Range', sprintf('F%d', row));
    writecell({[num2str(better_5),'/',num2str(similar_5),'/',num2str(worse_5)]}, excelFile, 'Sheet', 1, 'Range', sprintf('G%d', row));

end
