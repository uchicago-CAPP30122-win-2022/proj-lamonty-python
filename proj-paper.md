# Project: Nautral Disaster Aid and Demographics
## Team: (la)Monty Python 
## Team Members: Aditya, Ali, Wes and Zander
## IDs: , , , and 12273788

### Project Overview

### Software Structure
```mermaid
flowchart LR
db1[(FEMA)] --> py1([Python Connector])
db2[(ACS)] --> py2([Python Connector])


py1 --> ag([Aggregation/Analysis])
py2 --> ag([Aggregation/Analysis])
ss[[Static Datafiles]] --> ag([Aggregation/Analysis])

subgraph dash
  cs[Cross Section View]
  dd[Deep Dive View]
end

ag --> dash
```
The software consists of two abstract class connections to two separate APIs on the backend, a data integration and analysis middle layer, and a Plotly Dash frontend application. The frontend consists of two views:
- Cross Section: user can explore the relationship between demographics and FEMA aid provided at the county-disaster level, exploring how different county demographic factors are related with aid levels for a given disaster or disasters  
- Deep Dive: user can view specific statistical relationships between

### Code Responsibilities
#### Aditya
- Project management
- Dash frontend, deep dive view  

#### Ali
- FEMA API  
- ACS & FEMA blending  

#### Wesley
- ACS API  
- Statistical models  

#### Zander
- Dash frontend, cross-sectional view: 