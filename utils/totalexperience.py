import re

def calculate_total_experience(experience_list):

    if not experience_list:
            return '0 months' 

    total_months = 0
    for item in experience_list:
        # Extrai anos e meses usando expressões regulares
        years = re.search(r'(\d+)\s*year', item)
        months = re.search(r'(\d+)\s*month', item)

        if years:
            total_months += int(years.group(1)) * 12
        if months:
            total_months += int(months.group(1))

    # Convertendo meses totais de volta para anos e meses
    years = total_months // 12
    months = total_months % 12
    return f"{years} years {months} months" if years > 0 else f"{months} months"
