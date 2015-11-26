#abc.hs
This is an implementation of an Artificial Bee Colony optimization algorithm for the Maximally Diverse Grouping Problem that I developed with github.com/toonn. We basically picked Haskell because we both like functional programming, but admittedly we didn't know nearly enough about Haskell to do the assignment properly, even after we finished. Haskell is also not the ideal language to do it in, which we learned the hard way. It involves a lot of randomness (which can be... painful... in Haskell), was originally written with a bunch of (global) state and most irritatingly required a fixed execution time, usually guaranteed by killing the thread executing the calculations. Not that this last feature is impossible to implement in Haskell, it just doesn't work at all as expected. The thing is that the only thing that's stopped is the symbolic calculation, after which the actual calculation still needed to be executed. So we'd stop the symbolic calculation after a couple of seconds, but the actual computation would run for hours after that (an unpredictable number of hours even).
Had we been more comfortable with monads and a couple of other more advanced Haskell features at the time we wrote this a bunch of things would be a lot better implemented. We also probably could have made a bunch of performance improvements, but we didn't have time for that.

#htrace.hs
A fork of something I found on the internet while studying for my Graphics course. Most of the code is still original but I changed a couple of things that I thought were really weird and added a couple of things to make it look more like the raytracer we saw in the book. I think it should work, I haven't tried.

#hammersley.hs
A quick script to graph Hammersley points (look it up!). Nothing fancy.
