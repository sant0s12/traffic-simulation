# Complex Social Systems Fall 2020 – Research Plan

> * Group Name: The Traffic Team
> * Group participants names: Diego De los Santos, Daniel Nezamabadi, Natalie Suter, Róbert Veres, Victor Vitéz
> * Project Title: Effects of a general speed limit on multi-lane highway throughput

## General Introduction

(Why is it important/interesting to solve this problem?)
(Put the problem into a historical context, from what does it originate? Are there already some proposed solutions?)  
Highways are an important part of our infrastructure and are used by a lot of people every day for different reasons: To commute to work, transport goods and to go on holidays. Thus a general speed limit may have significant consequences for many people. In particular, we want to analyze the effects of a general speed limit on the throughput of multi-lane highways.  
While many (European) countries have a general speed limit in place, Germany is one of few countries that doesn't have such a limit and where controversial debates surrounding a general speed limit happen regularly: First article in 1975 (Zeit) "Der alte Streit ist neu entflammt: Tempostopp auf Autobahnen - ja oder nein?", more recently in 2019 (Andreas Scheuer (German Verkehrsminister) gegen neue Tempolimit-Debatte). Both sides seemingly use the same argument: A general speed limit decreases travel time by reducing traffic congestion, while without such a speed limit travel time is decreased because people can drive faster and thus reach their destination quicker. We want to see which of the argumentations hold. 

## The Model
We model a straight multi-lane highway, where cars enter from the left and exit to the right. To determine the acceleration of each car at a given time step, we use a modified version of the Intelligent Driver Model (IDM) [1]. Since we are modeling a multi-lane highway, we also need to model lane-changing behaviour. This is achieved by utilizing the lane-changing model MOBIL [2].  
To analyse the results of our simulation, we define our independent variables as time, if a general speed limit is in place and the proportions of different drivers/cars, and our dependent variables as the location of cars and their associated velocity/acceleration at a given time step. The dependent variables can easily be measured by storing the corresponding parameters at every time step in a file.  

(Define dependent and independent variables you want to study. Say how you want to measure them.) (Why is your model a good abtraction of the problem you want to study?) (Are you capturing all the relevant aspects of the problem?)


## Fundamental Questions

- How does a general speed limit affect highway throughput?
- Does a general speed limit increase or decrease the average travel time?
- How does the effect of a general speed limit on highway throughput change with varying proportions and types of drivers?
- Is there a difference in response to "forced" speed changes (sudden stop of a car) with and without a general speed limit? If yes, what are those differences?

(At the end of the project you want to find the answer to these questions)
(Formulate a few, clear questions. Articulate them in sub-questions, from the more general to the more specific. )


## Expected Results

We expect that a general speed limit decreases traffic congestion and thus increase highway throughput in basically all situations by decreasing differences in speed of individual cars.

(What are the answers to the above questions that you expect to find before starting your research?)


## References 

([Format guideline](https://intranet.birmingham.ac.uk/as/libraryservices/library/referencing/icite/harvard/referencelist.aspx))

[1] Treiber, M., Hennecke A., Helbing D. (2000) ["Congested Traffic States in Empirical Observations and Microscopic Simulations"](https://www.researchgate.net/publication/1783975_Congested_Traffic_States_in_Empirical_Observations_and_Microscopic_Simulations)  
[2] Treiber, M. and Helbing, D. (2002) ["Realistische Mikrosimulation von Straßenverkehr miteinem einfachen Modell"](https://www.researchgate.net/publication/228748555_Realistische_Mikrosimulation_von_Strassenverkehr_mit_einem_einfachen_Modell)  
[3] "The Intelligent-Driver Model and its Variants" *traffic-simulation.de*. Available at https://traffic-simulation.de/info/info_IDM.html (Accessed 27.11.2020)  
[4] "The Lane-change Model MOBIL" *traffic-simulation.de*. Available at https://traffic-simulation.de/info/info_MOBIL.html (Accessed 27.11.2020)  


(Add the bibliographic references you intend to use)
(Explain possible extension to the above models)
(Code / Projects Reports of the previous year)


## Research Methods

Cellular Automata  

(Cellular Automata, Agent-Based Model, Continuous Modeling...) (If you are not sure here: 1. Consult your colleagues, 2. ask the teachers, 3. remember that you can change it afterwards)


## Other

(mention datasets you are going to use)
