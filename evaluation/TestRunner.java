import algorithm.BFSPMiner;
import model.StatusObject;
import model.PatternObject;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class TestRunner {
    public static void main(String[] args) {
        System.out.println("\n======================================================================");
        System.out.println("                  JAVA BFSPMINER BASELINE (ORIGINAL)                  ");
        System.out.println("======================================================================");
        
        BFSPMiner miner = new BFSPMiner(5, false, 4, 500, 0.00995, 0.00999);
        
        String[] stream;
        String datasetName = "toy";
        double minSup = 0.1;
        
        if (args.length > 0 && args[0].equals("redd")) {
            datasetName = "redd";
            minSup = 0.001;
            int limit = 100000;
            if (args.length > 1) {
                try {
                    limit = Integer.parseInt(args[1]);
                    if (limit <= 0) limit = Integer.MAX_VALUE;
                } catch (NumberFormatException e) {
                    limit = Integer.MAX_VALUE;
                }
            }
            List<String> list = new ArrayList<>();
            try (BufferedReader br = new BufferedReader(new FileReader("data/redd_full_sequence.txt"))) {
                String line;
                int count = 0;
                while ((line = br.readLine()) != null && count < limit) {
                    if (!line.trim().isEmpty()) {
                        list.add(line.trim().replace(" ", "|"));
                        count++;
                    }
                }
            } catch (IOException e) {
                System.out.println("[-] Error loading redd_full_sequence.txt");
                e.printStackTrace();
            }
            stream = list.toArray(new String[0]);
        } else {
            stream = new String[]{"a", "b", "c", "a", "b", "d", "a", "b", "c", "e", "a", "b"};
        }
        
        System.out.println("[*] Processing " + datasetName.toUpperCase() + " Stream (Length: " + stream.length + ")");
        long startTime = System.currentTimeMillis();
        StatusObject status = null;
        for (int i = 0; i < stream.length; i++) {
            boolean output = (i == stream.length - 1);
            status = miner.createPatterns(stream[i], minSup, output);
        }
        long endTime = System.currentTimeMillis();
        
        System.out.println(String.format("[*] Time Taken: %.4fs", (endTime - startTime) / 1000.0));
        
        if (status != null && status.getPatterns() != null) {
            System.out.println("[*] Total Frequent Patterns Found: " + status.getPatterns().size());
            
            System.out.println("\n----------------------------------------------------------------------");
            System.out.println(String.format("%-5s | %-50s | %-10s", "No.", "Pattern", "Support"));
            System.out.println("----------------------------------------------------------------------");
            
            int count = 1;
            for(PatternObject p : status.getPatterns()) {
                if(count > 10) break;
                
                String[] parts = p.getPattern().split(";");
                StringBuilder sb = new StringBuilder("(");
                for(int i = 0; i < parts.length; i++) {
                    sb.append("'").append(parts[i].trim()).append("'");
                    if(i < parts.length - 1) sb.append(", ");
                }
                if(parts.length == 1) sb.append(",");
                sb.append(")");
                
                String patternStr = sb.toString();
                if(patternStr.length() > 48) patternStr = patternStr.substring(0, 45) + "...";
                
                System.out.println(String.format("%-5d | %-50s | %-10.3f", 
                    count, patternStr, p.getSupport()));
                count++;
            }
            System.out.println("----------------------------------------------------------------------");
            
            // Predictions
            System.out.println("\n[*] Next 3 Predictions:");
            algorithm.Predictor predictor = new algorithm.Predictor(1, 3, 5);
            String[][] preds = predictor.naivePred(status);
            System.out.print("    => [");
            if (preds != null && preds.length > 0 && preds[0] != null) {
                for(int i=0; i<preds[0].length; i++) {
                    System.out.print("'" + preds[0][i] + "'");
                    if(i < preds[0].length - 1) System.out.print(", ");
                }
            }
            System.out.println("]");
        } else {
            System.out.println("[-] No patterns returned or status is null.");
        }
        System.out.println("======================================================================\n");
    }
}
