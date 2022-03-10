year <- c(rep(2010, 5), rep(2011, 15), rep(2012, 5))
state <- rep(c('Louisiana', 'Louisiana', 'Texas', 'Texas', 'California'), 5)
disaster_id <- rep(1:5, each =5)
disaster_type <-c(rep('Hurricane', 10), rep('Fire', 5), rep('Earthquake', 10))
county_id <- rep(1:5, 5)
dc_id <- paste0(disaster_id, '-', county_id)
aid <- runif(25, 100, 1000)
population <- runif(25, 1000, 25000)
pcnt_white <- runif(25)
med_income <- runif(25, 25000, 100000)
dem_rep <- c(rep(0,15), rep(1, 10))

df <- data.frame(year, disaster_id, disaster_type, state, county_id, dc_id, aid, population, pcnt_white, 
                 med_income, dem_rep)

setwd('~/git-hub/capp30122/proj-lamonty-python/app/')
write.csv(df, 'dummy_data.csv', row.names = F)
