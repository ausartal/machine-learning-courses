# Data Training: [ID, cuaca, kelembaban, angin, keputusan]
dtTraining = [
    ["D1", "cerah", "normal",  "pelan",   "ya"],
    ["D2", "cerah", "normal",  "pelan",   "ya"],
    ["D3", "hujan", "tinggi",  "pelan",   "tidak"],
    ["D4", "cerah", "normal",  "kencang", "ya"],
    ["D5", "hujan", "tinggi",  "kencang", "tidak"],
    ["D6", "cerah", "normal",  "pelan",   "ya"]
]

nData = len(dtTraining)
nAttribut = len(dtTraining[0])

instance = []
for i in range(nData):
    keputusan = dtTraining[i][nAttribut - 1]
    if keputusan not in instance:
        instance.append(keputusan)

nInstance = len(instance)
hipotesis = [[None] * (nAttribut - 2) for _ in range(nInstance)]

for n in range(nInstance):
    # Seleksi data berdasarkan keputusan
    dataH = []
    for i in range(nData):
        if dtTraining[i][nAttribut - 1] == instance[n]:
            dataH.append(dtTraining[i])

    # Hipotesa awal dari data pertama
    for j in range(1, nAttribut - 1):
        hipotesis[n][j - 1] = dataH[0][j]

    # Membandingkan seluruh data
    for i in range(1, len(dataH)):
        for j in range(1, nAttribut - 1):
            # Jika terdapat perbedaan nilai maka atribut menjadi *
            if hipotesis[n][j - 1] != "*":
                if hipotesis[n][j - 1] != dataH[i][j]:
                    hipotesis[n][j - 1] = "*"

print("Hasil Hipotesa Find-S:")
for n in range(nInstance):
    h = ", ".join(hipotesis[n])
    print(f"H({h}) = {instance[n]}")
