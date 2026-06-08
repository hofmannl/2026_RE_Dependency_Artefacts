import krippendorff

data_path = r"<USER_HOME>\<DATASET_PATH>"
data: list[list[str]] = []
with open(data_path, "r") as f:
    lines = f.read().splitlines()
    for line in lines:
        elements = line.split(",")
        if data == []:
            for element in elements:
                data.append([element])
        else: 
            for i, element in enumerate(elements):
                data[i].append(element)
            
krippendorff_alpha = krippendorff.alpha(reliability_data=data, level_of_measurement="nominal")
print(f"Krippendorff's alpha: {krippendorff_alpha}")