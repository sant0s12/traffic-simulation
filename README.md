# Complex Social Systems Fall 2020 – Research Plan

> * Group Name: The Traffic Team
> * Group participants names: Diego De los Santos, Daniel Nezamabadi, Natalie Suter, Róbert Veres, Victor Vitéz
> * Project Title: Effects of a general speed limit on two-lane highway traffic

## General Introduction
  
Highways are an important part of our infrastructure and are used by a lot of people every day for different reasons: To commute to work, transport goods and to go on holidays. Thus a general speed limit may have significant consequences for many people. In particular, we want to analyze the effects of a general speed limit on two-lane highway traffic.  
While many (European) countries have a general speed limit in place, Germany is one of few countries that doesn't have such a limit and where controversial debates surrounding a general speed limit happen regularly [5, 6]. Both sides seemingly use the same argument: A general speed limit decreases travel time by reducing traffic congestion, while without such a speed limit travel time is decreased because people can drive faster and thus reach their destination quicker. We want to see which of the argumentations hold. 

## The Model

We model a straight two-lane highway, where cars enter from the left and exit to the right. To determine the acceleration of each car at a given time step, we use the Intelligent Driver Model (IDM) [1, 3]. Since we are modeling a two-lane highway, we also need to model lane-changing behaviour. This is achieved by utilizing the lane-changing model MOBIL [2, 4].  
To analyse the results of our simulation, we define our independent variables as time, the speed limit, the deviation from the speed limit/average speed and the probability of disturbances. Our dependent variables are the location of cars and their associated velocity/acceleration at a given time step. The dependent variables can easily be measured by storing the corresponding parameters at every time step in a file.  


## Fundamental Questions

- How does a general speed limit affect highway traffic?
- Does a general speed limit increase or decrease the average velocity?
- How does the effect of a general speed limit on highway throughput change with varying velocities?
- Is there a difference in response to disturbances with and without a general speed limit? If yes, what are those differences?


## Expected Results

We expect that a general speed limit decreases traffic congestion and thus increases highway throughput in basically all situations by decreasing differences in speed of individual cars.


## References 

[1] Treiber, M., Hennecke A., Helbing D. (2000) ["Congested Traffic States in Empirical Observations and Microscopic Simulations"](https://www.researchgate.net/publication/1783975_Congested_Traffic_States_in_Empirical_Observations_and_Microscopic_Simulations)  
[2] Treiber, M. and Helbing, D. (2002) ["Realistische Mikrosimulation von Straßenverkehr miteinem einfachen Modell"](https://www.researchgate.net/publication/228748555_Realistische_Mikrosimulation_von_Strassenverkehr_mit_einem_einfachen_Modell)  
[3] "The Intelligent-Driver Model and its Variants" *traffic-simulation.de*. Available at https://traffic-simulation.de/info/info_IDM.html (Accessed 27.11.2020)  
[4] "The Lane-change Model MOBIL" *traffic-simulation.de*. Available at https://traffic-simulation.de/info/info_MOBIL.html (Accessed 27.11.2020)  
[5] "Und nun rasen sie wieder" *DIE ZEIT*. Available (German) at https://www.zeit.de/1975/35/und-nun-rasen-sie-wieder (Accessed 01.12.2020)
[6] "Andreas Scheuer gegen neue Tempolimit-Debatte" *ZEIT ONLINE* Available (German) at https://www.zeit.de/politik/deutschland/2019-12/verkehrsminister-tempolimit-debatte-andreas-scheuer-spd (Accessed 01.12.2020)


## Research Methods

Agent-Based Continous modelling.

## Other
