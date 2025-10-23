function [Po,FEs_out] = generate_Po(pbest,gbest,NP,Dim,fun,FEs_in)
    %第一步，正交表生成
    M=2^ceil(log2(Dim+1));%确定实验组合数
    OLarray=generate_OLarray(M,Dim);
    %第二步，测试解生成
    Xj=zeros(M,Dim);

    for i = 1:NP
        % Step 2: 生成多个测试解
        Xj = zeros(M, Dim);  % 用于存储每个测试解
        for j = 1:M
            for d = 1:Dim
                if OLarray(j, d) == 1
                    Xj(j, d) = pbest(i, d);  % 从该粒子的 Pbest 选择
                else
                    Xj(j, d) = gbest(d);     % 从 Gbest 选择
                end
            end
        end
    end
    Fit_Xj=arrayfun(@(i) fun(Xj(i,:)),1:M);
    Fit_Xj=Fit_Xj';
    FEs_out=FEs_in+NP;
    [~,best_idx]=min(Fit_Xj);
    Xb=Xj(best_idx,:);
    %第三步，确认分析最佳维度
    best_level=zeros(1,Dim);
    
    for d=1:Dim
        %tem=mean(Fit_Xj(OLarray(:,d)==2));
        level1_effect=mean(Fit_Xj(OLarray(:,d)==1));
        level2_effect=mean(Fit_Xj(OLarray(:,d)==2));
        if level1_effect<level2_effect
            best_level(d)=1;
        else
            best_level(d)=2;
        end
    end
    %第四步，构建预测解Po
    logic1=(best_level==1);
    logic2=(best_level==2);
    logic1=ones(NP,1)*logic1;
    logic2=ones(NP,1)*logic2;
    Po=logic1.*pbest+logic2.*(ones(NP,1)*gbest);
end

function orthogonal_array = generate_OLarray(M, Dim)
    % 生成一个 M 行 Dim 列的正交表，元素为 1 或 2
    orthogonal_array = zeros(M, Dim);
    for i = 1:M
        for j = 1:Dim
            % 使用二进制数模式生成 1 或 2 的交替组合
            orthogonal_array(i, j) = mod(floor((i-1)/(2^(j-1))), 2) + 1;
        end
    end
end