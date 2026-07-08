import zipfile
import pandas as pd
import io

with zipfile.ZipFile('PPR-ALL.zip', 'r') as z:
    file_list = z.namelist()
    print('Files in zip:', file_list)
    csv_filename = file_list[0]
    
    with z.open(csv_filename) as f:
        # Read the first few lines to see the structure
        for i in range(3):
            print(f.readline().decode('cp1252').strip())
            
    with z.open(csv_filename) as f:
        df = pd.read_csv(f, encoding='cp1252', nrows=5)
        print('Columns:', df.columns.tolist())
        print('Sample:')
        print(df.head())
