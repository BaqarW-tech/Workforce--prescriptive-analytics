import pandas as pd
import numpy as np

def generate_saudi_data():
    sectors = ["Construction", "Information Technology", "Healthcare", "Financial Services", "Retail"]
    regions = ["Riyadh", "Jeddah", "Dammam", "Makkah", "Medina"]
    nitaqat_targets = {"Construction": 6, "Information Technology": 35, "Healthcare": 35, "Financial Services": 70, "Retail": 30}
    
    data = []
    for i in range(47):  # 47 companies
        company_id = f"CO-{1000+i}"
        sector = np.random.choice(sectors)
        target = nitaqat_targets[sector]
        # Generate random current saudization (some failing, some passing)
        current_pct = np.random.uniform(target - 15, target + 5) / 100
        headcount = np.random.randint(50, 500)
        
        for j in range(headcount):
            is_saudi = np.random.random() < current_pct
            data.append({
                "company_id": company_id,
                "company_name": f"Saudi {sector} Group {i}",
                "sector": sector,
                "region": np.random.choice(regions),
                "nationality": "Saudi" if is_saudi else "Expatriate",
                "monthly_salary_sar": np.random.randint(4000, 25000),
                "nitaqat_status": "Platinum" if current_pct > (target/100 + 0.1) else "Red"
            })
            
    df = pd.DataFrame(data)
    df.to_csv("saudi_workforce_data.csv", index=False)
    print("✅ Created saudi_workforce_data.csv with 5,000+ records.")

if __name__ == "__main__":
    generate_saudi_data()
