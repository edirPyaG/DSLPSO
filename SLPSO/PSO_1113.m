close all;
clear all;
%% 
upperbound_test=[60,70,100,130,160,200];
for t=1:6
Dim=10;
NP=3*Dim;
Wmax=0.9;
Wmin=0.4;
batch_size_min=5;
batch_size_max=upperbound_test(t);
for h=1:10
Function_name=h;
disp(['第',num2str(h),'个函数, Dim=',num2str(Dim)]);
[lb,ub,Dim,fun] = Get_Functions_cec2021(Function_name, Dim);
max_FEs=10000*NP;
c1=2*ones(NP,1);
c2=2*ones(NP,1);
Xmax=ub(1);
Xmin=lb(1);
Vmax=0.2*(Xmax-Xmin);
Vmin=-Vmax;
eposide=30;
average=0;
record=[];
for m=1:eposide
challenger=zeros(1,Dim);
size_current=1;
for u=1:NP
    for r=1:Dim
        x(u,r)=rand()*(Xmax-Xmin)+Xmin;
        if x(u,r)>Xmax
            x(u,r)=Xmax-(Xmax-Xmin)*0.25*rand;
        elseif x(u,r)<Xmin
            x(u,r)=Xmin+(Xmax-Xmin)*0.25*rand;
        end
        v(u,r)=rand()*(Vmax-Vmin)+Vmin;
        if v(u,r)>Vmax
            v(u,r)=Vmax;
        elseif v(u,r)<Vmin
            v(u,r)=Vmin;
        end
    end
end
Fit=arrayfun(@(i) fun(x(i,:)),1:NP);
[gbest_fit,gbest_index]=min(Fit);
gbest=x(gbest_index,:);
batch=zeros(1,Dim);
batch=gbest;
batch_fit=gbest_fit;
sigma=zeros(1,Dim);
batch_size=batch_size_min;
Leader=gbest;
pbest=x;
pbest_fit=Fit;
FEs=0;
g=0;
w=0.7298;
while FEs<max_FEs
    tic;
    %%update w
    w=Wmax-(Wmax-Wmin)*g/10000;
    for u=1:NP
        for r=1:Dim
            v(u,r)=w*v(u,r)+(c1(u)*rand())*(pbest(u,r)-x(u,r))+(c2(u)*rand()).*(Leader(r)-x(u,r));
            if v(u,r)>Vmax
                v(u,r)=Vmax;
            elseif v(u,r)<Vmin
                v(u,r)=Vmin;
            end
            x(u,r)=x(u,r)+v(u,r);
            if x(u,r)>Xmax
                x(u,r)=Xmax-(Xmax-Xmin)*0.25*rand;
            elseif x(u,r)<Xmin
                x(u,r)=Xmin+(Xmax-Xmin)*0.25*rand;
            end
        end
    Fit(u)=fun(x(u,:));
    FEs=FEs+1;
    if Fit(u)<pbest_fit(u)
        pbest(u,:)=x(u,:);
        pbest_fit(u)=Fit(u);
        if size_current<batch_size
            batch=[batch;x(u,:)];
            batch_fit=[batch_fit;Fit(u)];
            size_current=size_current+1;
        else
            [~,tem_index]=max(batch_fit);
            batch(tem_index,:)=x(u,:);
            batch_fit(tem_index,:)=Fit(u);
        end
    end
    if Fit(u)<gbest_fit
        gbest=x(u,:);
        gbest_index=u;
        gbest_fit=Fit(u);
    end
    end
    %% generate challenger
    mu=mean(batch,1);
    sigma_pre=sigma;
% 计算每列的均值
    mean_values = sum(batch, 1) / size_current;

    % 初始化标准差向量
    sigma = zeros(1, Dim);

    % 计算每列的标准差
    for j = 1:Dim
        % 计算当前列的方差
        variance = sum((batch(:, j) - mean_values(j)).^2) / (size_current - 1);
        % 计算标准差
        sigma(j) = sqrt(variance);
    end
%     for f=1:Dim
%     record_plot_x=linspace(mean_values(f) - 3*sigma(f), mean_values(f) + 3*sigma(f), 1500);
%     record_plot_y(:,f) = (1 / (sigma(f) * sqrt(2 * pi))) * exp(-0.5 * ((record_plot_x - mean_values(f)) / sigma(f)).^2);
%     end
    LOGIC=(sigma<=sigma_pre);
    add_windows=sum(LOGIC);
    limit_windows=Dim-add_windows;
    batch_size=batch_size+add_windows-limit_windows;
    batch_size=min(max(batch_size_min,batch_size),batch_size_max);
    for k=1:Dim
        challenger(k)=normrnd(mu(k), sigma(k),1);
    end
        challenger_fit=fun(challenger);
        if challenger_fit<gbest_fit
            gbest=challenger;
            gbest_fit=challenger_fit;
        end
%     end
    FEs=FEs+1;
    Leader=gbest;
    g=g+1;
    %disp(['第',num2str(g),'代：',num2str(gbest_fit)]);
    record_gbest_fit(g)=gbest_fit;
end
disp(['第',num2str(m),'次, 最优适应值=',num2str(gbest_fit)]);
record(m)=gbest_fit;
average=average+gbest_fit;
if m==1
fileID1=fopen(['.\DRLPSO_CEC2021\Analyze_of_bound\changing_upperbound\',num2str(batch_size_max),'\',num2str(Function_name),'_',num2str(eposide),'_',num2str(Dim),'RECORD_DRLPSO.txt'],'w');
fprintf(fileID1,'%1d \n',record_gbest_fit);
fclose(fileID1);
end
end
average=average/eposide;
disp(num2str(average));
std_2=record-average;
std=sqrt(mean(std_2.^2));
best=min(record);
fileID1=fopen(['.\DRLPSO_CEC2021\Analyze_of_bound\changing_upperbound\',num2str(batch_size_max),'\',num2str(Function_name),'_',num2str(eposide),'_',num2str(Dim),'total_DRLPSO.txt'],'w');
fprintf(fileID1,'%1d \n',record);
fprintf(fileID1,'average=%ld \n',average);
fprintf(fileID1,'std=%ld \n',std);
fprintf(fileID1,'best=%ld \n',best);
fclose(fileID1);
end
end