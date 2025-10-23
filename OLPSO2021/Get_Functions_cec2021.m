%% cec2021

function [lb,ub,dim,fobj] = Get_Functions_cec2021(F,dim)
optimum= [100, 1100 ,700 ,1900 ,1700 ,1600 ,2100 ,2200 ,2400 ,2500];
switch F
    case 1

        lb=-100*ones(1,dim);
        ub=100*ones(1,dim);
        fobj = @(x) cec21_basic_func(x',1); 
        
    case 2

        lb=-100*ones(1,dim);
        ub=100*ones(1,dim);
        fobj = @(x) cec21_basic_func(x',2); 
        
    case 3

        lb=-100*ones(1,dim);
        ub=100*ones(1,dim);
        fobj = @(x) cec21_basic_func(x',3); 
        
        
    case 4
        
        lb=-100*ones(1,dim);
        ub=100*ones(1,dim);
        fobj = @(x) cec21_basic_func(x',4); 
        
    case 5
        
        lb=-100*ones(1,dim);
        ub=100*ones(1,dim);
        fobj = @(x) cec21_basic_func(x',5); 
        
        
    case 6
        
        lb=-100*ones(1,dim);
        ub=100*ones(1,dim);
        fobj = @(x) cec21_basic_func(x',6); 
        
    case 7
        
        lb=-100*ones(1,dim);
        ub=100*ones(1,dim);
        fobj = @(x) cec21_basic_func(x',7); 
        
    case 8
        
        lb=-100*ones(1,dim);
        ub=100*ones(1,dim);
        fobj = @(x) cec21_basic_func(x',8); 
        
    case 9
        
        lb=-100*ones(1,dim);
        ub=100*ones(1,dim);
        fobj = @(x) cec21_basic_func(x',9); 
        
    case 10
        
        lb=-100*ones(1,dim);
        ub=100*ones(1,dim);
        fobj = @(x) cec21_basic_func(x',10); 

end

end
