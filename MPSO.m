close all;
clear all;
%% 
NP=30;
Dim=30;
T=10000;
max_FEs=300000;
c1=2*ones(NP,1);
c2=2*ones(NP,1);
Wmax=0.9;
Wmin=0.4;
for h=15:30
Function_name=h;
[lb,ub,Dim,fun] = Get_Functions_cec2014(Function_name, Dim);
Xmax=ub(1);
Xmin=lb(1);
Vmax=0.2*(Xmax-Xmin);
Vmin=-Vmax;
eposide=30;
average=0;
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
FEs=0;
g=0;
w=0.4;
while FEs<max_FEs
    %%update w
    v=w.*v+((c1*ones(1,Dim)).*rand(NP,Dim)).*(pbest-x)+((c2*ones(1,Dim)).*rand(NP,Dim)).*(ones(NP,1)*Leader-x);
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
    Fit=arrayfun(@(i) fun(x(i,:)),1:NP);
    Fit=Fit';
    FEs=FEs+NP;
    g=g+1;
    logic=(Fit<pbest_fit);
    pbest=(logic*ones(1,Dim)).*x+((ones(NP,1)-logic)*ones(1,Dim)).*pbest;
    pbest_fit=logic.*Fit+(1-logic).*pbest_fit;
    %update gbest
    [gbest_fit,gbest_index]=min(pbest_fit);
    gbest=pbest(gbest_index,:);
    Leader=gbest;
    disp(['第',num2str(h),'个函数第',num2str(g),'代： ',num2str(gbest_fit)]);
    record_gbest_fit(g)=gbest_fit;
end
record(i)=gbest_fit;
average=average+gbest_fit;
fileID1=fopen(['.\MPSO_102\',num2str(Function_name),'_',num2str(eposide),'record_MPSO_102.txt'],'w');
fprintf(fileID1,'%1d \n',record_gbest_fit);
fclose(fileID1);
end
%record
average=average/eposide;
std_2=record-average;
std=sqrt(mean(std_2.^2));
best=min(record);
fileID1=fopen(['.\MPSO_102\',num2str(Function_name),'_',num2str(eposide),'total_MPSO_102.txt'],'w');
fprintf(fileID1,'%1d \n',record);
fprintf(fileID1,'average=%ld \n',average);
fprintf(fileID1,'std=%ld \n',std);
fprintf(fileID1,'best=%ld \n',best);
fclose(fileID1);
end