    import java.util.*;

public class FindS {

    public static void main(String[] args) {
        // Data Training: {ID, cuaca, kelembaban, angin, keputusan}
        String[][] dtTraining = {
            {"D1", "cerah", "normal",  "pelan",   "ya"},
            {"D2", "cerah", "normal",  "pelan",   "ya"},
            {"D3", "hujan", "tinggi",  "pelan",   "tidak"},
            {"D4", "cerah", "normal",  "kencang", "ya"},
                {"D5", "hujan", "tinggi",  "kencang", "tidak"},
                {"D6", "cerah", "normal",  "pelan",   "ya"}
        };

        int nData = dtTraining.length;
        int nAttribut = dtTraining[0].length;

        // Mengambil instance keputusan unik
        List<String> instance = new ArrayList<>();
        for (int i = 0; i < nData; i++) {
            String keputusan = dtTraining[i][nAttribut - 1];
            if (!instance.contains(keputusan)) {
                instance.add(keputusan);
            }
        }

        int nInstance = instance.size();

        // Proses Find-S
        String[][] hipotesis = new String[nInstance][nAttribut - 2];

        for (int n = 0; n < nInstance; n++) {
            // Seleksi data berdasarkan keputusan
            List<String[]> dataH = new ArrayList<>();
            for (int i = 0; i < nData; i++) {
                if (dtTraining[i][nAttribut - 1].equals(instance.get(n))) {
                    dataH.add(dtTraining[i]);
                }
            }

            // Hipotesa awal dari data pertama
            for (int j = 1; j <= nAttribut - 2; j++) {
                hipotesis[n][j - 1] = dataH.get(0)[j];
            }

            // Membandingkan seluruh data
            for (int i = 1; i < dataH.size(); i++) {
                for (int j = 1; j <= nAttribut - 2; j++) {
                    // Jika terdapat perbedaan nilai maka atribut menjadi *
                    if (!hipotesis[n][j - 1].equals("*")) {
                        if (!hipotesis[n][j - 1].equals(dataH.get(i)[j])) {
                            hipotesis[n][j - 1] = "*";
                        }
                    }
                }
            }
        }

        // Menampilkan hasil
        System.out.println("Hasil Hipotesa Find-S:");
        for (int n = 0; n < nInstance; n++) {
            System.out.print("H(");
            for (int j = 0; j < nAttribut - 2; j++) {
                System.out.print(hipotesis[n][j]);
                if (j < nAttribut - 3) {
                    System.out.print(", ");
                }
            }
            System.out.println(") = " + instance.get(n));
        }
    }
}
