close all;
clear all;
%% 

Dim_test=[10,20];
for p=1:2
    Dim=Dim_test(p);
    NP=20;
    max_FEs=200000;
    c1=2*ones(NP,1);
    c2=2*ones(NP,1);
    w=0.4;
for h=1:10
Function_name=h;
disp(['第',num2str(h),'个函数, Dim=',num2str(Dim)]);
[lb,ub,Dim,fun] = Get_Functions_cec2021(Function_name, Dim);
Xmax=ub(1);
Xmin=lb(1);
Vmax=0.5*(Xmax-Xmin);
Vmin=-Vmax;
eposide=30;
average=0;
th0=60;
th=th0;
pro=1/Dim;
FEs=0;
g=0;
maxg=10000;
Wmax=0.9;
Wmin=0.4;
for i=1:eposide
x=rand(NP,Dim).*(Xmax-Xmin)+Xmin*ones(NP,Dim);
v=rand(NP,Dim).*(Vmax-Vmin)+Vmin*ones(NP,Dim);
Fit=arrayfun(@(i) fun(x(i,:)),1:NP);
Fit=Fit';
[gbest_fit,gbest_index]=min(Fit);
gbest=x(gbest_index,:);
Leader=gbest;
pbest=x;
pbest_fit=Fit;
pbest_fit_pre=Fit;
Leader_pre=Leader;
pbest_pre=pbest;
gbest_pre=gbest;
theta=0;
th=th0;
k=0;
w=0.4;
TT=0;
T=2;
while FEs<max_FEs
    %%adjust c1、c2
    %%update w
    v=w*v+((c1.*rand(NP,1))*ones(1,Dim)).*(pbest-x)+((c2.*rand(NP,1))*ones(1,Dim)).*(ones(NP,1)*Leader-x);
    %%bound
    logic=v>Vmax;
    v=logic.*Vmax+(1-logic).*v;
    logic=v<Vmin;
    v=logic.*Vmin+(1-logic).*v;
    x=x+v;
    logic=x>Xmax;
    x=logic.*(Xmax*ones(NP,Dim)-(Xmax-Xmin)*0.25*rand(NP,Dim))+(1-logic).*x;
    logic=x<Xmin;
    x=logic.*(Xmin*ones(NP,Dim)+(Xmax-Xmin)*0.25*rand(NP,Dim))+(1-logic).*x;
    pbest_fit_pre=Fit;
    Fit=arrayfun(@(i) fun(x(i,:)),1:NP);
    FEs=FEs+NP;
    g=g+1;
    Fit=Fit';
    logic=(Fit<pbest_fit);
    pbest_pre=pbest;
    pbest=(logic*ones(1,Dim)).*x+((ones(NP,1)-logic)*ones(1,Dim)).*pbest;
    pbest_fit=logic.*Fit+(1-logic).*pbest_fit;
    %update gbest
    gbest_pre=gbest;
    [gbest_fit,gbest_index]=min(pbest_fit);
    gbest=pbest(gbest_index,:);
    
    if fun(Leader)>fun(gbest)
        Leader=gbest;
    end
    [zeta_pbest_fit,th,zeta_Leader]=lifespan(Leader,pbest_fit,pbest_fit_pre,fun(Leader_pre),th,fun,gbest,gbest_pre);
    theta=theta+1;
    if theta>=th%challenger
        %disp('-------------------------------------------open------------------------------------');
        [Leader,flag,FEs]=challanger(w,c1,c2,Leader,x,v,Xmax,Xmin,Dim,pro,pbest,NP,Function_name,gbest,FEs,pbest_fit);
        if flag==2
            theta=th-1;
            flag=0;
        elseif flag==1
            theta=0;
            th=th0;
            flag=0;
        end
    end
    Leader_pre=Leader;
    record_gbest_fit(g)=gbest_fit;
    record_th(g)=th;
end
%save('record_plot.mat', 'record_plot');
plot(record_th);
disp(['第',num2str(i),'次, 最优适应值=',num2str(gbest_fit)]);
record(i)=gbest_fit;
average=average+gbest_fit;
if i==1
fileID1=fopen(['.\ALCPSO2021\',num2str(Dim),'\',num2str(Function_name),'_',num2str(eposide),'record_ALC_PSO.txt'],'w');
fprintf(fileID1,'%1d \n',record_gbest_fit);
fclose(fileID1);
end
end
%record
average=average/eposide;
std_2=record-average;
std=sqrt(mean(std_2.^2));
best=min(record);
fileID1=fopen(['.\ALCPSO2021\',num2str(Dim),'\',num2str(Function_name),'_',num2str(eposide),'total_ALC_PSO.txt'],'w');
fprintf(fileID1,'%1d \n',record);
fprintf(fileID1,'average=%ld \n',average);
fprintf(fileID1,'std=%ld \n',std);
fprintf(fileID1,'best=%ld \n',best);
fclose(fileID1);
end
end