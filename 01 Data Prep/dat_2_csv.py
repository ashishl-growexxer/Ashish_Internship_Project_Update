import pandas as pd

def convert_dat_to_csv(dat_file_path, csv_file_path):
    df = pd.read_csv(dat_file_path, delimiter='\t')

    df.to_csv(csv_file_path, index=False)

# Example usage
dat_file_path = 'Data/airfoil+self+noise/airfoil_self_noise.dat'
csv_file_path = 'Data/csv_data/airfoil_self_noise.csv'
convert_dat_to_csv(dat_file_path, csv_file_path)
