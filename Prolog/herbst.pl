% Herbstluftwm frame layout dump parser

:- set_prolog_flag(debugger_write_options,[quoted(true), portray(true), max_depth(10), attributes(portray), max_depth(3)]).

layout(split(O,R,S,A,B)) --> split_(O,R,S,A,B).
layout(clients(O,S,C)) --> clients_(O,S,C).

clients_(Orientation,Selection,Clients) --> "(clients "
                                           ,( hv(Orientation)
                                            ; m(Orientation)
                                            )
                                           ,":"
                                           ,num(Selection)
                                           ,space(star)
                                           ,(
                                                windowIDs(Clients)
                                              , space(star)
                                              , ")"
                                            ;
                                                ")", { Clients = [] }
                                            ).
% Dit zit eigenlijk ook in :- use_module(library(dcg_basics))
% http://www.swi-prolog.org/pldoc/doc/swi/library/dcg/basics.pl
space(plus) --> " ", space(star).
space(star) --> ( " " -> space(star) ; "" ).
hv(horizontal) --> "horizontal".
hv(vertical) --> "vertical".
hv(error) --> \+ ("horizontal" ; "vertical" ; "max").
m(max) --> "max".
m(error) --> \+ "max".
windowIDs([H|T]) --> "0x", untilclose(H), space(plus), windowIDs(T).
windowIDs([H]) --> "0x", untilclose(H).
% Maybe do this on code_type ?
untilclose([]), ")" --> ")", !.
untilclose([]), " " --> " ", !.
untilclose([H|T]) --> [H], untilclose(T).

num(Num) --> digits(NumStr)
            ,{
                number_codes(Num,NumStr)
             }.
% Early stopping, not really necessary
digits([]), [C] --> [C], { \+ code_type(C,period) , \+ code_type(C,digit) }.
digits([H|T]) --> [H]
                 ,{(
                    code_type(H,digit)
                  ;
                    code_type(H,period)
                  )}
                 ,digits(T).

split_(Orientation,Ratio,Select,L,R) --> "(split "
                                        ,hv(Orientation)
                                        ,":"
                                        ,num(Ratio)
                                        ,":"
                                        ,num(Select)
                                        ," "
                                        ,layout(L)
                                        ," "
                                        ,layout(R)
                                        ,")".
