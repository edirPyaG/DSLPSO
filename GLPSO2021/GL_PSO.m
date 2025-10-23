close all;
clear all;
%% 
Dim_test=[10,20];
for p=1:2
Dim=Dim_test(p);
NP=3*Dim;
T=10000;
max_FEs=10000*Dim;
% c1=2*ones(NP,1);
% c2=2*ones(NP,1);
c=1.49618;
pm=0.01;
sg=7;
for h=1:10
Function_name=h;
disp(['第',num2str(h),'个函数, Dim=',num2str(Dim)]);
[lb,ub,Dim,fun] = Get_Functions_cec2021(Function_name, Dim);
Xmax=ub(1);
Xmin=lb(1);
Vmax=0.2*(Xmax-Xmin);
Vmin=-Vmax;
eposide=30;
average=0;
for m=1:eposide
%%Initialization
x=rand(NP,Dim).*(Xmax-Xmin)+Xmin*ones(NP,Dim);
v=rand(NP,Dim).*(Vmax-Vmin)+Vmin*ones(NP,Dim);
Fit=arrayfun(@(i) fun(x(i,:)),1:NP);
Fit=Fit';
[gbest_fit,gbest_index]=min(Fit);
gbest=x(gbest_index,:);
Leader=gbest;
pbest=x;
Ei=x;
pbest_fit=Fit;
FEs=0;
g=0;
w=0.7298;
stagnationcounter=zeros(NP,1);
%%Main loop
while FEs<max_FEs
    for i=1:NP
        %crossover
        for d=1:Dim
            if Fit(i)<Fit(gbest_index)
                Oi(d)=rand*x(i,d)+(1-rand)*gbest(d);
            else
                Oi(d)=x(randi(NP),d);
            end
        end
        
        %Mutation
        for d=1:Dim
            if rand<pm
                Oi(d)=rand*(Xmax-Xmin)+lb(1);
            end
        end
        %selection
        Oi_Fit=fun(Oi);
        Ei_Fit=fun(Ei(i,:));
        FEs=FEs+2;
        if Oi_Fit<Ei_Fit
            Ei(i,:)=Oi;
            stagnationcounter(i)=0;
        else
            stagnationcounter(i)=stagnationcounter(i)+1;
        end
        
        if stagnationcounter(i)>sg
            tournamesize=max(1,round(0.2*NP));
            candidates=randperm(NP,tournamesize);
            Fit_Ei=arrayfun(@(i) fun(Ei(i,:)),1:NP);
            FEs=FEs+NP;
            Fit_candidates=Fit_Ei(candidates);
            [~,bestIdx]=min(Fit_candidates);
            Ei(i,:)=Ei(candidates(bestIdx),:);
            stagnationcounter(i)=0;
        end
    end
    logic=Ei>Xmax;
    Ei=logic.*Xmax+(1-logic).*Ei;
    logic=Ei<Xmin;
    Ei=logic.*Xmin+(1-logic).*Ei;
    %%particle update
    v=w*v+c*rand(NP,Dim).*(Ei-x);
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
    %disp(['第',num2str(h),'个函数第',num2str(g),'代： ',num2str(gbest_fit)]);
    record_gbest_fit(g)=gbest_fit;
end
disp(['第',num2str(m),'次, 最优适应值=',num2str(gbest_fit)]);
record(m)=gbest_fit;
average=average+gbest_fit;
if m==1
fileID1=fopen(['.\GLPSO2021\',num2str(Dim),'\',num2str(Function_name),'_',num2str(eposide),'RECORD_GLPSO.txt'],'w');
fprintf(fileID1,'%1d \n',record_gbest_fit);
fclose(fileID1);
end
end
average=average/eposide;
std_2=record-average;
std=sqrt(mean(std_2.^2));
best=min(record);
fileID1=fopen(['.\GLPSO2021\',num2str(Dim),'\',num2str(Function_name),'_',num2str(eposide),'total_GLPSO.txt'],'w');
fprintf(fileID1,'%1d \n',record);
fprintf(fileID1,'average=%ld \n',average);
fprintf(fileID1,'std=%ld \n',std);
fprintf(fileID1,'best=%ld \n',best);
fclose(fileID1);
end
end