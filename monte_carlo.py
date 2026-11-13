import math
import matplotlib.pyplot as plt
import random

l=2

probability=[]
goals=[]
for x in range(10):
    probability.append((pow(math.e,-l)*pow(l,x))/math.factorial(x))
    goals.append(x)

goals_scored=[]
for i in range(100):
    rand=random.random()
    for j in range(10):
        if rand<sum(probability[0:j+1]):
            goals_scored.append(j)
            break

count_goals=[0,0,0,0,0,0,0,0,0,0]
for i in range(len(goals_scored)):
    count_goals[goals_scored[i]]+=1

#print(len(goals_scored))
#print(goals_scored)
#print(sum(goals_scored)/100)
fig,(ax1,ax2)=plt.subplots(1,2)
ax1.set_xlabel('Number of Goals')
ax1.set_ylabel('Probability')
ax1.plot(goals,probability)

ax2.set_xlabel('Number of Goals')
ax2.set_ylabel('Count of Goals')
ax2.plot(goals,count_goals)

plt.sca(ax1)
plt.xticks(range(10)) 
plt.sca(ax2)
plt.xticks(range(10))  

plt.show()