# CISC-121-Final-Project-Binary-Search
CISC 121 W26 final project submission. Program is a binary search educational programed with a mystery game theme.

# Abstraction
Algorithm Name: Spooky Mystery Solver

Spooky mystery solver is an educational game that enables the user to learn about the python binary search method in a fun and interactive manner. The user attempts to find a villain among a list of 16 masked suspects using binary search in less than four guesses, the system suggests the optimal guess following the binary search process.

# Design
The layout of the game predominantly includes the centre game box, where the user can click "New Mystery" to generate a new scenario, or restart the game. The interface includes a visualizaiton of the current list range (with X's denoting the suspects that have been eliminated) the user can input their numbered guess into a text box, and click "Investigate" to make their guess. Clues and system feedback come through the right-side panel called "Investigation Log" and in the box above the list visualization. At the bottom of the app lie two drop-downs: (1) a full description of the binary search algorithm for further education, (2) disclaimer.

# Demo Video and Testing
To access demo video and testing cases please use this google drive link, as github presented issues uploading the images and videos directly to the README:
https://drive.google.com/drive/folders/1wXplrGy3IqoipRPY9r43XfmsE-PjaXEn?usp=sharing

# Problem Breakdown and Computational Thinking

Why Binary Search?

Binary search is one of the most efficient searching algorithms. Instead of checking every suspect one by one (linear search, O(n)), binary search cuts the search space in half with every guess, solving the problem in O(log n) time. The mystery/detective theme makes this concept intuitive: you're narrowing down suspects, eliminating half the lineup each round until only the villain remains. Binary search was chosen for this project as the author did not initially fully understand the binary search algorithm when learning it in the CISC 121 course, and educated themselves further in order to fully understand it. The author believes than a fun and interactive way to learn binary search will prove beneficial to future learners in the CISC 121 course, and young code learners.

The Four Pillars of Computational Thinking

Decomposition:
(1) generate a lineup of 16 suspects
(2) randomly hide a villain at a position within the list
(3) accept the player's guess
(4) compare the guess to the villain's position
(5) narrow the search range by updating low/high bounds
(6) check win/loss conditions
(7) display results visually with HTML cards

Pattern Recognition: 
Every game round the user initiates follows the same pattern: guess the middle, compare, eliminate half. This halving pattern is the fundamental process of the binary search method in python

Abstraction: 
The player doesn't need to think about array indices, memory, or code. They see numbered suspect cards and get plain-language hints such as "go HIGHER" or "go LOWER" in the investigation log. The algorithm's internal state (low/high bounds) is displayed as a simple search range with a calculated pivot suggestion.

Algorithm Design: 
Please click this link to see the algorithm flowchart: https://drive.google.com/file/d/1wXtTwFW4-TFlibdr41BPA8fpAdz90L11/view?usp=sharing




# How to Run
#Clone the repository and install gradio using:

"pip install gradio"

or

"python -m pip install gradio"

Then run

"python app.py"


Alternatively, access the program through the following HuggingFace link: 
https://huggingface.co/spaces/L-J-J-S/CISC_121-Final_Project-Binary_Search

# Acknowledgement
Author: Luke Sipes

AI Disclaimer: Portions of the program code were written with assistance from Claude Opus 4.6 with prompts based on this README, in accordance with the Level 4 AI policy mandated by the final project guidlines. Project concept, structure, and logic are entirely the author's own. AI assisted entirely with creating custom Gradio theming using a custom CCS (extra theming bonus due to extra time and not a required component of the project).
