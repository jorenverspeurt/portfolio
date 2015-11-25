% 
:- dynamic distance_dyn/3.
distance(E1,E2,Dist) :- distance_dyn(E1,E2,Dist),!.
distance(F1,F2,Dist) :-
    combination(F1,F2,Comb),
    F1 \== F2,
    single(F1,S1),
    single(F2,S2),
    Min is min(S1,S2),
    Max is max(S1,S2),
    Dist is (Comb-Min)/Max,
    asserta(distance_dyn(F1,F2,Dist)).
% Distance defined for combinations of F's and cs
distance(F,c(El1,El2),Dist) :-
    distance(F,El1,DFE1),
    distance(F,El2,DFE2),
    % Average linkage
    Dist is (DFE1+DFE2)/2,
    % Single linkage
    %Dist is min(DFE1,DFE2),
    % Complete linkage
    %Dist is max(DFE1,DFE2).
    %
    asserta(distance_dyn(F,c(El1,El2),Dist)),
    !.
distance(c(El1,El2),F,Dist) :-
    distance(F,c(El1,El2),Dist),!.
distance(c(El1,El1),c(El3,El4),Dist) :-
    distance(El1,c(El3,El4),Dist1),
    distance(El2,c(El3,El4),Dist2),
    distance(El3,c(El1,El2),Dist3),
    distance(El4,c(El1,El2),Dist4),
    Dist is (Dist1+Dist2+Dist3+Dist4)/4,
    %DistA is min(Dist1,Dist2), DistB is min(Dist3,Dist4), Dist is min(DistA,DistB),
    %DistA is max(Dist1,Dist2), DistB is max(Dist3,Dist4), Dist is max(DistA,DistB),
    %
    asserta(distance_dyn(c(El1,El2),c(El3,El4))).

averagedistance(AD) :-
    findall(D,distance(_F1,_F2,D),Distances),
    sum_list(Distances,Sum),
    length(Distances,Length),
    AD is Sum/Length.

% If the number of elements in the Input accumulator is equal to
% Number (the wanted number of clusters in our hierarchical clustering
% of the inputs) then the Input is clustered so it is equal to
% the wanted Fcs structure.
clustered(Fcs,Fcs,Number) :-
    length(Fcs,N),
    N=<Number.
% Fcs will be unified to a list consisting of elements that
% are either F's or clusters with a length equal to Number.
% The initial input should be the full list of F's.
% This Input then acts as a sort of reverse accumulator 
% (it decreases in size every step)
clustered(Fcs,Input,Number) :-
    length(Input,I),
    I>=Number,
    findall(Dist-El1-El2
        ,(member(El1,Input)
        ,member(El2,Input)
        ,El1\==El2
        ,distance(El1,El2,Dist))
        ,Dists),
    min_member(Dist-El1-El2,Dists),
    selectchk(El1,Input,Input2),
    selectchk(El2,Input2,Input3),
    clustered(Fcs,[c(El1,El2)|Input3],Number).

% Calculates the quality of a clustering based on the consistency
% of the last part of the name of the files being clustered
% (last word/part of the band name in the test application)
% Aggregate quality is defined as the average of per-cluster quality
% Per-cluster quality is defined as the amount of files for the 
% majority name divided by the sum of the amount of files for
% the other names. In this way the per-cluster quality is a number
% between 1/(#names) and 1. (TODO: make number between 0 and 1)
quality(Fcs,Names,Quality) :-
    findall(c(A,B),member(c(A,B),Fcs),Clusters),
    findall(NC-Name-Amount
        ,(nth1(NC,Clusters,c(E1,E2))
            ,member(Name,Names)
            ,contains_amount(E1,Name,0,Amount1)
            ,contains_amount(E2,Name,0,Amount2)
            ,Amount is Amount1+Amount2)
        ,Amounts),
    findall(CQuality
        ,(member(NC-_-_,Amounts)
            ,findall(Amount,member(NC-_-Amount,Amounts),AmsForNC)
            ,max_list(AmsForNC,MaxAm)
            ,sum_list(AmsForNC,SumOthers)
            ,CQuality is MaxAm/SumOthers)
        ,QualForNC),
    sum_list(QualForNC,QSum),
    length(QualForNC,QLen),
    Quality is QSum/QLen.

% TODO Write description and test
contains_amount(_-Name,Name,Acc,Amount) :- 
    Amount is Acc+1.
contains_amount(_-OtherName,Name,Acc,Acc) :- 
    OtherName \== Name.
contains_amount(c(A,B),Name,Acc,Amount) :-
    contains_amount(A,Name,Acc,AAmount),
    contains_amount(B,Name,Acc,BAmount),
    Amount is AAmount+BAmount.
