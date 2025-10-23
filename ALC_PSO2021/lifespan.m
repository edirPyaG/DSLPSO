function [zeta_pbest_fit,thrd,zeta_Leader]=lifespan(Leader,pbest_fit,pbest_fit_pre,Leader_fit_pre,th,fun,gbest,gbest_pre)
    thrd=th;
    %%pbest_fit的余弦相似度
    zeta_pbest_fit=sum(pbest_fit-pbest_fit_pre);
    zeta_Leader=fun(Leader)-Leader_fit_pre;
    zeta_gbest=fun(gbest)-fun(gbest_pre);
    if zeta_gbest<0
        thrd=th+2;
    else
        if zeta_pbest_fit<0
            thrd=th+1;
        else
            if zeta_Leader<0
                thrd=th;
            else
                thrd=th-1;
            end
        end
    end
 end

