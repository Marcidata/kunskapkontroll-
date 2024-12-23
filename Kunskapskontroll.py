import pandas as pd  
import sqlite3

df = pd.read_csv("data_science_job.csv")  

print(df)  

print("Kolumner i filen:", df.columns)  

if 'start_date' not in df.columns:  
    print("Kolumnen 'start_date' saknas! En dummy-kolumn skapas.")  
    df['start_date'] = pd.NaT  # Skapa en dummy-kolumn för start_date  

df = df[df['salary'] > 50000]  

df['salary_in_thousands'] = df['salary'] / 1000  

df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')  
df['start_date'] = df['start_date'].fillna(pd.Timestamp.today())  

df['start_year'] = df['start_date'].dt.year  
df['start_month'] = df['start_date'].dt.month  

df = df[df['start_year'] >= 2000]  

df['salary_category'] = pd.cut(  
    df['salary'],  
    bins=[0, 60000, 100000, float('inf')],  
    labels=['Low', 'Medium', 'High']  
)  

df['job_title'] = df['job_title'].str.lower()  
df['job_title_length'] = df['job_title'].str.len()  

df = df.sort_values(by='salary', ascending=False)  

print(df.head())



import pandas as pd  
import logging  
import sqlite3  

logging.basicConfig(  
    filename='data_sciens_job.txt',  
    format='%(asctime)s - %(levelname)s - %(message)s',  
    level=logging.INFO  
)  

logger = logging.getLogger()  
logger.info('Startar hantering av data.')  

try:  
    df = pd.read_csv("data_science_job.csv")  
    logger.info('Tillgängliga kolumner: %s', df.columns.tolist())  
    
    if 'salary' not in df.columns:  
        logger.error("Kolumnen 'salary' saknas.")  
        raise KeyError("Kolumnen 'salary' saknas.")  
    
    if 'start_date' not in df.columns:  
        logger.warning("Kolumnen 'start_date' saknas! En dummy-kolumn skapas.")  
        df['start_date'] = pd.NaT  # Skapa en dummy-kolumn  

    df = df[df['salary'] > 50000]  

    df['salary_in_thousands'] = df['salary'] / 1000  
    
    df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')  
    df['start_date'] = df['start_date'].fillna(pd.Timestamp.today())  
    df['start_year'] = df['start_date'].dt.year  
    df['start_month'] = df['start_date'].dt.month  
    df = df[df['start_year'] >= 2000]  

    df['salary_category'] = pd.cut(  
        df['salary'],  
        bins=[0, 60000, 100000, float('inf')],  
        labels=['Low', 'Medium', 'High']  
    )  

    df['job_title'] = df['job_title'].str.lower()  
    df['job_title_length'] = df['job_title'].str.len()  
    
    df = df.sort_values(by='salary', ascending=False)  
    
    print(df.head())  
    
    con = sqlite3.connect("data_science_job.db")  
    
    df.to_sql("filtered_data", con, if_exists="replace", index=False)  
    
    logger.info('Data har bearbetats och sparats i databasen.')  

except Exception as e:  
    logger.error('Ett fel uppstod: %s', e)  
    print("Fel! Kontrollera loggen.")  

finally:  
    if 'con' in locals():  
        con.close()  
        logger.info("Databasanslutningen har stängts.")
        


