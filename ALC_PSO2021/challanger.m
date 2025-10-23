function [Leader_out,flag,FEs]=challanger(w,c11,c22,Leader,x,v,Xmax,Xmin,D,pro,pbest,N,Function_name,gbest,FEs_in,pbest_fit)
[lb,ub,dim,fobj] = Get_Functions_cec2021(Function_name, D);
%%原始Leader
% v1=w.*v+c11*R1.*(pbest-x)+(c22*R2.*(ones(N,1)*Leader-x));
% x1=x+v1;
% for i=1:N
% x1_fit(i,1)=fobj(x1(i,:));
% end
%%challanger生成
replace=0;
potient=(Xmax-Xmin).*rand(1,D)+Xmin;
%signa=tem_leader(randi(length(Leader)));
rand1=rand(1,D);
logic1=rand1<pro;
%cha=(1-logic1|logic2).*Leader+(logic1-logic1.*logic2).*gbest+logic2.*potient;
count=sum(logic1);
cha=(1-logic1).*Leader+logic1.*potient;
if count==0
    cha(randi(length(Leader)))=rand()*(Xmax(1)-Xmin(1));%这地方如果改了Xmin的格式是要改的
end
for iter=1:2
v2=w.*v+c11*rand(1,D).*(pbest-x)+(c22*rand(1,D).*(ones(N,1)*cha-x));
x2=x+v2;
for i=1:N
x2_fit(i,1)=fobj(x2(i,:));
end
FEs=FEs_in+N;
LOGIC=x2_fit<pbest_fit;
if sum(LOGIC)>0
    replace=1;
    break;
end
end
%disp(['fit1=',num2str(fit1),' fit2=',num2str(fit2)]);
if replace~=1
    Leader_out=Leader;
    flag=2;
else
    %disp('--------------------------------------------------------------------------------------替换成功----------------------------------------------------------------------------------------------');
    Leader_out=cha;
    flag=1;
end
end

