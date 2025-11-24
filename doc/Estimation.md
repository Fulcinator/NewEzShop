# Project Estimation

Date: 18 / 11 / 2025

Version: 2.0.0

# Contents 
- [Project Estimation] (#project-estimation)
- 

Estimate by size

Estimate by product decomposition

Estimate by activity decomposition + Gantt chart

Gantt chart

Summary

# Estimate by size

###

|                                                                                                         | Estimate |
| ------------------------------------------------------------------------------------------------------- | -------- |
| NC = Estimated number of classes to be developed                                                        |     28     |
| A = Estimated average size per class, in LOC                                                            |    420      |
| S = Estimated size of project, in LOC (= NC \* A)                                                       |    11760      |
| E = Estimated effort, in person hours (here use productivity 10 LOC per person hour)                    |      1176    |
| C = Estimated cost, in euro (here use 1 person hour cost = 30 euro)                                     |    35280      |
| Estimated calendar time, in calendar weeks (Assume team of 5 people, 8 hours per day, 5 days per week ) |    5.9 weeks      |

# Estimate by product decomposition

###

| component name       | Estimated effort (person hours) |
| -------------------- | ------------------------------- |
| Requirements documentation and acceptance criteria | 40
| Architecture setup, CI/CD, environment configuration | 60
| Database design and persistence layer | 90
| Authentication and role management | 50
| Point of Sale (POS) module | 180
| Returns handling | 60
| End-of-Day reconciliation | 40
| Inventory management | 110
| Supplier and Purchase Order module | 100
| Accounting and report generation | 90
| Register management | 25
| Employee management | 35
| System maintenance and diagnostics | 40
| Hardware integrations (scanner, printer, cash drawer) | 120
| Payment gateway integration | 60
| Non-functional improvements (performance, backups, concurrency) | 50
| Testing and QA | 150
| Documentation and user training | 40
| Project management and review | 45
| total | 1385


Estimated duration: (calendar time)

# Estimate by activity decomposition + Gantt chart

###
step 1: activities (WBS), step 2 Gantt chart
| Activity name | Estimated effort (person hours) |
| ------------- | ------------------------------- |
| Project inception and requirement validation | 24
| Architecture and environment setup | 56
| Domain modeling and database schema design | 72
| Authentication and role management | 48
| POS module implementation | 208
| Returns handling | 60
| End-of-Day reconciliation | 36
| Inventory management | 120
| Supplier and purchase order module | 108
| Report generation | 92
| Employee and register management | 54
| Maintenance and diagnostics | 44
| Hardware integration | 120
| Payment gateway integration | 60
| Performance and NFR improvements | 56
| System and integration testing | 158
| User acceptance testing and bug fixing | 80
| Documentation and training | 40
| Project management and review | 45
| total | 1481



###

## Gantt chart

| Activity name | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10| 11| 12| 13| 14| 15| 16| 17| 18| 19| 20| 21| 22| 23| 24| 25| 26| 27| 28| 29| 30| 31| 32 | 33| 34 | 35 | 36 | 37| 38 |
|---------------|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Project inception and requirement validation | 24 | 
| Architecture and environment setup || 24 | 24 | 16
| Domain modeling and database schema design || 16 | 16 | 24 | 16
| Authentication and role management ||||| 24 | 24
| POS module implementation |||||| 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16
| Returns handling ||||||| 8 | 8 | 8 | 8 | 8 | 8 | 8 | 4 
| End-of-Day reconciliation ||||||| 8| 8 | 8 | 8 |
| Inventory management ||||||| 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 |
| Supplier and purchase order module ||||||||||| 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 4
| Report generation |||||||||||||| 4 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 16 | 16 
| Employee and register management ||||||||||||||||||| 8 | 8 | 8 | 8 | 8 | 16 
| Maintenance and diagnostics ||||||||||||||||||| 8 | 8 | 8 | 8 | 12
| Hardware integration |||||||||||||||||||||||| 24 | 24 | 24 | 24 | 24
| Payment gateway integration ||||||||||||||||||||||||| 16 | 16 |16 | 12
| Performance and NFR improvements |||||||||||||||||||||||||||| 4 | 16 |16 |16 | 4
| System and integration testing ||||||||||||||||||||||||||||| 24| 24| 24| 36| 40|
| User acceptance testing and bug fixing |||||||||||||||||||||||||||||||||| 24| 24 | 24 | 8
| Documentation and training |||||||||||||||||||||||||||||||||| 16 | 16| 8
| Project management and review |||||||||||||||||||||||||||||||||||| 8 | 32 | 5


Insert here Gantt chart

Estimated duration: (calendar time)

# Summary

Report here the results of the three estimation approaches. The estimates may differ. Discuss here the possible reasons for the difference

|                                    | Estimated effort (ph) | Estimated duration (calendar time, relative)|
| ---------------------------------- | ---------------- | ------------------ |
| estimate by size                   |      1176            |             5.9 weeks       |
| estimate by product decomposition  |   1385               |          6.9 weeks          |
| estimate by activity decomposition (Gantt) |  1469        |         7.3 weeks           |

