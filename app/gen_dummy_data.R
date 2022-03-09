disaster_id <- rep(1:5, each =5)
county_id <- rep(1:5, 5)
dc_id <- paste0(disaster_id, '-', county_id)
aid <- runif(25, 100, 1000)
population <- runif(25, 1000, 25000)
pcnt_white <- runif(25)
med_income <- runif(25, 25000, 100000)
dem_rep <- c(rep(0,15), rep(1, 10))

df <- data.frame(disaster_id, county_id, dc_id, aid, population, pcnt_white, 
                 med_income, dem_rep)

write.csv(df, 'dummy_data.csv', row.names = F)
