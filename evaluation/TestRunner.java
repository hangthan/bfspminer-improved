import algorithm.BFSPMiner;
import model.StatusObject;
import model.PatternObject;

public class TestRunner {
    public static void main(String[] args) {
        System.out.println("\n======================================================================");
        System.out.println("                  JAVA BFSPMINER BASELINE (ORIGINAL)                  ");
        System.out.println("======================================================================");
        
        BFSPMiner miner = new BFSPMiner(5, false, 4, 500, 0.00995, 0.00999);
        String[] stream = {"a", "b", "c", "a", "b", "d", "a", "b", "c", "e", "a", "b"};
        
        System.out.println("[*] Processing Toy Stream (Length: " + stream.length + ")");
        long startTime = System.currentTimeMillis();
        StatusObject status = null;
        for (int i = 0; i < stream.length; i++) {
            boolean output = (i == stream.length - 1);
            status = miner.createPatterns(stream[i], 0.1, output);
        }
        long endTime = System.currentTimeMillis();
        
        System.out.println(String.format("[*] Time Taken: %.4fs", (endTime - startTime) / 1000.0));
        System.out.println("[*] Total Frequent Patterns Found: " + status.getPatterns().size());
        
        System.out.println("\n----------------------------------------------------------------------");
        System.out.println(String.format("%-5s | %-20s | %-10s | %-10s", "No.", "Pattern", "Support", "Count"));
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
            
            System.out.println(String.format("%-5d | %-20s | %-10.3f | %-10d", 
                count, sb.toString(), p.getSupport(), p.getCount()));
            count++;
        }
        System.out.println("----------------------------------------------------------------------");
        
        // Predictions
        System.out.println("\n[*] Next 3 Predictions (Context: 'a' -> 'b'):");
        algorithm.Predictor predictor = new algorithm.Predictor(1, 3, 5);
        String[][] preds = predictor.naivePred(status);
        System.out.print("    => [");
        for(int i=0; i<preds[0].length; i++) {
            System.out.print("'" + preds[0][i] + "'");
            if(i < preds[0].length - 1) System.out.print(", ");
        }
        System.out.println("]");
        System.out.println("======================================================================\n");
    }
}
