A couple of things I've written in Python (both 2 and 3)

---

#generateComps.py 
This is a helper script I wrote for a Software Architecture assignment. It processes a couple of lists and dictionaries containing information about components of the system we were designing. In this way I could make a kind of DSL for generating LaTeX code with the descriptions. It has a couple of interesting features. For example it's possible to have methods shared among interfaces and interfaces shared among components, but refer to the right interface or component in the description text. Objects that stand for methods that are available in multiple interfaces which are then offered by multiple components add themselves are also automatically added to the right parents and "cousins" (it doesn't work in all cases, I don't really have time to explain it properly here but please believe me when I say it's a complicated problem)
Some things are also named automatically (for example: parameter names have sane defaults, if the type of a parameter is `Tuple<BatchID,List<JobID>>` then the default name for it is `batchIDAndJobIDs`) and it's possible to "refactor" certain names after the fact with a simple method call (it's a bit overkill but it was relatively simple to add)
Something that was required by the assignment and would have been a real pain otherwise is the fact that when referring to another component or method the name of the referred item should be a PDF hyperlink to the description of that item. This was rather easy to add to the code.
The code throws an error when it tries to generate LaTeX for an incomplete element. This was handy because it made sure all of the descriptions were complete.
The next step would be to make the code read an actual DSL that's even less hassle to write than the current hardcoded structure and perform more interesting checks on the object structure.

#tusker
This is a little CLI ToDo-application that I wrote in Python3 for fun. I challenged myself to write it in a style that was as much like code you would see in a functional language like Haskell. I don't think I succeeded 100% but it's close. 
It operates on a file located at `~/.tusker.json` where it stores a JSON representation of a set of projects which can have deadlines, notes and tasks. Tasks in turn can have a description, a deadline, a priority, time spent on that task, ...
The time spent on a project is the sum spent on its subtasks, etc.
It's far from feature-complete and probably quite buggy but a lot of functions already work, feel free to try it out.
I was planning on completing it and giving it a Synapse-like GUI but there's really no point, I guess.

#ExperimentResultViz 
This folder contains a script that takes a JSON file with a specific format and outputs a bar chart. It's something simple and it's only an edit of something someone else wrote but it's served me for a couple of assignments, so I thought I might as well include it.
The JSON file accompanying it renders into the png that's also there.

