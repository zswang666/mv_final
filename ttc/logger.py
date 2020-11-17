import csv

class TTCLogger(object):
    def __init__(self, output_path):
        self.output_path = output_path
   
        with open(self.output_path, 'w', newline='\n') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')          
            writer.writerow(['TTC', 'x0', 'y0', 'A', 'B', 'C'])

    def log(self, TTC, x0, y0, A, B, C):
        with open(self.output_path, 'a', newline='\n') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')          
            writer.writerow([TTC, x0, y0, A, B, C])