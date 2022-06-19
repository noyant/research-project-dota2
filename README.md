# Research Project Dota 2

This is the code repository as part of the 2022 Q4 edition of the
[Research Project](https://github.com/TU-Delft-CSE/Research-Project)
of [TU Delft](https://https//github.com/TU-Delft-CSE).

### Abstract
Dota 2 is one of the most popular MOBA (Multiplayer Online Battle Arena) games being played today. A Dota 2 match is
played by two teams of 5 players. The main goal of the game is to destroy the opposing team’s Ancient tower, the team
that manages to do so, wins the game. An essential part of a match is the hero selection phase before it starts. There
are different ways to select heroes in different game modes, but the game mode that is used for this research is the
Captain’s mode where each team is assigned a captain and the captains take turn picking and banning heroes. The main
question that this research aims to answer is: What is the effect of the Pudge hero being picked in a team on the
outcome of a Dota 2 game? Causal inference, a discipline that is concerned with discovering causal relationships using
data analysis under certain assumptions about the data is used in this research to measure this effect. More
specifically, the g-formula is the causal inference method of choice for this research. The data that is used for this
research is gathered through the OpenDota API. After running the correctly formatted data through the g-formula
implementation, the effect of the Pudge hero being picked in a team on the game outcome was estimated as -0.2848%.
Meaning that, on average, there is a 0.2848% less chance of a team winning the game, if the Pudge hero is in that team.

The Research paper in full can be found at: link_to_paper.

The full dataset needed can be downloaded
through [this link](https://figshare.com/s/d0d019862fbe2bc5fbc6)
and added to the data folder of this repository.

