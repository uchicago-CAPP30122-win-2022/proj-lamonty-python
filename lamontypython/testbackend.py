from backend import datasets
import pandas as pd



test_cols = pd.read_csv('data/harvey_test_data.csv').columns
print(test_cols)

print("Test 1")
try:
    test_1 = datasets.get_data(["49"], [2017])
except:
    print('Error')
else:
    print(test_cols.difference(test_1.columns))
    
print("Test 2")
try: 
    test_2 = datasets.get_data(["48"], [2017])
except:
    print('Error')
else:
    print(test_cols.difference(test_2.columns))

print("Test 3")
try: 
    test_3 = datasets.get_data(["48","10","20","19"], [2017])
except:
    print('Error')
else:
    print(test_cols.difference(test_3.columns))

print("Test 4")
try: 
    test_4 = datasets.get_data(["48"], [2017,2018,2019])
except:
    print('Error')
else:
    print(test_cols.difference(test_4.columns))
