% Calculate results for 4 types of compression (Gzip, Lr2, Lr9, Zpaq)
main :-
    consult(distance),
    tell(scriptoutput),
    main1,
    main2,
    main3,
    main4,
    told.

% Calculate results for tar.gzs
main1 :-
    consult(testSingleTar),
    consult(testCorrTar),
    findall(F,single(F,_),Fs1),append(FShort1,_,Fs1),length(FShort1, 20),time(clustered(Fcs11,FShort1,4)),!,writeln(Fcs11),findall(Name,(member(_-Name,FShort1),\+ Name=_-_),Names1),quality(Fcs11,Names1,Quality1),writeln(Quality1),
    findall(F,single(F,_),Fs2),append(FShort2,_,Fs2),length(FShort2, 30),time(clustered(Fcs2,FShort2,4)),!,writeln(Fcs2),findall(Name,(member(_-Name,FShort2),\+ Name=_-_),Names2),quality(Fcs2,Names2,Quality2),writeln(Quality2),
    findall(F,single(F,_),Fs3),append(FShort3,_,Fs3),length(FShort3, 40),time(clustered(Fcs3,FShort3,4)),!,writeln(Fcs3),findall(Name,(member(_-Name,FShort3),\+ Name=_-_),Names3),quality(Fcs3,Names3,Quality3),writeln(Quality3),
    findall(F,single(F,_),Fs4),append(FShort4,_,Fs4),length(FShort4, 50),time(clustered(Fcs4,FShort4,4)),!,writeln(Fcs4),findall(Name,(member(_-Name,FShort4),\+ Name=_-_),Names4),quality(Fcs4,Names4,Quality4),writeln(Quality4),
    % Save memory...
    unload_file(testSingleTar),
    unload_file(testCorrTar),
    retractall(distance_dyn(_,_,_)).
    
% Calculate results for Lr2
main2 :-
    consult(testSingleLr2),
    consult(testCorrLr2),
    findall(F,single(F,_),Fs1),append(FShort5,_,Fs1),length(FShort5, 20),time(clustered(Fcs1,FShort5,4)),!,writeln(Fcs1),findall(Name,(member(_-Name,FShort5),\+ Name=_-_),Names1),quality(Fcs1,Names1,Quality1),writeln(Quality1),
    findall(F,single(F,_),Fs2),append(FShort6,_,Fs2),length(FShort6, 30),time(clustered(Fcs2,FShort6,4)),!,writeln(Fcs2),findall(Name,(member(_-Name,FShort6),\+ Name=_-_),Names2),quality(Fcs2,Names2,Quality2),writeln(Quality2),
    findall(F,single(F,_),Fs3),append(FShort7,_,Fs3),length(FShort7, 40),time(clustered(Fcs3,FShort7,4)),!,writeln(Fcs3),findall(Name,(member(_-Name,FShort7),\+ Name=_-_),Names3),quality(Fcs3,Names3,Quality3),writeln(Quality3),
    findall(F,single(F,_),Fs4),append(FShort8,_,Fs4),length(FShort8, 50),time(clustered(Fcs4,FShort8,4)),!,writeln(Fcs4),findall(Name,(member(_-Name,FShort8),\+ Name=_-_),Names4),quality(Fcs4,Names4,Quality4),writeln(Quality4),
    % Save memory...
    unload_file(testSingleLr2),
    unload_file(testCorrLr2),
    retractall(distance_dyn(_,_,_)).

% Calculate results for Lr9
main3 :-
    consult(testSingleLr9),
    consult(testCorrLr9),
    findall(F,single(F,_),Fs1),append(FShort9,_,Fs1),length(FShort9, 20),time(clustered(Fcs1,FShort9,4)),!,writeln(Fcs1),findall(Name,(member(_-Name,FShort9),\+ Name=_-_),Names1),quality(Fcs1,Names1,Quality1),writeln(Quality1),
    findall(F,single(F,_),Fs2),append(FShort10,_,Fs2),length(FShort10, 30),time(clustered(Fcs2,FShort10,4)),!,writeln(Fcs2),findall(Name,(member(_-Name,FShort10),\+ Name=_-_),Names2),quality(Fcs2,Names2,Quality2),writeln(Quality2),
    findall(F,single(F,_),Fs3),append(FShort11,_,Fs3),length(FShort11, 40),time(clustered(Fcs3,FShort11,4)),!,writeln(Fcs3),findall(Name,(member(_-Name,FShort11),\+ Name=_-_),Names3),quality(Fcs3,Names3,Quality3),writeln(Quality3),
    findall(F,single(F,_),Fs4),append(FShort12,_,Fs4),length(FShort12, 50),time(clustered(Fcs4,FShort12,4)),!,writeln(Fcs4),findall(Name,(member(_-Name,FShort12),\+ Name=_-_),Names4),quality(Fcs4,Names4,Quality4),writeln(Quality4),
    unload_file(testSingleLr9),
    unload_file(testCorrLr9),
    retractall(distance_dyn(_,_,_)).

% Calculate results for Lr9
main4 :-
    consult(testSingleZpaq),
    consult(testCorrZpaq),
    findall(F,single(F,_),Fs1),append(FShort13,_,Fs1),length(FShort13, 20),time(clustered(Fcs1,FShort13,4)),!,writeln(Fcs1),findall(Name,(member(_-Name,FShort13),\+ Name=_-_),Names1),quality(Fcs1,Names1,Quality1),writeln(Quality1),
    findall(F,single(F,_),Fs2),append(FShort14,_,Fs2),length(FShort14, 30),time(clustered(Fcs2,FShort14,4)),!,writeln(Fcs2),findall(Name,(member(_-Name,FShort14),\+ Name=_-_),Names2),quality(Fcs2,Names2,Quality2),writeln(Quality2),
    findall(F,single(F,_),Fs3),append(FShort15,_,Fs3),length(FShort15, 40),time(clustered(Fcs3,FShort15,4)),!,writeln(Fcs3),findall(Name,(member(_-Name,FShort15),\+ Name=_-_),Names3),quality(Fcs3,Names3,Quality3),writeln(Quality3),
    findall(F,single(F,_),Fs4),append(FShort16,_,Fs4),length(FShort16, 50),time(clustered(Fcs4,FShort16,4)),!,writeln(Fcs4),findall(Name,(member(_-Name,FShort16),\+ Name=_-_),Names4),quality(Fcs4,Names4,Quality4),writeln(Quality4),
    % Save memory...
    unload_file(testSingleZpaq),
    unload_file(testCorrZpaq),
    retractall(distance_dyn(_,_,_)).
