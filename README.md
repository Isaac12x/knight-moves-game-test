# Tech test

## Instructions

To run please use python3.8 or above. 

Run by `python main.py`

And when in the game type any key followed by typing `responses` to see the output you're looking for.

I have left development notes in the relevant methods for you to check with the common NOTE: format.

DISCLAIMER: The code presented here is not the cleanliest nor the one I would have presented if more time (see improvements below if you're interested in what things I would have done differently), however because of the nature of this test I need to set for good enough at this stage.




## Development notes 
### Read through
The tasks will be similar for what it would be a CLI-based chess game. Each letter and number in the board should be treated as unique and associated to an index. 
The board has a gist compared to a normal chess board where the last row (4th row) misses two squares in each end of the game board.
 
Rationale: 
This task will need a gameloop always running
That loop will contain prompt for the user to type in a letter (and only 1 letter.)
 
 
### Development
The way I will tackle this is: 
a) make a quick prototype of the code and see  if that's what we're after. 

To distinguish a good vs bad move in pros of having things looking a bit tidier, I will color code errors in red and 
anything you throw in green
   1. The first task will be to encode the gameboard so we have a reference.
   2. The next bit will be to add the piece and what movements can it do, so we have the actions.
   3. Finally, create the rules so actions are constrained and gameplay, so there is a core loop running once you run the file..

b) (here) the next task will be to refine data structures, refactor into classes (Piece, Board, Rules, Gameplay) and simplify the code very much.
c) type annotate the functions once we know they are final, write bdd tests.

### Notes
* Messaging all in once place instead of scattered around. I prefer it in this way because it's easier to see all the messaging in one place. People in charge of copy or legal, etc. can review it and see at a glance if something should be removed/added or changed.

* Dict instead of list of lists (nested) for the game indexes. This is done because in case of making the game bigger and bigger a dictionary is easier then to work with and the time to access an index is always O(n). Not that it matters at this level but if we were to make a board of rows = 2031231231 and columns = 231232013020023321231231. Not sure how fun the game would be but... It will start being relevant.

* I have never coded any game, nor chess game and did this without looking at how it's done in other chess games. In a normal environment I would do that after I have a sense of what needs doing.

### Improvements
If I had more time, the next thing I would do is (b) and (c) in the Development section.
Make a coordinate system also include the column and row instead of only using the index position: "0-0" 
Implement a tree structure and a reverse lookup for all dicts.
